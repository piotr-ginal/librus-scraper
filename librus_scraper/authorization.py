import re
from json.decoder import JSONDecodeError
import bs4
import requests


class AuthorizationException(Exception):
    pass


def parse_cookie(cookie_string: str) -> dict:
    return {
        (sp := x.split("="))[0]: sp[1] for x in cookie_string.split("; ")
    }


def get_cookies(login: str, password: str) -> dict:

    response = requests.get(
        "https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata"
    )

    cookies = {}

    for cookie_string in response.request.headers["Cookie"].split("; "):

        data = cookie_string.split("=")

        cookies[data[0]] = data[1]

    response = requests.post(
        "https://api.librus.pl/OAuth/Authorization?client_id=46",
        data={
            "action": "login",
            "login": login,
            "pass": password
        },
        cookies=cookies
    )

    try:
        response_json = response.json()
    except JSONDecodeError:
        raise AuthorizationException("something went wrong")

    if response_json["status"] != "ok":
        raise AuthorizationException(response.json()["errors"])

    response = requests.get(
        "https://api.librus.pl/OAuth/Authorization/PerformLogin?client_id=46",
        cookies=cookies,
        headers={
            "Referer": "https://portal.librus.pl/rodzina"
        }
    )

    return dict(response.cookies)


def get_csrf_token(cookies: dict, parent: bool = False) -> str:
    response = requests.get(
        f"https://synergia.librus.pl/{'rodzic' if parent else 'uczen'}/index",
        cookies=cookies
    )

    response = re.search(
        'var csrfTokenValue = "(.*)";',
        bs4.BeautifulSoup(
            response.text, "html.parser"
        ).select_one(
            "script[type='text/javascript']:not(script[src])"
        ).text
    )

    if response is not None:
        return response.groups()[0]

    raise AuthorizationException("CSRF token not found")


def get_login_history(cookies: dict, parent: bool = False) -> dict:
    response = bs4.BeautifulSoup(
        requests.get(
            f"https://synergia.librus.pl/{'rodzic' if parent else 'uczen'}/index",
            cookies=cookies
        ).text,
        "html.parser"
    )

    title_strig = re.sub(
        "<.{1,4}>",
        " ",
        response.select_one("span.tooltip").attrs["title"]
    )

    regex_pattern =\
        r'(\d{4}-\d{1,2}-\d{1,2}) (\d{1,2}:\d{1,2}:\d{1,2}), IP: ([\d.]{7,15})'

    ip_info = list(map(
        lambda x: [
            {"date": entry[0], "time": entry[1], "ip": entry[2]} for entry in re.findall(regex_pattern, x)
        ],

        list(filter(
            lambda x: len(set(x)) > 1,
            re.split("ostatnie.{0,4}udane logowania:", title_strig)
        ))
    ))

    return {
        "successful": ip_info[0],
        "failed": ip_info[1]
    }
