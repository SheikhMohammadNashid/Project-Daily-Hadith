"""
Utility script to seed the SQLite database with hadith entries.

This script is intentionally minimal. For production use you should prepare
an authoritative CSV or JSON file containing at least 500 verified hadith
from Sahih al-Bukhari and Sahih Muslim, then adapt the `load_from_csv`
function below to ingest that dataset.
"""

import csv
import sqlite3
from pathlib import Path
from typing import Iterable, Mapping

from db_utils import HADITH_DB_PATH, get_db_connection, init_db


def load_from_csv(path: Path) -> Iterable[Mapping[str, str]]:
    """
    Load hadith records from a CSV file.

    Expected columns (logical mapping):
        collection, reference, arabic, translation, narrator

    The current Sahih al-Bukhari CSV has columns:
        Book, Chapter_Number, Chapter_Title_Arabic, Chapter_Title_English,
        Arabic_Text, English_Text, Grade, Reference, In-book reference
    We map these into the logical fields used by the app.
    """
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Collection: book name (e.g. "Sahih al-Bukhari")
            collection = (row.get("Book") or "").strip() or "Sahih al-Bukhari"

            # Reference: use the external reference (e.g. bukhari:1)
            reference = (row.get("Reference") or "").strip()

            # Arabic text and translation
            arabic = (row.get("Arabic_Text") or "").strip()
            translation = (row.get("English_Text") or "").strip()

            # Narrator: not provided as a dedicated column; keep generic.
            narrator = "Narrated in " + collection

            # Basic filtering: skip obviously empty rows
            if not arabic and not translation:
                continue

            yield {
                "collection": collection,
                "reference": reference or "Reference unavailable",
                "arabic": arabic,
                "translation": translation,
                "narrator": narrator,
            }


def bulk_insert(conn: sqlite3.Connection, rows: Iterable[Mapping[str, str]]) -> int:
    cursor = conn.executemany(
        """
        INSERT INTO hadiths (collection, reference, arabic, translation, narrator)
        VALUES (:collection, :reference, :arabic, :translation, :narrator)
        """,
        rows,
    )
    return cursor.rowcount or 0


def main() -> None:
    # For seeding from CSV we do NOT want to auto-seed the sample data.
    init_db(seed_if_empty=False)
    db_path = HADITH_DB_PATH

    # Adjust this path if you use a differently named CSV.
    # Here we default to the Sahih al-Bukhari CSV present in the repo.
    csv_path = Path("hadiths.csv")
    if not csv_path.exists():
        # Fallback to any known CSV in the directory (e.g. Sahih al-Bukhari.csv)
        for candidate in Path(".").glob("*.csv"):
            csv_path = candidate
            break

    if not csv_path.exists():
        print(
            f"[seed_hadiths] CSV file {csv_path} not found.\n"
            "Create hadiths.csv with at least 500 rows from Sahih al-Bukhari and "
            "Sahih Muslim (columns: collection,reference,arabic,translation,narrator) "
            "and rerun this script."
        )
        return

    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT COUNT(*) AS c FROM hadiths")
        existing = cur.fetchone()["c"]

        if existing > 0:
            print(
                f"[seed_hadiths] Database already contains {existing} hadiths. "
                "If you want to reset it, clear the table manually first."
            )
            return

        rows = list(load_from_csv(csv_path))
        inserted = bulk_insert(conn, rows)
        conn.commit()
        print(
            f"[seed_hadiths] Inserted {inserted} hadiths into {db_path}. "
            "Ensure your CSV contains at least 500 entries."
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()

