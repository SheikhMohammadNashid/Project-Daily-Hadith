# Project Hadith - Daily Hadith (FastAPI)

This is a minimal FastAPI project that serves a modern, glassmorphism-style **Daily Hadith** page.

The backend exposes:

- `/` – Renders the main Jinja2 template (`templates/index.html`) with the current daily hadith.
- `/api/hadith` – Returns the current daily hadith as JSON (useful for dynamic frontends or JS refresh).

## Setup

Create and activate a virtual environment (recommended), then install dependencies:

```bash
cd "/home/patcher/Documents/Python/virtual environment/Project Hadith"
pip install -r requirements.txt
```

## Running the app

You can run the app directly via `python`:

```bash
cd "/home/patcher/Documents/Python/virtual environment/Project Hadith"
python app.py
```

or with Uvicorn explicitly:

```bash
cd "/home/patcher/Documents/Python/virtual environment/Project Hadith"
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000/` in your browser.

## Customising the hadith

The sample hadiths are currently defined in `app.py` in the `SAMPLE_HADITHS` list. You can:

- Replace them with your own verified hadiths.
- Load them from a database or file instead of hardcoding.
- Implement rotation logic (daily, random, etc.) inside the `get_daily_hadith()` function.

Always ensure that any hadith text and references are checked against **reliable, authentic sources** before public use.

