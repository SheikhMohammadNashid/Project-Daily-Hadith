import os
import random
from datetime import date
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Daily Hadith")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

HADITH_API_URL = os.getenv("HADITH_API_URL", "").rstrip("/")
HADITH_API_KEY = os.getenv("HADITH_API_KEY")


# Local fallback hadith list – still used if API is unavailable.
SAMPLE_HADITHS = [
    {
        "reference": "Sahih al-Bukhari 1",
        "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
        "translation": "Actions are judged by intentions.",
        "narrator": "Umar ibn al-Khattab (ra)",
        "collection": "Sahih al-Bukhari",
    },
    {
        "reference": "Sahih al-Bukhari 10",
        "arabic": "الدِّينُ النَّصِيحَةُ",
        "translation": "The religion is sincere advice.",
        "narrator": "Tamim ad-Dari (ra)",
        "collection": "Sahih al-Bukhari",
    },
    {
        "reference": "Sahih Muslim 55",
        "arabic": "لَا يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ",
        "translation": "None of you truly believes until he loves for his brother what he loves for himself.",
        "narrator": "Anas ibn Malik (ra)",
        "collection": "Sahih Muslim",
    },
    {
        "reference": "Sunan al-Tirmidhi 2516",
        "arabic": "مِنْ حُسْنِ إِسْلَامِ الْمَرْءِ تَرْكُهُ مَا لَا يَعْنِيهِ",
        "translation": "Part of a person’s good Islam is leaving that which does not concern him.",
        "narrator": "Abu Hurairah (ra)",
        "collection": "Jamiʿ at-Tirmidhi",
    },
]


def get_daily_index() -> int:
    """Deterministic index based on today's date, so the hadith is stable for the day."""
    today = date.today().toordinal()
    return today % len(SAMPLE_HADITHS)


def get_daily_hadith() -> Dict[str, Any]:
    return SAMPLE_HADITHS[get_daily_index()]


def get_random_hadith() -> Dict[str, Any]:
    return random.choice(SAMPLE_HADITHS)


def _normalize_external_hadith(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a hadith payload from an external API into the shape
    expected by the frontend.
    """
    # Try a few common key variants, but always provide safe defaults.
    reference = (
        payload.get("reference")
        or payload.get("ref")
        or payload.get("id")
        or "Hadith reference"
    )
    arabic = payload.get("arabic") or payload.get("text_ar") or payload.get("text") or ""
    translation = (
        payload.get("translation")
        or payload.get("text_en")
        or payload.get("translation_en")
        or ""
    )
    narrator = payload.get("narrator") or payload.get("rawi") or "Unknown"
    collection = payload.get("collection") or payload.get("book") or ""

    return {
        "reference": reference,
        "arabic": arabic,
        "translation": translation,
        "narrator": narrator,
        "collection": collection,
    }


async def fetch_hadith_from_api(mode: str = "daily") -> Optional[Dict[str, Any]]:
    """
    Fetch a hadith from an external API using an API key.

    - Uses HADITH_API_URL and HADITH_API_KEY from the environment.
    - Returns None if configuration is missing or any error occurs.
    """
    if not HADITH_API_URL or not HADITH_API_KEY:
        # External API not configured; caller should fallback to local list.
        return None

    url = HADITH_API_URL
    params = {"mode": mode}
    headers = {
        # The user requested a key-based retrieval; we send it as a Bearer token.
        "Authorization": f"Bearer {HADITH_API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        # Some APIs wrap the hadith inside a field like "data" or "hadith".
        if isinstance(data, dict):
            candidate = (
                data.get("hadith")
                or data.get("data")
                or data
            )
        else:
            candidate = data

        if isinstance(candidate, list) and candidate:
            # Take the first item if a list is returned.
            candidate = candidate[0]

        if not isinstance(candidate, dict):
            return None

        return _normalize_external_hadith(candidate)
    except Exception as exc:  # noqa: BLE001
        # In this minimal app we just log and quietly fall back to local data.
        print(f"[Daily Hadith] Failed to fetch from external API: {exc}")
        return None


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Prefer external API if configured; otherwise fall back to local list.
    hadith = await fetch_hadith_from_api(mode="daily") or get_daily_hadith()
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

    # Try the external API first if configured.
    external = await fetch_hadith_from_api(mode=mode)
    if external is not None:
        return external

    # Fallback to local list.
    if mode == "random":
        return get_random_hadith()
    return get_daily_hadith()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
