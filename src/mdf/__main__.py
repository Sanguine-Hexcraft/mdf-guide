from pathlib import Path
import sys
import csv

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "bands.csv"
    
    if len(sys.argv) < 2:
        print("Please use a search term, for example (uv run python -m mdf <search term>)")
        sys.exit(1)

    search_term = sys.argv[1].lower()
    # search_term2 = sys.argv[2].lower() # 2 search terms experiment.
    results = []

    # open the file at data_path
    # enoding="utf-8" avoids weird character bugs later?
    # newline="" is needed by the csv module, prevents double-line issues on Windows
    with open(data_path, newline="", encoding="utf-8") as f:
        # turn the csv from raw text to a dict with keys and values
        reader = csv.DictReader(f)
        for row in reader:
            if any(search_term in value.lower() for value in row.values()):
                results.append(row)

    print("Search Results:")
    for band in results:
        print(
            f"{band['band']} | {band['day']} | {band['stage']} | "
            f"{band['time']} | {band['genre']}"
    )

if __name__ == "__main__":
    main()
