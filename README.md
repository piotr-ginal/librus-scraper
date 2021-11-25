# Librus scraper
## Przykłady użycia:
### Pobieranie wiadomości:
Powiedzmy że chcemy pobrać 50 najnowszych wiadomości:
```python
from librus_scraper import get_messages, get_cookies

cookies = get_cookies("LOGIN", "PASSWORD")

messages = get_messages(cookies)

print(messages)
```
Otrzymujemy:
```python
{
    "pagination": [
        1,  # current page
        2  # last page
    ],
    "messages": [
        {
            "nadawca": "James Smith",
            "temat": "xyz",
            "data": "2005-04-02 21:37:06",  # date the message was sent
            "href": "/wiadomosci/1/5/1234567/f0",  # link do wiadomości
            "id": "1234567",  # id wiadomości
            "new": True,  # czy ta wiadomość jest nowa?
            "files": True  # czy ta wiadomość zawiera jakieś pliki?
        }
    ]
}
```
### Odczytywanie wiadomości:
Powiedzmy że chcemy pobrać zawartość wiadomości:
``` python
from librus_scraper import read_message, get_cookies

cookies = get_cookies("LOGIN", "PASSWORD")

message = read_message(cookies, "/wiadomosci/1/5/1234567/f0")

print(message)
```
Otrzymujemy:
```python
{
    "nadawca": "James Smith",
    "temat": "xyz",
    "data": "2005-04-02 21:37:06",
    "data_odczytania": "2005-04-02 21:37:06",
    "tresc": "xyz",
    "files": [
        [
            "file.docx",  # nazwa pliku
            "/wiadomosci/pobierz_zalacznik/1234567/7654321"  # link do pliku
        ]
    ]
}
```