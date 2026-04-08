from pathlib import Path
import csv
from typing import TypedDict


class Band(TypedDict):
    band: str
    day: str
    stage: str
    genre: str
    location: str
    must_see: str
    metal_archives: str
    notes: str


def load_bands(data_path: Path | None = None) -> list[Band]:
    if data_path is None:
        project_root = Path(__file__).resolve().parents[2]
        data_path = project_root / "data" / "mdf_bands.csv"

    bands = []
    with open(data_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bands.append(Band(row))
    return bands


import re


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def fuzzy_match(query: str, text: str) -> bool:
    q = _normalize(query)
    t = _normalize(text)
    return q in t


def matches_filter(
    band: Band,
    search: list[str] | None = None,
    day: str | None = None,
    stage: str | None = None,
    genre: str | None = None,
) -> bool:
    if day:
        if not fuzzy_match(day, band.get("day", "")):
            return False
    if stage:
        if not fuzzy_match(stage, band.get("stage", "")):
            return False
    if genre:
        if not fuzzy_match(genre, band.get("genre", "")):
            return False
    if search:
        searchable = " ".join(
            [
                band.get("band", ""),
                band.get("genre", ""),
                band.get("notes", ""),
                band.get("location", ""),
                band.get("stage", ""),
                band.get("day", ""),
            ]
        )
        for term in search:
            if not fuzzy_match(term, searchable):
                return False
    return True


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "mdf_bands.csv"
