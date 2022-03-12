import bs4
import requests
import re


def get_notifications(cookies: dict) -> dict:

    response = requests.get(
        "https://synergia.librus.pl/uczen/index",
        cookies=cookies
    )

    response = bs4.BeautifulSoup(
        response.text,
        "html.parser"
    )

    titles = response.select(
            "div[id='graphic-menu'] li:not(:first-child) a[id^='icon'][title]"
        )

    buttons = response.select("a.button.counter")

    keys = [
        title.text.strip(" \n") for title in titles
    ]

    values = [
        x.text.strip(" \n") for x in buttons
    ]

    return dict(zip(keys, values))


def get_user_information(cookies: dict) -> dict:
    response = bs4.BeautifulSoup(
        requests.get(
            "https://synergia.librus.pl/informacja",
            cookies=cookies
        ).text,
        "html.parser"
    )

    rows = response.select(
        "table.decorated.big.center.form > tbody > tr[class^='line']:not(:last-of-type)"
    )

    return {
        row.select_one("th.big").text.strip():
            re.sub(
                r" ?\n +", ", ",
                row.select_one("td").text.strip()
            )
        for row in rows[:-1]
    }
