import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

URL = "https://deathfests.com/lineup/"

project_root = Path(__file__).resolve().parents[1] 
output_path = project_root / "data" / "bands_raw.csv"

def scrape_lineup():
    resp = requests.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    current_day = None
    current_stage = None

    festival_line_up = []


    for el in soup.select("h2, h3, span.band-name"):
        if el.name == "h2":
            current_day = " ".join(el.get_text().split())

        elif el.name == "h3":
            current_stage = " ".join(el.get_text().split()) 
        

        elif el.name == "span" and "band-name" in el.get("class", []):
            band_name = " ".join(el.get_text().split())

            # next sibling must exist and NOT have 'band-name' class
            note_span = el.find_next_sibling("span")
            if note_span and "band-name" not in note_span.get("class", []):
                note_text = " ".join(note_span.get_text().split())
                band_name = f"{band_name} {note_text}"

            festival_line_up.append({
                "band": band_name,
                "day": current_day,
                "stage": current_stage,
            })
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["band", "day", "stage"],
        )
        writer.writeheader()
        writer.writerows(festival_line_up)

if __name__ == "__main__":
    scrape_lineup()
