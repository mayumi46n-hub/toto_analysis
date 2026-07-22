# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data/toto.db"

CSV_PATH = (
    PROJECT_ROOT
    / "data/master/footystats_match_candidates_2026.csv"
)

SOURCE_TEAM_ID = 877
SOURCE_TEAM_NAME = "Avispa Fukuoka"
SEASON = 2026


def main() -> None:

    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    con = sqlite3.connect(DB_PATH)

    inserted = 0
    existing = 0

    try:

        with CSV_PATH.open(
            encoding="utf-8-sig",
            newline="",
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                source_url = row["url"].strip()

                exists = con.execute(
                    """
                    SELECT footystats_match_url_id
                    FROM footystats_match_urls
                    WHERE source_url=?
                    """,
                    (
                        source_url,
                    ),
                ).fetchone()

                if exists:
                    existing += 1
                    continue

                con.execute(
                    """
                    INSERT INTO footystats_match_urls (

                        season,

                        match_slug,

                        source_url,

                        source_team_id,

                        source_team_name

                    )
                    VALUES (
                        ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        SEASON,
                        row["match_slug"].strip(),
                        source_url,
                        SOURCE_TEAM_ID,
                        SOURCE_TEAM_NAME,
                    ),
                )

                inserted += 1

        con.commit()

        total = con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_urls
            """
        ).fetchone()[0]

        print("=" * 100)
        print("FootyStats Match URL Import")
        print("=" * 100)

        print(f"csv                : {CSV_PATH.relative_to(PROJECT_ROOT)}")
        print(f"database           : {DB_PATH.relative_to(PROJECT_ROOT)}")
        print(f"inserted           : {inserted}")
        print(f"already existing   : {existing}")
        print(f"total urls         : {total}")

        print()
        print("FIRST 10 URLS")
        print("-" * 100)

        rows = con.execute(
            """
            SELECT
                footystats_match_url_id,
                season,
                match_slug,
                download_status
            FROM footystats_match_urls
            ORDER BY footystats_match_url_id
            LIMIT 10
            """
        ).fetchall()

        for r in rows:
            print(r)

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
    