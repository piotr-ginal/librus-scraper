import bs4
import requests


def get_grades_head(thead: str) -> dict:

    thead = bs4.BeautifulSoup(
        thead,
        "html.parser"
    )

    rows = thead.select("tr")

    rows_dict = {i:[] for i in range(len(rows))}

    for i, row in enumerate(rows):

        cells = row.select("th, td")

        for cell in cells:

            colspan = int(cell.attrs.get("colspan", 1))
            rowspan = int(cell.attrs.get("rowspan", 1))

            for row_index in range(i, i+rowspan):

                cell_text = cell.attrs.get(
                    "title", cell.text).strip()

                rows_dict[row_index] += [
                    cell_text.replace("<br>", "") for _ in range(colspan)
                ]

    return rows_dict


def get_grades(cookies: dict) -> list:

    response = bs4.BeautifulSoup(
        requests.get(
            "https://synergia.librus.pl/przegladaj_oceny/uczen",
            cookies=cookies
        ).text,
        "html.parser"
    )

    thead = list(get_grades_head(
        str(response.select_one("table.decorated.stretch > thead"))
    ).values())[-1]

    lines = response.select(
        "table.decorated.stretch > tbody > tr[class^='line']:not(tr[id])"
    )

    subjects = []

    for line in lines:

        cells = [
            c.text.replace("\n", " ").strip()
            for c in line.select("td")
        ]

        cells = list(zip(thead, cells))
        
        subjects.append(
            list(filter(all, cells))
        )

    return subjects
