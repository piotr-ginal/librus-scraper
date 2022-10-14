# Librus scraper
## Funkcje
- wiadomości
- ogłoszenia
- terminarz
- plan lekcji
- frekwencja
- oceny
    

## Przykłady użycia
### Pobieranie wiadomości:
Powiedzmy, że chcemy pobrać 50 najnowszych wiadomości:
```python
from librus_scraper import get_messages, get_cookies

cookies = get_cookies(
    "LOGIN", "PASSWORD"  # login i hasło do librusa synergii
)

messages = get_messages(cookies)

print(messages)
```
Otrzymujemy:
```python
{
    "pagination": [
        1,  # obecna strona
        2  # ostatnia strona
    ],
    "messages": [  # lista zawierająca pobrane wiadomości
        {
            "nadawca": "James Smith",  # imie i nazwisko
            "temat": "xyz",  # temat wiadomości
            "data": "2005-04-02 21:37:06",  # data wysłania wiadomości
            "href": "/wiadomosci/1/5/1234567/f0",  # link do wiadomości
            "id": "1234567",  # id wiadomości
            "new": True,  # czy ta wiadomość jest nowa?
            "files": True  # czy ta wiadomość zawiera jakieś pliki?
            "tags": [  # lista tagów (None jeżeli wiadomości nie ma)
                "tag1",
                "tag2"
            ]
        }
    ]
}
```
### Odczytywanie wiadomości:
Powiedzmy, że chcemy pobrać zawartość wiadomości:
``` python
from librus_scraper import read_message, get_cookies

cookies = get_cookies(
    "LOGIN", "PASSWORD"  # login i hasło do librusa synergii
)

message = read_message(cookies, "/wiadomosci/1/5/1234567/f0")

print(message)
```
Otrzymujemy:
```python
{
    "nadawca": "James Smith",  # imie i nazwisko nadawcy
    "temat": "xyz",  # temat wiadomości
    "data": "2005-04-02 21:37:06",  # data wysłania wiadomości
    "data_odczytania": "2005-04-02 21:37:06",  # data odczytania wiadomości
    "tresc": "xyz",  # treść wiadomości
    "files": [
        [
            "file.docx",  # nazwa pliku
            "/wiadomosci/pobierz_zalacznik/1234567/7654321"  # link do pliku
        ]
    ]
}
```