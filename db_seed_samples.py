import sqlite3
from typing import Any, Dict, List


def _sample_hadiths() -> List[Dict[str, Any]]:
    return [
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


def seed_sample_hadiths_if_needed(conn: sqlite3.Connection) -> None:
    """
    Insert a minimal sample set of hadith into the database if it is empty.

    This keeps the app usable even before you seed 500+ hadith via CSV.
    """
    cur = conn.execute("SELECT COUNT(*) AS c FROM hadiths")
    count = cur.fetchone()["c"]
    if count > 0:
        return

    conn.executemany(
        """
        INSERT INTO hadiths (collection, reference, arabic, translation, narrator)
        VALUES (:collection, :reference, :arabic, :translation, :narrator)
        """,
        _sample_hadiths(),
    )

