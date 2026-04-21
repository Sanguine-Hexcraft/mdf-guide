# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for dependency management (no pip/venv setup needed).

```bash
# Run the TUI
uv run python -m mdf.tui [search terms] [--day DAY] [--stage STAGE] [--genre GENRE]

# Run the web UI (served at http://localhost:8000)
uv run python -m mdf.remote

# Run the original prototype
uv run python -m mdf.classic

# Run the web scraper to update band data
uv run python scripts/crawler.py
```

There are no automated tests or linting configured.

## Architecture

The project has three independent front-ends that all share a single data layer:

- **`src/mdf/data.py`** — the shared core. Defines the `Band` TypedDict, `load_bands()` (reads `data/mdf_bands.csv`), and `matches_filter()` which powers all three UIs. All filtering logic lives here.
- **`src/mdf/tui/`** — terminal UI using raw ANSI escape codes (no curses/rich). Prints a box-drawing table to stdout and exits.
- **`src/mdf/remote/`** — FastAPI + HTMX web UI. Two routes: `GET /` returns a full page render, `GET /bands` returns only the table rows (used by HTMX for live filtering). Templates are Jinja2 in `src/mdf/remote/templates/`.
- **`src/mdf/classic/`** — original prototype, hardcoded query, kept for reference.

## Data

`data/mdf_bands.csv` is the single source of truth. CSV columns: `band`, `day`, `stage`, `genre`, `location`, `time`, `must_see`, `metal_archives`, `notes`.

The `must_see` column is a numeric rating (inverted — 0 = must-see ⛧⛧, 1 = recommended ⛧, 2 = worth checking out ✧, 3 = lowest priority).

`data_path` is resolved relative to `__file__` in `data.py`, so the CSV is always found regardless of the working directory.

## Themes

The web UI supports a `?theme=` query param (default: `death`). The TUI uses hardcoded ANSI ice-blue/dark styling throughout.
