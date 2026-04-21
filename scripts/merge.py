"""
Merges set_times_raw.csv (authoritative for lineup/stage/time) with
mdf_bands.csv (authoritative for genre/location/must_see/metal_archives/notes).

Outputs data/mdf_bands_new.csv and prints a diff report.
"""

import csv
import unicodedata
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
SET_TIMES_PATH = project_root / "data" / "set_times_raw.csv"
HANDCRAFTED_PATH = project_root / "data" / "mdf_bands.csv"
OUTPUT_PATH = project_root / "data" / "mdf_bands_new.csv"

FIELDNAMES = ["band", "day", "stage", "genre", "location", "time", "must_see", "metal_archives", "notes"]


def normalize(name: str) -> str:
    """Lowercase, strip, normalize unicode (handles curly apostrophes, ellipsis, etc.)."""
    name = name.lower().strip()
    # Normalize unicode: NFKD then re-encode to ASCII where possible, keep rest
    # This converts curly apostrophes → ', ellipsis … → ...
    name = unicodedata.normalize("NFKD", name)
    name = name.replace("’", "'").replace("‘", "'")  # curly apostrophes
    name = name.replace("…", "...")                        # ellipsis
    return name


def find_match(st_band: str, hc_lookup: dict) -> tuple[str, dict] | tuple[None, None]:
    """
    Returns (hc_band_name, hc_row) for the best match, or (None, None).
    Strategy (in order):
      1. Exact match after normalization
      2. HC name starts with ST name — when multiple candidates exist, prefer the
         longest HC name so "Grave" picks "Grave Old School Grave & Corpse" over
         the unrelated band "Grave Infestation"
      3. ST name is contained anywhere in HC name (longest match wins)
    """
    norm_st = normalize(st_band)

    # 1. Exact
    if norm_st in hc_lookup:
        return hc_lookup[norm_st]

    # 2. HC name starts with ST name — collect all candidates, pick longest
    candidates = [
        (norm_hc, hc_name, hc_row)
        for norm_hc, (hc_name, hc_row) in hc_lookup.items()
        if norm_hc.startswith(norm_st)
    ]
    if candidates:
        candidates.sort(key=lambda c: len(c[0]), reverse=True)
        _, hc_name, hc_row = candidates[0]
        return hc_name, hc_row

    # 3. ST name substring of HC name — pick longest
    candidates = [
        (norm_hc, hc_name, hc_row)
        for norm_hc, (hc_name, hc_row) in hc_lookup.items()
        if norm_st in norm_hc
    ]
    if candidates:
        candidates.sort(key=lambda c: len(c[0]), reverse=True)
        _, hc_name, hc_row = candidates[0]
        return hc_name, hc_row

    return None, None


def main():
    # Load handcrafted CSV; normalize "Official Pre-Fest" to the actual date
    hc_rows = []
    with open(HANDCRAFTED_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["day"] == "Official Pre-Fest":
                row["day"] = "Wednesday May 20, 2026"
            hc_rows.append(row)

    # Build lookup: normalized_name → (original_name, row)
    hc_lookup: dict[str, tuple[str, dict]] = {}
    for row in hc_rows:
        hc_lookup[normalize(row["band"])] = (row["band"], row)

    # Load set times (authoritative source)
    with open(SET_TIMES_PATH, newline="", encoding="utf-8") as f:
        set_times = list(csv.DictReader(f))

    merged = []
    matched_hc_names = set()
    new_bands = []
    name_changes = []

    for entry in set_times:
        hc_name, hc_row = find_match(entry["band"], hc_lookup)

        if hc_row:
            matched_hc_names.add(normalize(hc_name))
            if normalize(hc_name) != normalize(entry["band"]):
                name_changes.append((entry["band"], hc_name))
            merged.append({
                "band": hc_name,
                "day": entry["day"],
                "stage": entry["stage"],
                "genre": hc_row["genre"],
                "location": hc_row["location"],
                "time": entry["time"],
                "must_see": hc_row["must_see"],
                "metal_archives": hc_row["metal_archives"],
                "notes": hc_row["notes"],
            })
        else:
            new_bands.append((entry["band"], entry["day"], entry["stage"]))
            merged.append({
                "band": entry["band"],
                "day": entry["day"],
                "stage": entry["stage"],
                "genre": "",
                "location": "",
                "time": entry["time"],
                "must_see": "",
                "metal_archives": "",
                "notes": "",
            })

    dropped = [
        row["band"] for row in hc_rows
        if normalize(row["band"]) not in matched_hc_names
    ]

    # Write output
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(merged)

    # Print diff report
    print(f"Wrote {len(merged)} entries to {OUTPUT_PATH.name}")
    print(f"  {len(merged) - len(new_bands)} matched from handcrafted CSV")
    print(f"  {len(new_bands)} new  |  {len(dropped)} dropped")
    print()

    if new_bands:
        print(f"NEW bands ({len(new_bands)}) — need genre/links filled in:")
        for band, day, stage in new_bands:
            print(f"  + {band}  [{day} / {stage}]")
        print()

    if dropped:
        print(f"DROPPED bands ({len(dropped)}) — removed from lineup:")
        for band in dropped:
            print(f"  - {band}")
        print()

    if name_changes:
        print(f"NAME differences — kept handcrafted name, set-times name shown in parens:")
        for st_name, hc_name in name_changes:
            print(f"  \"{hc_name}\"  (site: \"{st_name}\")")


if __name__ == "__main__":
    main()
