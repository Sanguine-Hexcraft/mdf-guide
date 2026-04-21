# Maryland Deathfest Guide

A terminal and web guide for **Maryland Deathfest 2026**, built as a learning project and a useful personal tool.

**Live site:** https://sanguine-hexcraft.github.io/mdf-guide

This project exists primarily to:

- learn modern Python project structure
- practice working with real-world data (web scraping, CSV merging)
- build a useful festival companion
- stay terminal-focused and minimal (black metal treatment)
- explore web development with FastAPI + HTMX

It is _not_ intended to be a production app or an official festival resource.

---

## Running the Code

This project uses `uv` for dependency management. If you haven't installed uv yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Available Variants

```bash
# TUI (black metal themed terminal UI)
uv run python -m mdf.tui [search terms]
uv run python -m mdf.tui --stage Soundstage --day Thursday
uv run python -m mdf.tui doom --genre death

# Web UI (FastAPI + HTMX, served at http://localhost:8000)
uv run python -m mdf.remote

# Classic (simple prototype, kept for reference)
uv run python -m mdf.classic
```

### TUI Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--day` | Filter by day (partial match) | `--day Friday` |
| `--stage` | Filter by stage (partial match) | `--stage Soundstage` |
| `--genre` | Filter by genre (partial match) | `--genre black` |
| (positional) | Free-text search across band, genre, notes | `mdf.tui oranssi` |

### Web UI Query Params

| Param | Description |
|-------|-------------|
| `?q=` | Free-text search |
| `?day=` | Filter by day |
| `?stage=` | Filter by stage |
| `?genre=` | Filter by genre |

Themes: append `?theme=death` (default) or `?theme=black` to the URL.

---

## Project Structure

```
src/mdf/
├── data.py             # shared CSV loading and filtering logic
├── classic/            # original prototype
├── tui/                # ANSI terminal UI
└── remote/             # FastAPI + HTMX web UI
    └── templates/      # Jinja2 templates

data/
├── mdf_bands.csv       # main band data (hand-curated + scraped)
├── set_times_raw.csv   # raw set times from deathfests.com/set-times/
└── mdf_bands_new.csv   # last merge output (for reference)

scripts/
├── crawler.py          # scrapes deathfests.com/lineup/ → bands_raw.csv
├── set_times_crawler.py # scrapes deathfests.com/set-times/ → set_times_raw.csv
├── merge.py            # merges set times data with hand-curated CSV
└── build_static.py     # builds docs/index.html for GitHub Pages

docs/
└── index.html          # auto-generated static site (do not edit by hand)
```

---

## Data

`data/mdf_bands.csv` is the single source of truth. CSV columns:

| Column | Description |
|--------|-------------|
| `band` | Band name (may include set descriptor, e.g. "Kreator Deep Cuts") |
| `day` | Full date string, e.g. "Friday May 22, 2026" |
| `stage` | Venue name |
| `genre` | Genre tags |
| `location` | Country of origin |
| `time` | Set time range, e.g. "09:45-10:45" |
| `must_see` | Rating: 0=must-see ⛧⛧, 1=recommended ⛧, 2=worth it ✧, 3=skip · |
| `metal_archives` | Link to Metal Archives entry |
| `notes` | Personal notes |

### Updating the Data

When the lineup or set times change, re-scrape and merge:

```bash
# 1. Re-scrape set times
uv run python scripts/set_times_crawler.py
# → writes data/set_times_raw.csv

# 2. Merge with hand-curated data (preserves genre, ratings, notes, links)
uv run python scripts/merge.py
# → writes data/mdf_bands_new.csv and prints a diff report

# 3. Review the diff output, then swap in the new file
cp data/mdf_bands_new.csv data/mdf_bands.csv

# 4. Rebuild the static site
uv run python scripts/build_static.py
```

The merge script fuzzy-matches band names between the two sources (handles cases like "Kreator Deep Cuts" → "Kreator"), preserving all hand-curated fields while updating day, stage, and set times from the official schedule.

### Stages (2026)

| Stage | Notes |
|-------|-------|
| Nevermore Hall | Wednesday pre-fest + main fest |
| Power Plant Live | Main stage |
| Market Place | Main stage (separate from Power Plant Live as of 2026) |
| Soundstage | Heavy/extreme focus |
| Angels Rock Bar | Smaller stage, earlier sets |

---

## Rating System

| Symbol | Value | Meaning |
|--------|-------|---------|
| ⛧⛧ | 0 | Must see — drop everything |
| ⛧ | 1 | Recommended |
| ✧ | 2 | Worth checking out |
| · | 3 | Skip or low priority |

Ratings are personal and subjective.

---

## Deployment

The static site at `docs/index.html` is auto-built and deployed to GitHub Pages via GitHub Actions on every push to `ai-improvements`. The static build embeds all band data as JSON and uses vanilla JS for filtering and sorting — no server required.

To manually rebuild the static site:

```bash
uv run python scripts/build_static.py
```

---

## Dependencies

- Python >=3.12
- `beautifulsoup4`, `requests` — crawler/scraper
- `fastapi`, `uvicorn`, `jinja2`, `httpx` — web UI
