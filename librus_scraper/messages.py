import re
import bs4
import requests
from dataclasses import dataclass


def process_message_tr(row: bs4.element.Tag) -> dict:
    row_cels = row.select("td")

    data = {
        "nadawca": row_cels[2].text,
        "temat": row_cels[3].select_one("a[href]").text,
        "data": row_cels[4].text,
        "href": (href := row.select_one(
            "a[href^='/wiadomosci']").attrs["href"]),
        "id": re.findall("/wiadomosci/././([0-9]+)/.*", href)[0],
        "new": "style" in row_cels[2].attrs,
        "files": row_cels[1].select_one("img") is not None,
        "tags": None
    }

    tags = row_cels[3].select("span")

    if tags is None:
        return data

    data["tags"] = {tag.text for tag in tags}

    return data


def get_messages(
    cookies: dict, *,
    archive: bool = False,
    sent: bool = False,
    deleted: bool = False,
    csrf_token: str = None,
    person: str = "-",
    page: str = "0"
) -> dict:

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
            messages.append(process_message_tr(row))

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
        "files": list(zip(filenames, files))
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


@dataclass()
class Recipient():
    name: str
    recipient_id: str
    recipient_type: str


@dataclass()
class RecipientGroup:

    recipient_type: str
    is_virtual_classes: str = "false"
    group: str = "0"
    class_id: str = None

    def get_recipients(self, cookies: dict) -> list[Recipient]:

        response = requests.post(
            "https://synergia.librus.pl/getRecipients",
            cookies=cookies,
            data={
                "typAdresata": self.recipient_type,
                "czyWirtualneKlasy": self.is_virtual_classes == "true",
                "idGrupy": self.group,
                "klasa_rada_rodzicow": self.class_id,
                "klasa_opiekunowie": self.class_id,
                "klasa_rodzice": self.class_id,
            }
        )

        response = bs4.BeautifulSoup(
            response.text,
            "html.parser"
        )

        labels = response.select("label")

        return [Recipient(label.text.strip(), label.attrs['for'].split("_")[1], self.recipient_type) for label in labels]


def get_recipient_groups(cookies: dict) -> list[RecipientGroup]:

    response = bs4.BeautifulSoup(
        requests.get("https://synergia.librus.pl/wiadomosci/2/5", cookies=cookies).text,
        "html.parser"
    )

    inputs = response.select(
        "input[name='adresat']"
    )

    recipients = []

    for inp in inputs:

        onclick = inp.attrs["onclick"][:-2].split("(")[-1]

        onclick = [x.strip('"') for x in re.split(" ?, ?", onclick)]

        recipients.append(RecipientGroup(*onclick))

    return recipients


def send_message(
    cookies: dict,
    csrf_token: str,
    recipinet: Recipient,
    title: str,
    content: str
) -> None:

    data = {
        "requestkey": csrf_token,
        "adresat": recipinet.recipient_type,
        "DoKogo[]": recipinet.recipient_id,
        "DoKogo_hid[]": recipinet.recipient_id,
        "temat": title,
        "tresc": content,
        "wyslij": "Wyślij",
    }

    requests.post(
        "https://synergia.librus.pl/wiadomosci/5",
        cookies=cookies,
        headers={
            "Referer": "https://synergia.librus.pl/wiadomosci/2/5"
        },
        data=data
    )


def manage_tags_on_messages(
    cookies: dict,
    messages: list[str],
    tag_id: str,
    *,
    archive: bool = False,
    delete: bool = False
) -> int:

    if not messages:
        return 0

    opcja = f"{'usunEtykiete_' if delete else 'oznaczEtykieta_'}{tag_id}",

    data = {"opcja_zaznaczone_g": opcja}

    for index, message_id in enumerate(messages):
        data[f"wiadomosci[{index}]"] = message_id

    url = "https://synergia.librus.pl/" + (
        "wiadomosci_archiwum" if archive else "wiadomosci_aktualne")

    response = requests.post(
        url, cookies=cookies, data=data, headers={"Referer": url})

    response = bs4.BeautifulSoup(response.text, "html.parser")

    text = response.select_one("div.container.green > div.container-background > p").text

    return int(text.split(": ")[1])
