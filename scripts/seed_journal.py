"""
Seed the journal DB with existing CSV notes.
Safe to re-run — skips any band that already has a journal entry.
"""
import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
csv_path = project_root / "data" / "mdf_bands.csv"

data_dir = Path(os.environ.get("DATA_DIR", project_root / ".local_data"))
db_path = data_dir / "journal.db"

db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Ensure table exists
conn.executescript("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        band TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
""")

# Find bands that already have journal entries
existing = {r[0] for r in conn.execute("SELECT DISTINCT band FROM notes").fetchall()}

seeded = []
skipped = []

with open(csv_path, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        note = row.get("notes", "").strip()
        band = row["band"].strip()
        if not note:
            continue
        if band in existing:
            skipped.append(band)
            continue
        conn.execute(
            "INSERT INTO notes (band, content, created_at) VALUES (?, ?, ?)",
            (band, note, datetime.utcnow().isoformat()),
        )
        seeded.append((band, note))

conn.commit()
conn.close()

print(f"Seeded {len(seeded)} bands into {db_path}\n")
for band, note in seeded:
    print(f"  {band}: {note[:80]}")

if skipped:
    print(f"\nSkipped {len(skipped)} bands (already had entries):")
    for band in skipped:
        print(f"  {band}")
