# -*- coding: utf-8 -*-

"""
Project AKAMURASAKI

File:
    import_team_alias.py

Purpose:
    team_alias.csv を SQLite に取り込む

Author:
    Project AKAMURASAKI
"""

from pathlib import Path
import sqlite3
import csv

DB_PATH = Path("data/toto.db")
CSV_PATH = Path("data/master/team_alias.csv")


def main():

    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    con = sqlite3.connect(DB_PATH)

    inserted = 0
    skipped = 0

    with open(CSV_PATH, encoding="utf-8-sig") as f:

        reader = csv.DictReader(f)

        for row in reader:

            alias = row["alias_name"].strip()
            official = row["official_name"].strip()

            cur = con.execute(
                """
                INSERT OR IGNORE INTO team_alias
                (
                    alias_name,
                    official_name
                )
                VALUES (?, ?)
                """,
                (
                    alias,
                    official,
                ),
            )

            if cur.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

    con.commit()

    print("=" * 80)
    print("team_alias Import")
    print("=" * 80)

    print(f"Inserted : {inserted}")
    print(f"Skipped  : {skipped}")
    print()

    rows = con.execute(
        """
        SELECT
            alias_name,
            official_name
        FROM team_alias
        ORDER BY alias_name
        """
    ).fetchall()

    print(f"Total Rows : {len(rows)}")
    print()

    for alias, official in rows:
        print(f"{alias:<30} -> {official}")

    con.close()


if __name__ == "__main__":
    main()
