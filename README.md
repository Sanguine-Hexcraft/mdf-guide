# Maryland Deathfest XXXX Guide

This is still very much a work in progress

A terminal-based guide for **Maryland Deathfest 2026**, built as a learning project as well as something useful.

This project exists primarily to:

- learn modern Python project structure
- practice working with real-world data
- build a useful personal tool
- stay terminal-focused and minimal (black metal treatment)

It is _not_ intended to be a production app or an official/unofficial festival resource.

---

## Running the Code

This project uses `uv` for dependency management. To run the code:

1. **Install uv** (if you haven't already):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Run the guide**:

   ```bash
   uv run python -m mdf <search term>
   ```

   You can also use two search terms:

   ```bash
   uv run python -m mdf <search term 1> <search term 2>
   ```

   Example:

   ```bash
   uv run python -m mdf death
   ```

---
