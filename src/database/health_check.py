# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path


DB_PATH = Path("data/toto.db")


def header(title: str):
    print("=" * 80)
    print(title)
    print("=" * 80)


def count_table(con, table):
    cnt = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table:<30} {cnt:>8}")


def check_missing_teams(con):

    header("Missing Teams")

    sql = """
    SELECT DISTINCT team_name
    FROM (

        SELECT home_team AS team_name
        FROM jleague_matches

        UNION

        SELECT away_team
        FROM jleague_matches

    )

    EXCEPT

    SELECT short_name
    FROM team_master

    ORDER BY team_name
    """

    rows = con.execute(sql).fetchall()

    if not rows:
        print("OK")
        return

    print(f"{len(rows)} team(s) missing\n")

    for row in rows:
        print(row[0])


def main():

    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    con = sqlite3.connect(DB_PATH)

    header("Project AKAMURASAKI Database Health Check")

    print()

    count_table(con, "team_master")
    count_table(con, "team_source_map")
    count_table(con, "jleague_matches")
    count_table(con, "match_elo")
    count_table(con, "match_features_season")
    count_table(con, "team_match_stats")

    print()

    check_missing_teams(con)

    con.close()


if __name__ == "__main__":
    main()
