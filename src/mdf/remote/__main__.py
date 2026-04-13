from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mdf.data import load_bands, matches_filter, Band

app = FastAPI(title="MDF Guide")

templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    q: str | None = Query(None),
    day: str | None = Query(None),
    stage: str | None = Query(None),
    genre: str | None = Query(None),
    sort: str | None = Query(None),
    order: str | None = Query("asc"),
    theme: str | None = Query("death"),
):
    bands = load_bands()
    search_terms = q.split() if q else None
    filtered = [
        band for band in bands if matches_filter(band, search_terms, day, stage, genre)
    ]
    if sort and sort in ("band", "day", "stage", "genre", "location", "must_see"):
        reverse = order == "desc"
        filtered.sort(key=lambda b: b.get(sort, "").lower(), reverse=reverse)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "bands": filtered,
            "sort": sort,
            "order": order,
            "theme": theme,
            "request": request,
        },
    )


@app.get("/bands", response_class=HTMLResponse)
async def get_bands(
    request: Request,
    q: str | None = Query(None),
    day: str | None = Query(None),
    stage: str | None = Query(None),
    genre: str | None = Query(None),
    sort: str | None = Query(None),
    order: str | None = Query("asc"),
    theme: str | None = Query("death"),
):
    bands = load_bands()
    search_terms = q.split() if q else None

    filtered = [
        band for band in bands if matches_filter(band, search_terms, day, stage, genre)
    ]

    if sort and sort in ("band", "day", "stage", "genre", "location", "must_see"):
        reverse = order == "desc"
        filtered.sort(key=lambda b: b.get(sort, "").lower(), reverse=reverse)

    return templates.TemplateResponse(
        request=request,
        name="band_rows.html",
        context={
            "bands": filtered,
            "sort": sort,
            "order": order,
            "theme": theme,
            "request": request,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
