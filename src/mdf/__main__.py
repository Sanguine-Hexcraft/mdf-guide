from pathlib import Path
import sys

def main():
    project_root = Path(__file__).resolve().parents[2]
    p = project_root / "data" / "bands.csv"
    
    if len(sys.argv) < 2:
        print("Please use a search term, for example (uv run python -m mdf <search term>)")
        sys.exit(1)

    search_term = sys.argv[1].lower()
    # search_term2 = sys.argv[2].lower() # 2 search terms experiment
    results = []

    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if search_term in line.lower(): # or search_term2 in line.lower():
                results.append(line)

    print(f"Search Results:")
    print("".join(results))


if __name__ == "__main__":
    main()
