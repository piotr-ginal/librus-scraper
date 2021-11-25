from librus_scraper import get_attendence, get_cookies

cookies = get_cookies("LOGIN", "PASSWORD")

attendence = get_attendence(cookies)

for day in attendence:
    print(day["date"])
    for entry in day["entries"]:
        print("\t", entry["Rodzaj"])