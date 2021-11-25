from typing import Iterator
import bs4
import requests
import re


def get_timetable(cookies: dict, *, month: str = "", year: str = "", csrf_token: str = None) -> dict:
    response = requests.post(
        url="https://synergia.librus.pl/terminarz",
        data={
            "requestkey": csrf_token,
            "miesiac": month,
            "rok": year
        },
        cookies=cookies
    )

    response = bs4.BeautifulSoup(
        re.sub("<br ?/>", " ", response.text), "html.parser"
    )

    selected = list(map(
        lambda x: x.attrs["value"],
        response.select("option[selected]"))
    )

    days_data = {
        int(day.select_one("div[class]").text): [
            x.text.strip() for x in day.select("td")
        ] for day in response.select("div.kalendarz-dzien")
    }

    return {
        "date": selected,
        "days": days_data
    }


def get_attendence(cookies: dict) -> Iterator:
    response = bs4.BeautifulSoup(
        requests.get(
            url="https://synergia.librus.pl/przegladaj_nb/uczen",
            cookies=cookies
        ).text,
        "html.parser"
    )

    rows = response.select(
        "tr[class^='line']:not(:first-of-type):not(:last-child)"
    )

    for row in rows:
        entries = [
            {
                (val := x.split(": "))[0]: val[1] for x in
                re.split(" *<br/?> *", re.sub("</?b>", "", entry.attrs["title"]))
            } for entry in row.select("td.center a.ocena")
        ]

        yield {
            "date": row.select_one("td").text.split(" ")[0],
            "entries": entries
        }
