from librus_scraper import get_announcements, get_cookies

cookies = get_cookies("LOGIN", "PASSWORD")

announcements = get_announcements(cookies)

for ann in announcements:
    print(ann["temat"])
