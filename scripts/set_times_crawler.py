import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

URL = "https://deathfests.com/set-times/"

project_root = Path(__file__).resolve().parents[1]
output_path = project_root / "data" / "set_times_raw.csv"

DAYS = ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_schedule_table(table):
    """
    Parse a schedule table where row 0 = stage headers, row 1 = doors info,
    and subsequent rows are 5-minute time slots with bands in rowspan cells.

    Returns list of dicts: {stage, band, time}
    """
    rows = table.find_all("tr")
    if len(rows) < 3:
        return []

    # Row 0: stage names (col 0 is blank time column, cols 1+ are stages)
    header_cells = rows[0].find_all("td")
    stages = [cell.get_text(strip=True) for cell in header_cells[1:]]
    if not stages:
        return []

    # Track rowspan occupancy: col_index -> rows_remaining
    active = {}
    results = []

    for row in rows[2:]:  # skip header row and doors row
        cells = row.find_all("td")
        if not cells:
            continue

        # Decrement active rowspans, drop expired ones
        active = {col: rem - 1 for col, rem in active.items() if rem > 1}

        # Walk stage columns, consuming cells only for non-occupied slots
        cell_idx = 1  # cells[0] is the time column
        for stage_col, stage_name in enumerate(stages):
            if stage_col in active:
                continue  # this column is still occupied by a prior rowspan

            if cell_idx >= len(cells):
                break

            cell = cells[cell_idx]
            cell_idx += 1

            rowspan = int(cell.get("rowspan", 1))
            # Band cells contain "Band Name<br/>HH:MM-HH:MM"
            text = cell.get_text(separator="\n", strip=True)
            if text:
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                band_name = lines[0]
                time_range = lines[1] if len(lines) > 1 else ""
                results.append({"stage": stage_name, "band": band_name, "time": time_range})

            if rowspan > 1:
                active[stage_col] = rowspan

    return results


def scrape_set_times():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    all_entries = []

    for h2 in soup.find_all("h2"):
        day_text = " ".join(h2.get_text().split())
        if not any(d in day_text for d in DAYS):
            continue

        # h2 is in: inner wpb_wrapper > wpb_text_column > outer wpb_wrapper
        # We need the outer wpb_wrapper which also contains the table
        inner_wrapper = h2.find_parent("div", class_="wpb_wrapper")
        if not inner_wrapper:
            continue
        wrapper = inner_wrapper.find_parent("div", class_="wpb_wrapper")
        if not wrapper:
            continue

        for table in wrapper.find_all("table"):
            for entry in parse_schedule_table(table):
                entry["day"] = day_text
                all_entries.append(entry)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["band", "day", "stage", "time"])
        writer.writeheader()
        writer.writerows(all_entries)

    print(f"Wrote {len(all_entries)} entries to {output_path}")


if __name__ == "__main__":
    scrape_set_times()
