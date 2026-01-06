from pathlib import Path
import sys

def main():

    p = Path("data/bands.csv")
    
    if len(sys.argv) < 2:
        print("Please use a search term, for example (uv run python -m mdf <search term>)")
        sys.exit(1)

    search_term = sys.argv[1].lower()
    results = []

    with p.open() as f:
        for line in f:
            if search_term in line.lower():
                results.append(line)

    print(f"Search Results:")
    print("".join(results))
    # print(f"Contents: {contents}")


if __name__ == "__main__":
    main()
