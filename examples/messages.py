from librus_scraper import get_messages, get_cookies

cookies = get_cookies("LOGIN", "PASSWORD")

messages = get_messages(cookies)

for message in messages["messages"]:
    print(message["temat"])