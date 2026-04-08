# Maryland Deathfest Guide

A terminal-based guide for **Maryland Deathfest 2026**, built as a learning project and a useful personal tool.

This project exists primarily to:

- learn modern Python project structure
- practice working with real-world data
- build a useful festival companion
- stay terminal-focused and minimal (black metal treatment)

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

# Remote (future web/API version - coming soon)
uv run python -m mdf.remote
```

### TUI Options

| Flag | Description |
|------|-------------|
| `--day` | Filter by day (partial match) |
| `--stage` | Filter by stage (partial match) |
| `--genre` | Filter by genre (partial match) |

Free-text search matches band name, genre, and notes.

---

## Project Structure

```
src/mdf/
├── data.py           # shared CSV loading & filtering
├── classic/          # original prototype
├── tui/              # current black metal TUI
└── remote/           # future web version (placeholder)
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