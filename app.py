from datetime import date
import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Daily Hadith")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# In a real app you might load this from a database or API.
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


def get_daily_hadith() -> dict:
    return SAMPLE_HADITHS[get_daily_index()]


def get_random_hadith() -> dict:
    return random.choice(SAMPLE_HADITHS)


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
    if mode == "random":
        return get_random_hadith()
    return get_daily_hadith()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
