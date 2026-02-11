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

## Customising the hadith (database-backed)

The app now stores hadith in a **SQLite database** instead of a Python list.

- The database file path defaults to `hadith.db` in the project root.
- You can override this with the `HADITH_DB_PATH` environment variable.
- On startup, the app ensures the `hadiths` table exists and seeds a **small sample set** if the table is empty.

For real use, you should replace the sample data with at least **500 verified hadith** from **Sahih al-Bukhari** and **Sahih Muslim**:

1. Prepare a `hadiths.csv` file in the project root with columns:
   - `collection` (e.g. `Sahih al-Bukhari`, `Sahih Muslim`)
   - `reference` (e.g. `Sahih al-Bukhari 1`, `Sahih Muslim 55`)
   - `arabic`
   - `translation`
   - `narrator`
2. Run the seed script:

```bash
python seed_hadiths.py
```

This will create `hadith.db` (if needed) and bulk-insert the records from `hadiths.csv`. The app then serves:

- A **daily hadith** (deterministic by date) from the database.
- A **random hadith** via `/api/hadith?mode=random`.

Always ensure that any hadith text and references are checked against **reliable, authentic sources** before public use.