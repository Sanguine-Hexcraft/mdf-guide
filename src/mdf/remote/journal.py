import os
import sqlite3
from datetime import datetime
from pathlib import Path

_data_dir = Path(os.environ.get("DATA_DIR", "/data"))
DB_PATH = _data_dir / "journal.db"
PHOTOS_DIR = _data_dir / "photos"


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                band TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                band TEXT NOT NULL,
                filename TEXT NOT NULL,
                caption TEXT,
                created_at TEXT NOT NULL
            );
        """)


def add_note(band: str, content: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO notes (band, content, created_at) VALUES (?, ?, ?)",
            (band, content, datetime.utcnow().isoformat()),
        )


def add_photo(band: str, filename: str, caption: str | None) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO photos (band, filename, caption, created_at) VALUES (?, ?, ?, ?)",
            (band, filename, caption, datetime.utcnow().isoformat()),
        )


def get_journal(band: str) -> dict:
    with _conn() as conn:
        notes = conn.execute(
            "SELECT content, created_at FROM notes WHERE band = ? ORDER BY created_at",
            (band,),
        ).fetchall()
        photos = conn.execute(
            "SELECT filename, caption, created_at FROM photos WHERE band = ? ORDER BY created_at",
            (band,),
        ).fetchall()
    return {
        "notes": [dict(r) for r in notes],
        "photos": [dict(r) for r in photos],
    }


def get_all_bands_with_entries() -> set[str]:
    with _conn() as conn:
        notes = {r[0] for r in conn.execute("SELECT DISTINCT band FROM notes").fetchall()}
        photos = {r[0] for r in conn.execute("SELECT DISTINCT band FROM photos").fetchall()}
    return notes | photos
