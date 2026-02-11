import os
import sqlite3
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
HADITH_DB_PATH = Path(os.getenv("HADITH_DB_PATH", BASE_DIR / "hadith.db"))


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(HADITH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed_if_empty: bool = False) -> None:
    """
    Initialise the SQLite database and ensure the hadiths table exists.
    Optionally seed a small sample set if empty.
    """
    from db_seed_samples import seed_sample_hadiths_if_needed  # local import to avoid cycles

    HADITH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS hadiths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection TEXT NOT NULL,
                reference TEXT NOT NULL,
                arabic TEXT NOT NULL,
                translation TEXT NOT NULL,
                narrator TEXT NOT NULL
            )
            """
        )

        if seed_if_empty:
            seed_sample_hadiths_if_needed(conn)
    finally:
        conn.commit()
        conn.close()


def row_to_hadith(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "reference": row["reference"],
        "arabic": row["arabic"],
        "translation": row["translation"],
        "narrator": row["narrator"],
        "collection": row["collection"],
    }

