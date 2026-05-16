import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

URL = "https://deathfests.com/set-times/"

project_root = Path(__file__).resolve().parents[1]
output_path = project_root / "data" / "set_times_raw.csv"

DAY_MAP = {
    "Wednesday": "Wednesday May 20, 2026",
    "Thursday":  "Thursday May 21, 2026",
    "Friday":    "Friday May 22, 2026",
    "Saturday":  "Saturday May 23, 2026",
    "Sunday":    "Sunday May 24, 2026",
}

def scrape():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []

    # Each day is wrapped in a wpb_text_column div containing an h2 and a table
    for day_block in soup.select("div.wpb_text_column"):
        h2 = day_block.find("h2")
        if not h2:
            continue

        day_text = h2.get_text(separator=" ", strip=True)
        day_key = next((k for k in DAY_MAP if k in day_text), None)
        if not day_key:
            continue
        day_full = DAY_MAP[day_key]

        table = day_block.find("table")
        if not table:
            continue

        rows = table.find_all("tr")
        if not rows:
            continue

        # First row: stage names (one <td> per column, first td is the time column)
        header_cells = rows[0].find_all("td")
        stages = [td.get_text(strip=True) for td in header_cells]
        # stages[0] is "" or "Time", stages[1..] are stage names

        # Walk remaining rows looking for band cells
        for row in rows[1:]:
            cells = row.find_all("td")
            for col_idx, cell in enumerate(cells):
                if col_idx >= len(stages):
                    continue
                stage = stages[col_idx]
                if not stage or stage in ("", "Doors", "Time"):
                    continue

                text = cell.get_text(separator="\n", strip=True)
                if not text:
                    continue

                # Skip pure time cells like "14:00", "15:35"
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                # A band cell has name + time range (e.g. "Organ Dealer\n6:45-7:20")
                # A time cell has just a clock value like "18:45"
                # A doors cell has "Doors 6:00PM"
                if len(lines) < 2:
                    continue
                if lines[0].replace(":", "").replace(".", "").isdigit():
                    continue

                band_name = lines[0]
                time_str = lines[1] if len(lines) > 1 else ""

                # Signing sessions are marked with "| Signing"
                is_signing = "Signing" in band_name or "Signing" in time_str
                if is_signing:
                    band_name = band_name.replace("| Signing", "").replace("|Signing", "").strip()
                    time_str = time_str.replace("Signing", "").strip()

                results.append({
                    "band":    band_name,
                    "day":     day_full,
                    "stage":   stage,
                    "time":    time_str,
                    "signing": "yes" if is_signing else "",
                })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["band", "day", "stage", "time", "signing"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Scraped {len(results)} entries → {output_path}\n")
    for r in results:
        sig = " [SIGNING]" if r["signing"] else ""
        print(f"  {r['day'][:3]}  {r['stage']:<20} {r['time']:<12} {r['band']}{sig}")

if __name__ == "__main__":
    scrape()
