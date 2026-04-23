import os
import uuid
from pathlib import Path

from fastapi import Cookie, FastAPI, Form, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mdf.data import load_bands, matches_filter
from mdf.remote.journal import (
    PHOTOS_DIR,
    add_note,
    add_photo,
    get_all_bands_with_entries,
    get_journal,
    init_db,
)

app = FastAPI(title="MDF Guide")

templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=templates_dir)

JOURNAL_PASSWORD = os.environ.get("JOURNAL_PASSWORD", "")
SESSION_TOKEN = os.environ.get("SESSION_TOKEN", "dev-token")

DAY_ORDER = {
    "Wednesday": 0,
    "Thursday": 1,
    "Friday": 2,
    "Saturday": 3,
    "Sunday": 4,
}


def day_sort_key(band: dict) -> int:
    day = band.get("day", "")
    for name, order in DAY_ORDER.items():
        if name in day:
            return order
    return 99


def is_authed(session: str | None) -> bool:
    return bool(JOURNAL_PASSWORD) and session == SESSION_TOKEN


@app.on_event("startup")
async def startup():
    init_db()
    try:
        app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")
    except RuntimeError:
        pass


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@app.post("/login")
async def login(password: str = Form(...)):
    if password == JOURNAL_PASSWORD:
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("session", SESSION_TOKEN, httponly=True, samesite="lax")
        return response
    return RedirectResponse("/login?error=1", status_code=303)


@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("session")
    return response


def _get_bands(q, day, stage, genre, sort, order):
    bands = load_bands()
    search_terms = q.split() if q else None
    filtered = [b for b in bands if matches_filter(b, search_terms, day, stage, genre)]
    if sort == "must_see":
        filtered.sort(
            key=lambda b: int(b.get("must_see") or 99),
            reverse=(order == "desc"),
        )
    elif sort == "day":
        filtered.sort(key=day_sort_key, reverse=(order == "desc"))
    elif sort and sort in ("band", "stage", "genre", "location", "time"):
        filtered.sort(key=lambda b: b.get(sort, "").lower(), reverse=(order == "desc"))
    else:
        filtered.sort(key=day_sort_key)
    return filtered


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    q: str | None = Query(None),
    day: str | None = Query(None),
    stage: str | None = Query(None),
    genre: str | None = Query(None),
    sort: str | None = Query(None),
    order: str | None = Query("asc"),
    session: str | None = Cookie(None),
):
    bands = _get_bands(q, day, stage, genre, sort, order)
    has_journal = get_all_bands_with_entries()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "bands": bands,
            "sort": sort,
            "order": order,
            "request": request,
            "authed": is_authed(session),
            "has_journal": has_journal,
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
    session: str | None = Cookie(None),
):
    bands = _get_bands(q, day, stage, genre, sort, order)
    has_journal = get_all_bands_with_entries()
    return templates.TemplateResponse(
        request=request,
        name="band_rows.html",
        context={
            "bands": bands,
            "sort": sort,
            "order": order,
            "request": request,
            "authed": is_authed(session),
            "has_journal": has_journal,
        },
    )


@app.get("/band/{band_name}", response_class=HTMLResponse)
async def band_detail(request: Request, band_name: str, session: str | None = Cookie(None)):
    journal = get_journal(band_name)
    return templates.TemplateResponse(
        request=request,
        name="band_detail.html",
        context={
            "band_name": band_name,
            "journal": journal,
            "authed": is_authed(session),
            "request": request,
        },
    )


@app.post("/band/{band_name}/note")
async def post_note(band_name: str, content: str = Form(...), session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    add_note(band_name, content)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.post("/band/{band_name}/photo")
async def post_photo(
    band_name: str,
    photo: UploadFile,
    caption: str = Form(""),
    session: str | None = Cookie(None),
):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    ext = Path(photo.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    dest = PHOTOS_DIR / filename
    dest.write_bytes(await photo.read())
    add_photo(band_name, filename, caption or None)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
