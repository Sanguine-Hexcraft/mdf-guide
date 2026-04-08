# Maryland Deathfest Guide

A terminal-based guide for **Maryland Deathfest 2026**, built as a learning project and a useful personal tool.

This project exists primarily to:

- learn modern Python project structure
- practice working with real-world data
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
# TUI (black metal themed terminal UI) - current default
uv run python -m mdf.tui <search term>
uv run python -m mdf.tui --stage Soundstage --day Thursday
uv run python -m mdf.tui doom --genre death

# Classic (simple prototype)
uv run python -m mdf.classic

# Remote (web UI with FastAPI + HTMX)
uv run python -m mdf.remote
# Open http://localhost:8000
```

### TUI Options

| Flag | Description |
|------|-------------|
| `--day` | Filter by day (partial match) |
| `--stage` | Filter by stage (partial match) |
| `--genre` | Filter by genre (partial match) |

Free-text search matches band name, genre, and notes.

### Remote Options

| Query Param | Description |
|------------|-------------|
| `?day=` | Filter by day |
| `?stage=` | Filter by stage |
| `?genre=` | Filter by genre |
| `?q=` | Free-text search |

HTMX provides live filtering as you type/select.

---

## Project Structure

```
src/mdf/
├── data.py           # shared CSV loading & filtering
├── classic/          # original prototype
├── tui/              # black metal themed TUI
└── remote/           # web UI with FastAPI + HTMX
```

### Data

- `data/mdf_bands.csv` - main band data
- `scripts/crawler.py` - web scraping for updates

---

## Rating System

- ✧ (1) - Worth checking out
- ⛧ (2) - Recommended  
- ⛧⛧ (3) - Must see

---

## Dependencies

- Python >=3.12
- beautifulsoup4, requests (for crawler)
- fastapi, uvicorn, jinja2, httpx (for web UI)