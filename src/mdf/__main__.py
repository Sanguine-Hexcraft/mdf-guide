from pathlib import Path
import argparse
import csv
import sys


RESET = "\x1b[0m"
BLACK = "\x1b[40m"
WHITE = "\x1b[37m"
GRAY = "\x1b[90m"
CYAN = "\x1b[36m"
BOLD = "\x1b[1m"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="mdf",
        description="MDF 2026 Terminal Guide - Black Metal Edition",
        epilog='Examples:\n  mdf soundstage\n  mdf --stage soundstage --day "Thursday"\n  mdf doom --genre death',
    )
    parser.add_argument("search", nargs="*", help="Search terms to filter bands")
    parser.add_argument("--day", help="Filter by day (partial match)")
    parser.add_argument("--stage", help="Filter by stage (partial match)")
    parser.add_argument("--genre", help="Filter by genre (partial match)")
    return parser.parse_args()


def load_bands(data_path: Path) -> list[dict]:
    bands = []
    with open(data_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bands.append(row)
    return bands


def matches_filter(band: dict, args) -> bool:
    if args.day:
        if args.day.lower() not in band.get("day", "").lower():
            return False
    if args.stage:
        if args.stage.lower() not in band.get("stage", "").lower():
            return False
    if args.genre:
        if args.genre.lower() not in band.get("genre", "").lower():
            return False
    if args.search:
        search_text = " ".join(args.search).lower()
        searchable = f"{band.get('band', '')} {band.get('genre', '')} {band.get('notes', '')}".lower()
        if search_text not in searchable:
            return False
    return True


def format_rating(value: str) -> str:
    try:
        rating = int(value)
    except (ValueError, TypeError):
        return "   "
    if rating == 0:
        return f"{CYAN}⛧⛧{RESET}"  # Can't miss - most metal
    elif rating == 1:
        return f"{CYAN}⛧{RESET} "  # Need to see
    elif rating == 2:
        return f"{GRAY}✧{RESET} "  # Want to see
    elif rating >= 3:
        return f"{GRAY}·{RESET} "  # Would see but maybe pizza
    return "   "


def format_row(band: dict, widths: dict) -> str:
    name = band.get("band", "")[: widths["band"]]
    day = band.get("day", "")[: widths["day"]]
    stage = band.get("stage", "")[: widths["stage"]]
    genre = band.get("genre", "")[: widths["genre"]]
    rating = format_rating(band.get("must_see", ""))
    location = band.get("location", "")[: widths["location"]]

    return (
        f"{WHITE}{name:<{widths['band']}}{RESET} │ "
        f"{GRAY}{day:<{widths['day']}}{RESET} │ "
        f"{stage:<{widths['stage']}} │ "
        f"{genre:<{widths['genre']}} │ "
        f"{location:<{widths['location']}} │ "
        f"{rating}"
    )


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parents[2]
    data_path = project_root / "data" / "mdf_bands.csv"

    if not data_path.exists():
        print(f"{BLACK}{WHITE}Error: Data file not found{RESET}")
        print(f"  Expected: {data_path}")
        sys.exit(1)

    bands = load_bands(data_path)
    filtered = [b for b in bands if matches_filter(b, args)]

    if not filtered:
        print(f"{BLACK}{WHITE}No results found{RESET}")
        sys.exit(0)

    widths = {
        "band": max(len(b.get("band", "")) for b in filtered) + 1,
        "day": max(len(b.get("day", "")) for b in filtered) + 1,
        "stage": max(len(b.get("stage", "")) for b in filtered) + 1,
        "genre": max(len(b.get("genre", "")) for b in filtered) + 1,
        "location": max(len(b.get("location", "")) for b in filtered) + 1,
    }

    widths = {k: min(v, 20) for k, v in widths.items()}

    filter_desc = "All Bands"
    if args.stage:
        filter_desc = args.stage
    elif args.day:
        filter_desc = args.day

    print(f"{BLACK}")
    print(
        f"╭{'─' * (widths['band'] + widths['day'] + widths['stage'] + widths['genre'] + widths['location'] + 14)}╮"
    )
    print(
        f"│  {CYAN}☠{RESET} {BOLD}MDF 2026 - {filter_desc}{RESET}{' ' * (56 - len(filter_desc))}│"
    )
    print(
        f"├{'─' * (widths['band'] + widths['day'] + widths['stage'] + widths['genre'] + widths['location'] + 14)}┤"
    )
    print(
        f"│{WHITE} Band{' ' * (widths['band'] - 3)}│ Day{' ' * (widths['day'] - 3)}│ Stage{' ' * (widths['stage'] - 5)}│ Genre{' ' * (widths['genre'] - 5)}│ Location{' ' * (widths['location'] - 7)}│  ⚝{RESET}│"
    )
    print(
        f"├{'─' * (widths['band'] + widths['day'] + widths['stage'] + widths['genre'] + widths['location'] + 14)}┤"
    )

    for band in filtered:
        print(f"│ {format_row(band, widths)} │")

    print(
        f"╰{'─' * (widths['band'] + widths['day'] + widths['stage'] + widths['genre'] + widths['location'] + 14)}╯"
    )
    print(f"{RESET}", end="")


if __name__ == "__main__":
    main()
