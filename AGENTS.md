# AGENTS.md - mdf-guide

## Running the Project

Use `uv` to run the CLI:
```bash
uv run python -m mdf <search term>
```

With filters:
```bash
uv run python -m mdf --stage Soundstage --day Thursday
uv run python -m mdf doom --genre death
uv run python -m mdf --help
```

## Project Structure

- `src/mdf/__main__.py` - CLI entry point
- `data/mdf_bands.csv` - main data file (CSV with band/day/stage/genre/location/must_see/metal_archives/notes columns)
- `scripts/crawler.py` - web scraping script for updating band data
- `data/MDF 2026 Info - bands_raw.csv` - source data file (hand-curated)

## Features

- Filters: `--day`, `--stage`, `--genre` (partial match, case-insensitive)
- Free-text search: matches band name, genre, notes
- Rating system: ✧ (1), ⛧ (2), ⛧⛧ (3) - inverted pentagrams
- Black metal theme: dark terminal output with ice-blue accents
- All columns displayed: band, day, stage, genre, location, rating

## Dependencies

- beautifulsoup4, requests (from pyproject.toml)
- Python >=3.12 (uses argparse stdlib)
