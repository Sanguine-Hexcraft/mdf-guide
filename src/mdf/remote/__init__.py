import os
import uuid
from pathlib import Path

from fastapi import Cookie, FastAPI, Form, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mdf.data import load_bands, matches_filter
from mdf.remote.journal import (
    PHOTOS_DIR,
    add_note,
    add_photo,
    delete_note,
    delete_photo,
    get_all_bands_with_entries,
    get_journal,
    get_seen_bands,
    get_summary,
    init_db,
    toggle_seen,
    update_note,
    update_photo_caption,
)

app = FastAPI(title="MDF Guide")

templates_dir = Path(__file__).resolve().parent / "templates"
static_dir = Path(__file__).resolve().parent / "static"
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
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    try:
        app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")
    except RuntimeError:
        pass


@app.get("/sw.js")
async def service_worker():
    return FileResponse(static_dir / "sw.js", media_type="application/javascript")


@app.get("/manifest.json")
async def manifest():
    return FileResponse(static_dir / "manifest.json", media_type="application/manifest+json")


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


def _parse_time_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    if h < 2:
        h += 24
    return h * 60 + m


def _parse_slot(time_range: str) -> tuple[int, int] | None:
    if not time_range or "-" not in time_range:
        return None
    parts = time_range.split("-")
    try:
        return (_parse_time_minutes(parts[0]), _parse_time_minutes(parts[1]))
    except (ValueError, AttributeError):
        return None


def _slots_overlap(s1, s2) -> bool:
    if not s1 or not s2:
        return False
    return s1[0] < s2[1] and s2[0] < s1[1]


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
    # Always return all bands — filtering is done client-side for offline support.
    # Only sort is applied server-side so column headers work correctly.
    bands = _get_bands(None, None, None, None, sort, order)
    has_journal = get_all_bands_with_entries()
    seen_bands = get_seen_bands() | has_journal
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
            "seen_bands": seen_bands,
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
    seen_bands = get_seen_bands() | has_journal
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
            "seen_bands": seen_bands,
        },
    )


@app.get("/band/{band_name}", response_class=HTMLResponse)
async def band_detail(request: Request, band_name: str, session: str | None = Cookie(None)):
    journal = get_journal(band_name)
    seen = band_name in (get_seen_bands() | get_all_bands_with_entries())
    return templates.TemplateResponse(
        request=request,
        name="band_detail.html",
        context={
            "band_name": band_name,
            "journal": journal,
            "seen": seen,
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


@app.post("/band/{band_name}/note/{note_id}/edit")
async def edit_note(band_name: str, note_id: int, content: str = Form(...), session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    update_note(note_id, content)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.post("/band/{band_name}/note/{note_id}/delete")
async def delete_note_route(band_name: str, note_id: int, session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    delete_note(note_id)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.post("/band/{band_name}/photo/{photo_id}/edit")
async def edit_photo(band_name: str, photo_id: int, caption: str = Form(""), session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    update_photo_caption(photo_id, caption)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.post("/band/{band_name}/photo/{photo_id}/delete")
async def delete_photo_route(band_name: str, photo_id: int, session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    filename = delete_photo(photo_id)
    if filename:
        (PHOTOS_DIR / filename).unlink(missing_ok=True)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.post("/band/{band_name}/seen")
async def toggle_seen_route(band_name: str, session: str | None = Cookie(None)):
    if not is_authed(session):
        return RedirectResponse("/login", status_code=303)
    toggle_seen(band_name)
    return RedirectResponse(f"/band/{band_name}", status_code=303)


@app.get("/summary", response_class=HTMLResponse)
async def summary_page(request: Request, session: str | None = Cookie(None)):
    bands = load_bands()
    band_info = {b["band"]: b for b in bands}
    entries = get_summary()
    # attach schedule info and sort by day+time
    for e in entries:
        info = band_info.get(e["band"], {})
        e["day"] = info.get("day", "")
        e["stage"] = info.get("stage", "")
        e["time"] = info.get("time", "")
    day_order = ["Wednesday May 20, 2026", "Thursday May 21, 2026", "Friday May 22, 2026", "Saturday May 23, 2026", "Sunday May 24, 2026"]
    entries.sort(key=lambda e: (
        day_order.index(e["day"]) if e["day"] in day_order else 99,
        _parse_slot(e["time"]) or (9999, 9999),
    ))
    by_day: dict[str, list] = {}
    for e in entries:
        by_day.setdefault(e["day"] or "Unknown", []).append(e)
    return templates.TemplateResponse(
        request=request,
        name="summary.html",
        context={
            "days": list(by_day.items()),
            "total": len(entries),
            "authed": is_authed(session),
            "request": request,
        },
    )


@app.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request, session: str | None = Cookie(None)):
    bands = load_bands()
    picks = [b for b in bands if b.get("must_see") in ("0", "1")]

    by_day: dict[str, list] = {}
    for band in picks:
        by_day.setdefault(band.get("day", ""), []).append(band)

    for day_bands in by_day.values():
        day_bands.sort(key=lambda b: _parse_slot(b.get("time", "")) or (9999, 9999))

    conflict_map: dict[str, list[str]] = {}
    for day_bands in by_day.values():
        for i, b1 in enumerate(day_bands):
            s1 = _parse_slot(b1.get("time", ""))
            for b2 in day_bands[i + 1:]:
                s2 = _parse_slot(b2.get("time", ""))
                if _slots_overlap(s1, s2):
                    conflict_map.setdefault(b1["band"], []).append(b2["band"])
                    conflict_map.setdefault(b2["band"], []).append(b1["band"])

    sorted_days = sorted(by_day.items(), key=lambda x: day_sort_key({"day": x[0]}))
    has_journal = get_all_bands_with_entries()

    return templates.TemplateResponse(
        request=request,
        name="schedule.html",
        context={
            "days": sorted_days,
            "conflict_map": conflict_map,
            "has_journal": has_journal,
            "authed": is_authed(session),
            "request": request,
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
