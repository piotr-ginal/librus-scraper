import bs4
import requests
import re


def get_notifications(cookies: dict) -> dict:
    response = bs4.BeautifulSoup(
        requests.get(
            "https://synergia.librus.pl/uczen/index",
            cookies=cookies
        ).text,
        "html.parser"
    )

    cols = response.select('div[id="graphic-menu"] li')

    return {
        col.select_one("a").text.strip():
            (button.text.strip() if (button := col.select_one("a.button.counter")) else "0")
        for col in cols
    }


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
