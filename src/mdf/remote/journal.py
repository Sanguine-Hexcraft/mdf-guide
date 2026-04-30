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
            CREATE TABLE IF NOT EXISTS seen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                band TEXT NOT NULL UNIQUE,
                seen_at TEXT NOT NULL
            );
        """)


def add_note(band: str, content: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO notes (band, content, created_at) VALUES (?, ?, ?)",
            (band, content, datetime.utcnow().isoformat()),
        )


def update_note(note_id: int, content: str) -> None:
    with _conn() as conn:
        conn.execute("UPDATE notes SET content = ? WHERE id = ?", (content, note_id))


def delete_note(note_id: int) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))


def add_photo(band: str, filename: str, caption: str | None) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO photos (band, filename, caption, created_at) VALUES (?, ?, ?, ?)",
            (band, filename, caption, datetime.utcnow().isoformat()),
        )


def update_photo_caption(photo_id: int, caption: str | None) -> None:
    with _conn() as conn:
        conn.execute("UPDATE photos SET caption = ? WHERE id = ?", (caption or None, photo_id))


def delete_photo(photo_id: int) -> str | None:
    with _conn() as conn:
        row = conn.execute("SELECT filename FROM photos WHERE id = ?", (photo_id,)).fetchone()
        if row:
            conn.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
            return row["filename"]
    return None


def get_journal(band: str) -> dict:
    with _conn() as conn:
        notes = conn.execute(
            "SELECT id, content, created_at FROM notes WHERE band = ? ORDER BY created_at",
            (band,),
        ).fetchall()
        photos = conn.execute(
            "SELECT id, filename, caption, created_at FROM photos WHERE band = ? ORDER BY created_at",
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


def toggle_seen(band: str) -> bool:
    """Returns True if band is now seen, False if now unseen."""
    with _conn() as conn:
        exists = conn.execute("SELECT 1 FROM seen WHERE band = ?", (band,)).fetchone()
        if exists:
            conn.execute("DELETE FROM seen WHERE band = ?", (band,))
            return False
        else:
            conn.execute("INSERT INTO seen (band, seen_at) VALUES (?, ?)", (band, datetime.utcnow().isoformat()))
            return True


def get_seen_bands() -> set[str]:
    with _conn() as conn:
        return {r[0] for r in conn.execute("SELECT band FROM seen").fetchall()}


def get_summary() -> list[dict]:
    """All explicitly-seen or journal-having bands with their entries, for the summary page."""
    with _conn() as conn:
        seen = {r[0] for r in conn.execute("SELECT band FROM seen").fetchall()}
        journal_bands = {r[0] for r in conn.execute("SELECT DISTINCT band FROM notes").fetchall()} | \
                        {r[0] for r in conn.execute("SELECT DISTINCT band FROM photos").fetchall()}
        all_bands = seen | journal_bands
        result = []
        for band in all_bands:
            notes = conn.execute(
                "SELECT id, content, created_at FROM notes WHERE band = ? ORDER BY created_at", (band,)
            ).fetchall()
            photos = conn.execute(
                "SELECT id, filename, caption, created_at FROM photos WHERE band = ? ORDER BY created_at", (band,)
            ).fetchall()
            result.append({
                "band": band,
                "explicitly_seen": band in seen,
                "notes": [dict(r) for r in notes],
                "photos": [dict(r) for r in photos],
            })
    return result
