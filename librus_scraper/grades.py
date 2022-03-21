import bs4
import requests
from dataclasses import dataclass
import re


@dataclass()
class Grade:
    grade: float
    subject: str
    category: str
    date: str
    teacher: str
    mean: bool
    to_max_points: bool
    additional: dict

    @property
    def points(self) -> list[int]:
        maximal = re.findall(r"\(\d+-(\d+)\)", self.category)

        return [self.grade, int(maximal[-1])]


@dataclass()
class Semester():
    subject: str
    grades: list[Grade]

    @property
    def points_sum(self) -> int:
        s = 0
        for grade in self.grades:
            if grade.mean:
                s += grade.grade

        return s

    @property
    def points_max(self) -> int:
        s = 0
        for grade in self.grades:
            if grade.mean and grade.to_max_points:
                s += grade.points[1]

        return s

    @property
    def percentage(self) -> float:
        return self.points_sum / self.points_max * 100


@dataclass()
class Subject:
    name: str
    semesters: list[Semester]

    @property
    def grades(self) -> list[Grade]:
        grades = []
        for semester in self.semesters:
            grades += semester.grades

        return grades

    @property
    def points_sum(self) -> int:
        return sum(x.points_sum for x in self.semesters)

    @property
    def points_max(self) -> int:
        return sum(x.points_max for x in self.semesters)

    @property
    def percentage(self) -> float:
        return self.points_sum / self.points_max * 100


def get_grades_detailed(cookies: dict) -> list[Subject]:

    response = bs4.BeautifulSoup(
        requests.get(
            "https://synergia.librus.pl/przegladaj_oceny/uczen",
            cookies=cookies
        ).text,
        "html.parser"
    )

    lines = response.select("table.decorated.stretch > tbody > tr[class^='line']:not(tr[id])")

    subjects = []

    for line in lines:
        cols = line.select("td:has(span.grade-box):not(td.center)")

        if not cols:
            continue

        semesters = []

        subject_name = line.select_one("td:not(td[class])").text

        for semester in cols:
            a_elements = semester.select("span > a")
            grades_obj = []

            for a in a_elements:
                grade_info = dict(re.findall(
                    "([^:>]+): +([^<]*)",
                    a.attrs["title"]
                ))

                content = ['Kategoria', 'Data', 'Nauczyciel']

                is_eq_to = [
                    ('Licz do wyniku', "TAK"),
                    ('Licz do puli', "TAK"),
                ]

                values = [
                    grade_info.get(x, "") for x in content
                ]

                values += [
                    grade_info.get(x[0], "NIE") == x[1] for x in is_eq_to
                ]

                grades_obj.append(
                    Grade(
                        float(a.text), subject_name, *values,
                        additional={
                            key: grade_info[key] for key in grade_info if key not in content + [x[0] for x in is_eq_to]
                        }
                    )
                )

            semesters.append(
                Semester(subject_name, grades_obj)
            )

        subjects.append(
            Subject(
                subject_name,
                semesters
            )
        )

    return subjects


def get_grades_head(thead: str) -> dict:

    thead = bs4.BeautifulSoup(
        thead,
        "html.parser"
    )

    rows = thead.select("tr")

    rows_dict = {i: [] for i in range(len(rows))}

    for i, row in enumerate(rows):

        cells = row.select("th, td")

        for cell in cells:

            colspan = int(cell.attrs.get("colspan", 1))
            rowspan = int(cell.attrs.get("rowspan", 1))

            for row_index in range(i, i + rowspan):

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
