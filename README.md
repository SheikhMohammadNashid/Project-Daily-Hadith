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

## Using an external Hadith API

The app can optionally fetch hadith from an external API using an API key, and will fall back to the built‑in `SAMPLE_HADITHS` list if the API is unavailable or not configured.

Configure the following environment variables (locally or on your server/VM):

- `HADITH_API_URL` – Base URL of your hadith API endpoint that returns a hadith JSON.
- `HADITH_API_KEY` – API key used for authentication. The app sends this as a `Bearer` token via the `Authorization` header.

Example (local run):

```bash
export HADITH_API_URL="https://your-hadith-api.example.com/hadith"
export HADITH_API_KEY="YOUR_REAL_KEY_HERE"
uvicorn app:app --reload
```

When running via Docker Compose, `docker-compose.yml` is already wired to pass `HADITH_API_URL` and `HADITH_API_KEY` from the host environment into the container.