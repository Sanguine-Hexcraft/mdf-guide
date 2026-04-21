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

## Running Locally

This project uses `uv` for dependency management — no pip or venv setup needed.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### TUI — Terminal UI

```bash
uv run python -m mdf.tui                          # all bands
uv run python -m mdf.tui oranssi                  # free-text search
uv run python -m mdf.tui --day Friday             # filter by day
uv run python -m mdf.tui --stage Soundstage       # filter by stage
uv run python -m mdf.tui --day Saturday --genre black
uv run python -m mdf.tui doom --genre death       # combined
```

| Flag | Description |
|------|-------------|
| `--day` | Filter by day (partial match, e.g. `Wednesday`, `Friday`) |
| `--stage` | Filter by stage (partial match, e.g. `Soundstage`, `Angels`) |
| `--genre` | Filter by genre (partial match, e.g. `black`, `doom`) |
| positional args | Free-text search across band name, genre, notes, stage, day |

All filters use fuzzy/partial matching — `--day wed` matches `Wednesday May 20, 2026`.

### Web UI — FastAPI + HTMX

```bash
uv run python -m mdf.remote
# Open http://localhost:8000
```

Live filtering as you type. Theme (Death/Black) is toggled via the dropdown in the top-right and persists in `localStorage`. Columns are sortable by clicking the headers.

### Classic — Original Prototype

```bash
uv run python -m mdf.classic
```

Hardcoded query, kept for reference.

---

## Project Structure

```
src/mdf/
├── data.py              # shared CSV loading and filtering (used by all three UIs)
├── classic/             # original hardcoded prototype
├── tui/                 # ANSI escape code terminal UI
└── remote/              # FastAPI + HTMX web UI
    └── templates/       # Jinja2 templates (base, index, _table, band_rows)

data/
├── mdf_bands.csv        # source of truth — hand-curated + scraped, edit this one
├── set_times_raw.csv    # raw scrape output from deathfests.com/set-times/
├── bands_raw.csv        # raw scrape output from deathfests.com/lineup/
└── mdf_bands_new.csv    # last merge output, kept for reference

scripts/
├── crawler.py           # scrapes deathfests.com/lineup/ → bands_raw.csv
├── set_times_crawler.py # scrapes deathfests.com/set-times/ → set_times_raw.csv
├── merge.py             # merges scraped set times into hand-curated CSV
└── build_static.py      # generates docs/index.html for GitHub Pages

docs/
└── index.html           # auto-generated — do not edit by hand

.github/workflows/
└── deploy.yml           # builds and deploys to GitHub Pages on push to ai-improvements
```

---

## Data

`data/mdf_bands.csv` is the single source of truth. Edit this file to add ratings, notes, genre info, and Metal Archives links.

| Column | Description |
|--------|-------------|
| `band` | Band name, may include set descriptor e.g. "Kreator Deep Cuts" |
| `day` | Full date string e.g. "Friday May 22, 2026" (pre-fest = "Wednesday May 20, 2026") |
| `stage` | Venue — see stage list below |
| `genre` | Genre tags, free-form |
| `location` | Country of origin |
| `time` | Set time range e.g. "09:45-10:45" (12h display, scraped from schedule) |
| `must_see` | Rating: 0 ⛧⛧, 1 ⛧, 2 ✧, 3 · |
| `metal_archives` | Full URL to Metal Archives band page |
| `notes` | Personal notes, shown inline in TUI and web UI |

### Stages (2026)

| Stage | When |
|-------|------|
| Nevermore Hall | Pre-fest Wednesday + all main fest days |
| Power Plant Live | Thursday–Sunday main stage |
| Market Place | Thursday–Sunday main stage (split from Power Plant Live in 2026) |
| Soundstage | Thursday–Sunday, heavier/extreme focus |
| Angels Rock Bar | Friday–Sunday, smaller stage, earlier time slots |

### Updating for Lineup/Schedule Changes

When MDF updates the lineup or set times, re-scrape and merge:

```bash
# 1. Scrape the latest set times
uv run python scripts/set_times_crawler.py
# → overwrites data/set_times_raw.csv

# 2. Merge into hand-curated data (preserves your ratings, notes, genre, links)
uv run python scripts/merge.py
# → writes data/mdf_bands_new.csv and prints a diff:
#     NEW bands  — added to lineup, need genre/links filled in
#     DROPPED    — removed from lineup
#     NAME diffs — site name vs your hand-curated name

# 3. Review the diff, then swap in the new file
cp data/mdf_bands_new.csv data/mdf_bands.csv

# 4. Fill in any missing info for new bands directly in mdf_bands.csv

# 5. Rebuild the static site
uv run python scripts/build_static.py
```

The merge script uses fuzzy name matching to handle cases where the official schedule shortens names (e.g. "Kreator Deep Cuts" → "Kreator") without losing your hand-curated data.

---

## Rating System

Stored as a number (0–3), displayed as a symbol. Lower = better.

| Symbol | Value | Meaning |
|--------|-------|---------|
| ⛧⛧ | 0 | Must see — plan your day around this |
| ⛧  | 1 | Recommended |
| ✧  | 2 | Worth checking out if no conflict |
| ·  | 3 | Skip or lowest priority |

---

## Deployment

Pushes to `ai-improvements` automatically trigger a GitHub Actions build that:

1. Runs `uv run python scripts/build_static.py` to generate `docs/index.html`
2. Pushes the output to the `gh-pages` branch via `peaceiris/actions-gh-pages`

GitHub Pages then serves from the `gh-pages` branch root.

**First-time setup:** Go to the repo **Settings → Pages → Source**, set it to **Deploy from a branch**, select **gh-pages / root**, and save.

To rebuild the static site manually without deploying:

```bash
uv run python scripts/build_static.py
# → writes docs/index.html (self-contained, open directly in browser)
```

The static site embeds all band data as JSON and uses vanilla JS for filtering and sorting — no server or build tools required.

---

## Dependencies

- Python >= 3.12
- `beautifulsoup4`, `requests` — scrapers
- `fastapi`, `uvicorn`, `jinja2`, `httpx` — web UI
