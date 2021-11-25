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
        url='https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata'
    )

    data = {
        "action": "login",
        "login": login,
        "pass": password
    }

    response = requests.post(
        url='https://api.librus.pl/OAuth/Authorization?client_id=46',
        data=data,
        cookies=parse_cookie(response.request.headers["cookie"])
    )

    try:
        response_json = response.json()
    except JSONDecodeError:
        raise AuthorizationException("something went wrong")

    if response_json["status"] != "ok":
        raise AuthorizationException(response.json()["errors"])

    cookies_dict = parse_cookie(response.request.headers["cookie"])
    cookies_dict["DeviceCookie"] = dict(response.cookies)['DeviceCookie']

    response = requests.get(
        url="https://api.librus.pl/OAuth/Authorization/Grant?client_id=46",
        cookies=cookies_dict
    )

    return dict(response.cookies)


def get_csrf_token(cookies: dict) -> str:
    response = requests.get(
        "https://synergia.librus.pl/uczen/index",
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


def get_login_history(cookies: dict) -> dict:
    response = bs4.BeautifulSoup(
        requests.get(
            "https://synergia.librus.pl/uczen/index",
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
                    {"date": entry[0], "time": entry[1], "ip": entry[2]}
                    for entry in re.findall(regex_pattern, x)
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
