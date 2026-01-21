import requests
from bs4 import BeautifulSoup

URL = "https://deathfests.com/lineup/"


def scrape_lineup():
    resp = requests.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    current_day = None
    current_stage = None

    for el in soup.select("h2, h3, span.band-name"):
        if el.name == "h2":
            current_day = el.get_text(strip=True)

        elif el.name == "h3":
            current_stage = el.get_text(strip=True) 

        elif el.name == "span": 
            band = el.get_text(strip=False)

            print(f"{current_day} | {current_stage} | {band}")

if __name__ == "__main__":
    scrape_lineup()
