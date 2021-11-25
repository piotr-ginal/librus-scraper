import requests
import bs4


def get_announcements(cookies: dict) -> list:
    response = bs4.BeautifulSoup(
        requests.get(url="https://synergia.librus.pl/ogloszenia", cookies=cookies).text,
        "html.parser"
    )

    head = ["temat", "dodal", "data", "tresc"]

    announcements = [dict(zip(head, map(
        lambda x: x.text, annoucement.select("td:not(tfoot > tr > td)")
    ))) for annoucement in response.select("table.decorated.big.center.printable.margin-top")]

    return announcements
