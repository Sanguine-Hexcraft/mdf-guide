from pathlib import Path
import sys

def main():

    p = Path("/home/sanguine/workspace/mdf-guide/data/bands.csv")
    
    if len(sys.argv) < 2:
        print("Please use a search term, for example (uv run python -m mdf <search term>)")
        sys.exit(1)

    search_term = sys.argv[1]
    results = []

    with open(p, "r") as f:
        contents = f.readlines()

    for line in contents:
        
        if search_term.lower() in line.lower():
            results.append(line)

    print(f"Search Results: {"".join(results)}")
    # print(f"Contents: {contents}")


if __name__ == "__main__":
    main()
