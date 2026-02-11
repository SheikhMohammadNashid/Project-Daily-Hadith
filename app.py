import random
import sqlite3
from datetime import date
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db_utils import get_db_connection, init_db, row_to_hadith

app = FastAPI(title="Daily Hadith")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_daily_hadith() -> Dict[str, Any]:
    """
    Deterministic hadith based on today's date, using the database.
    """
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT COUNT(*) AS c FROM hadiths")
        count = cur.fetchone()["c"]
        if count == 0:
            raise RuntimeError("No hadiths found in database.")

        today_index = date.today().toordinal() % count
        cur = conn.execute(
            "SELECT * FROM hadiths ORDER BY id LIMIT 1 OFFSET ?",
            (today_index,),
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Failed to load daily hadith from database.")
        return row_to_hadith(row)
    finally:
        conn.close()


def get_random_hadith() -> Dict[str, Any]:
    """
    Random hadith from the database.
    """
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM hadiths ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("No hadiths found in database.")
        return row_to_hadith(row)
    finally:
        conn.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    hadith = get_daily_hadith()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "hadith": hadith,
        },
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
        },
    )


@app.get("/api/hadith")
async def api_hadith(mode: str = "daily"):
    """
    JSON API for the current hadith.

    - mode=daily (default): returns deterministic daily hadith
    - mode=random: returns a random hadith from the collection
    """
    mode = mode.lower()
    if mode not in {"daily", "random"}:
        mode = "daily"

    if mode == "random":
        return get_random_hadith()
    return get_daily_hadith()


@app.on_event("startup")
def on_startup() -> None:
    # When the API is running, we seed only a tiny sample if the DB is empty,
    # so the UI still works even if you have not run seed_hadiths.py yet.
    init_db(seed_if_empty=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
