# AGENTS.md - mdf-guide

## Running the Project

Use `uv` to run the CLI variants:

```bash
# TUI (black metal themed terminal UI) - current default
uv run python -m mdf.tui <search term>
uv run python -m mdf.tui --stage Soundstage --day Thursday
uv run python -m mdf.tui doom --genre death
uv run python -m mdf.tui --help

# Classic (simple prototype)
uv run python -m mdf.classic

# Remote (web UI with FastAPI + HTMX)
uv run python -m mdf.remote
# Open http://localhost:8000
```

## Project Structure

```
src/mdf/
├── data.py              # shared data loading & filtering
├── classic/
│   └── __main__.py      # original prototype
├── tui/
│   └── __main__.py      # black metal themed TUI
└── remote/
    ├── __main__.py      # FastAPI + HTMX web UI
    └── templates/       # Jinja2 templates
```

- `data/mdf_bands.csv` - main data file
- `scripts/crawler.py` - web scraping script for updating band data

## Features (TUI)

- Filters: `--day`, `--stage`, `--genre` (partial match, case-insensitive)
- Free-text search: matches band name, genre, notes
- Rating system: ✧ (1), ⛧ (2), ⛧⛧ (3) - inverted pentagrams
- Black metal theme: dark terminal output with ice-blue accents
- All columns displayed: band, day, stage, genre, location, rating

## Features (Remote)

- HTMX-powered live filtering (no page reloads)
- Query params: `?day=`, `?stage=`, `?genre=`, `?q=`
- Dark theme with ice-blue accents
- Reuses data.py filtering logic

## Dependencies

- beautifulsoup4, requests (from pyproject.toml)
- fastapi, uvicorn, jinja2, httpx
- Python >=3.12