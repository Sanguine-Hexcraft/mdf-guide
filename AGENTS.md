# AGENTS.md - mdf-guide

## Running the Project

Use `uv` to run the CLI:
```bash
uv run python -m mdf <search term>
```

## Project Structure

- `src/mdf/__main__.py` - CLI entry point
- `data/bands_raw.csv` - main data file (CSV with band/day/stage/genre columns)
- `scripts/crawler.py` - web scraping script for updating band data
- `data/raw.html` - raw HTML from source website
- `data/MDF_2026_Info.csv` - original scraped data

## Dependencies

- beautifulsoup4, requests (from pyproject.toml)

## Notes

- Python version: >=3.12
- This is a personal learning project, not production code
- Main functionality filters bands by `--day`, `--stage`, `--genre` flags
- Currently the query is hardcoded in `__main__.py` (see line 27) - needs CLI argument parsing