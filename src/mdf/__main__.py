from pathlib import Path
import sys
import csv


SUPPORTED_FLAGS = {
    "--day": "day",
    "--genre": "genre",
    "--stage": "stage"
}



def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "bands.csv"
    
    # if len(sys.argv) < 2:
        # print("Please use a search term, for example (uv run python -m mdf <search term>)")
        # sys.exit(1)

    # search_term = sys.argv[1].lower()
    # search_term2 = sys.argv[2].lower() # 2 search terms experiment.
    results = []

    # TEST query
    query = {"day": "Saturday", "stage": "Main Stage"}
    


    # open the file at data_path
    # enoding="utf-8" avoids weird character bugs later?
    # newline="" is needed by the csv module, prevents double-line issues on Windows
    with open(data_path, newline="", encoding="utf-8") as f:
        # turn the csv from raw text to a dict with keys and values
        reader = csv.DictReader(f)
        for row in reader:
            # if any(search_term in value.lower() for value in row.values()):
            if band_matches_query(row, query):
                results.append(row)

    print("Search Results:")
    for band in results:
        print(
            f"{band['band']} | {band['day']} | {band['stage']} | "
            f"{band['time']} | {band['genre']}"
    )



# We just want a function that returns True if the
# query condition is True
def band_matches_query(band: dict, query: dict) -> bool:
    for field, wanted in query.items():
        band_value = band.get(field)
        
        if band_value is None:
            return False

        band_value = band_value.lower()
        wanted = wanted.lower()
        
        if field in ("day", "stage"):
            if band_value != wanted:
                return False
        elif field == "genre":
            if wanted not in band_value:
                return False

        else: 
            return False

    return True


if __name__ == "__main__":
    main()
