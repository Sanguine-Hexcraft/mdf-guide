from pathlib import Path
import sys
import csv

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    p = project_root / "data" / "bands.csv"
    
    if len(sys.argv) < 2:
        print("Please use a search term, for example (uv run python -m mdf <search term>)")
        sys.exit(1)

    search_term = sys.argv[1].lower()
    # search_term2 = sys.argv[2].lower() # 2 search terms experiment
    results = []

    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)        
        for row in reader:
            # search across all fields
            if any(search_term in value.lower() for value in row.values()):
                results.append(row)

    print(f"Search Results:")
    for band in results:
        print(
            f"{band['band']} | {band['day']} | {band['stage']} | "
            f"{band['time']} | {band['genre']}"
        )

if __name__ == "__main__":
    main()
