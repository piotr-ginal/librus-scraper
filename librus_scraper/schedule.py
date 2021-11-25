import bs4
import requests


def get_schedule(cookies: dict, csrf_token: str = None, week: str = None) -> dict:

    response = requests.post(
        url="https://synergia.librus.pl/przegladaj_plan_lekcji",
        cookies=cookies,
        data={
            "requestkey": csrf_token,
            "tydzien": week,
            "pokaz_zajecia_zsk": "on",
            "pokaz_zajecia_ni": "on"
        }
    )

    response = bs4.BeautifulSoup(
        response.text, "html.parser"
    )

    hour_to_lesson = {
        line.select_one("th").text[:5]: line.select_one("td").text
        for line in response.select("tr[class=line1]")
    }

    schedule = {}

    for lesson in response.select("td[data-date][class=line1]"):

        if (lesson_name := lesson.select_one("b")) is None:
            continue

        date = (attrs := lesson.attrs)["data-date"]
        lesson_time = (attrs["data-time_from"], attrs["data-time_to"])

        if date not in schedule:
            schedule[date] = {}

        tags = bs4.BeautifulSoup(str(lesson), "html.parser").select(
            "td[data-date][class=line1] > :not(:last-child)")

        schedule[date][hour_to_lesson[lesson_time[0]]] = {
            "subject": lesson_name.text.strip(),
            "time": lesson_time,
            "tags": [x.text for x in tags]
        }

    lesson_hours = {}

    for h in response.select("table.decorated.plan-lekcji tr.line1"):

        data = h.select("td:first-child, th")
        lesson_hours[data[0].text] = data[1].text.replace("\xa0", "")

    return {
        "days": schedule,
        "hours": lesson_hours
    }


def get_schedule_weeks(cookies: dict) -> list:
    return list(map(
        lambda x: x.attrs["value"],
        bs4.BeautifulSoup(
            requests.get(
                url="https://synergia.librus.pl/przegladaj_plan_lekcji",
                cookies=cookies
            ).text,
            "html.parser"
        ).select("select[id='tydzien'] > option")
    ))
