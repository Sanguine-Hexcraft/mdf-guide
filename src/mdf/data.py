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


def matches_filter(
    band: Band,
    search: list[str] | None = None,
    day: str | None = None,
    stage: str | None = None,
    genre: str | None = None,
) -> bool:
    if day:
        if day.lower() not in band.get("day", "").lower():
            return False
    if stage:
        if stage.lower() not in band.get("stage", "").lower():
            return False
    if genre:
        if genre.lower() not in band.get("genre", "").lower():
            return False
    if search:
        search_text = " ".join(search).lower()
        searchable = f"{band.get('band', '')} {band.get('genre', '')} {band.get('notes', '')}".lower()
        if search_text not in searchable:
            return False
    return True


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "mdf_bands.csv"
