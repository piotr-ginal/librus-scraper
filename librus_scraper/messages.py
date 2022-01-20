import re
import bs4
import requests


def get_messages(
        cookies: dict, *, archive: bool = False, sent: bool=False, deleted: bool=False, csrf_token: str = None, person: str = "-", page: str = "0") -> dict:

    data = {
        "requestkey": csrf_token,
        "filtrUzytkownikow": "0",
        "idPojemnika": "105",
        "opcja_zaznaczone_g": "0",
        "filtr_uzytkownikow": person,
        "sortujTabele[tabeleKolumna]": "3",
        "sortujTabele[tabeleKierunek]": "1",
        "sortujTabele[tabelePojemnik]": "105",
        "sortowanie[105][0]": "",
        "sortowanie[105][1]": "",
        "sortowanie[105][2]": "",
        "opcja_zaznaczone_d": "0",
        "numer_strony105": page,
        "porcjowanie_pojemnik105": "105",
        "poprzednia": "5"
    }

    url = "https://synergia.librus.pl/wiadomosci_archiwum" if archive else "https://synergia.librus.pl/wiadomosci_aktualne"

    url = "https://synergia.librus.pl/wiadomosci/6" if sent else url

    url = "https://synergia.librus.pl/wiadomosci/7" if deleted else url

    response_object = requests.post(
        url,
        cookies=cookies,
        headers={
            "Referer": "https://synergia.librus.pl/wiadomosci_archiwum" if archive else "https://synergia.librus.pl/wiadomosci_aktualne"
        },
        data=data
    )

    response = bs4.BeautifulSoup(response_object.text, "html.parser")

    rows = response.select('table[class="decorated stretch"] > tbody > tr')

    messages = []

    if not (len(rows) == 1 and rows[0].select_one("td").text == "Brak wiadomości"):

        for row in rows:
            row_cels = row.select("td")

            messages.append({
                "nadawca": row_cels[2].text,
                "temat": row_cels[3].text,
                "data": row_cels[4].text,
                "href": (href := row.select_one(
                    "a[href^='/wiadomosci']").attrs["href"]),
                "id": re.findall("/wiadomosci/././([0-9]+)/.*", href)[0],
                "new": "style" in row_cels[2].attrs,
                "files":row_cels[1].select_one("img") is not None
            })

    pagination = response.select_one("div.pagination > span")

    if pagination is not None:
        pagination = re.match(
            r"Strona (.*) z (.*)",
            pagination.text.replace('\xa0', " ")
        ).groups()

    else:
        pagination = (1, 1)

    return {
        "pagination": tuple(map(int, pagination)),
        "messages": messages,
    }


def read_message(cookies: dict, href: str) -> dict:

    response_object = requests.get(
        url="https://synergia.librus.pl" + href,
        cookies=cookies,
        headers={
            "Referer": "https://synergia.librus.pl/wiadomosci_archiwum"
        }
    )

    response = bs4.BeautifulSoup(
        response_object.text,
        "html.parser"
    )

    information = list(map(
        lambda x: x.text,
        response.select("td.left:not(:first-child)")
    ))

    files = "".join([
        x.attrs["onclick"].replace("\\", "")
        for x in response.select(
            "img[src='/assets/img/homework_files_icons/download.png']"
        )
    ])

    files = re.findall("/wiadomosci/pobierz_zalacznik/[0-9]+/[0-9]+", files)

    filenames = [
        x.find_parent("td").text.strip()
        for x in response.select('img[src^="/assets/img/filetype_icons"]')
    ]

    information = ["Użytkownik", *information]

    return {    
        "nadawca": information[-4],
        "temat": information[-3],
        "data": information[-2],
        "data_odczytania": information[-1],
        "tresc": response.select_one("div.container-message-content").text,
        "files":list(zip(filenames, files))
    }


def get_senders_id(cookies: dict, *, archive: bool = False) -> list:

    response = requests.post(
        "https://synergia.librus.pl/wiadomosci_archiwum"
        if archive else "https://synergia.librus.pl/wiadomosci_aktualne",
        cookies=cookies,
        headers={
            "Referer": "https://synergia.librus.pl/wiadomosci"
            if archive else "https://synergia.librus.pl/wiadomosci_aktualne"
        }
    )

    response = bs4.BeautifulSoup(response.text, "html.parser")

    return list(map(
        lambda x: (x.attrs["value"], x.text),
        response.select("select[name='filtr_uzytkownikow'] > option")
    ))


def delete_messages(cookies: dict, messages: list, csrf_token: str, archive: bool = False) -> str:

    data = {
        "wiadomosciLista[]": messages,
        "folder": "5",
        "czyArchiwum": "0" if not archive else "1"
    }

    response = requests.post(
        "https://synergia.librus.pl/usun_wiadomosc",
        cookies=cookies,
        data=data,
        headers={
            "requestkey": csrf_token
        }
    )

    return response.text


def recover_messages(cookies: dict, messages: list, csrf_token: str, archive: bool = False) -> str:

    data = {
        "wiadomosciLista[]": messages,
        "folder": "7",
        "czyArchiwum": "0" if not archive else "1"
    }

    response = requests.post(
        "https://synergia.librus.pl/przywroc_wiadomosc",
        cookies=cookies,
        data=data,
        headers={
            "requestkey": csrf_token
        }
    )

    return response.text
