#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

DEFAULT_DB_PATH = Path("data/toto.db")
DEFAULT_SEASON = 2025
SOURCE_NAME = "footystats"

QUERY = """
WITH season_teams AS (
    SELECT
        tm.team_id AS team_id,
        tm.short_name AS short_name
    FROM jleague_matches AS jm
    JOIN team_alias_v2 AS ta
      ON ta.alias_name = jm.home_team
    JOIN team_master AS tm
      ON tm.team_id = ta.team_id
    WHERE jm.season = ?

    UNION

    SELECT
        tm.team_id AS team_id,
        tm.short_name AS short_name
    FROM jleague_matches AS jm
    JOIN team_alias_v2 AS ta
      ON ta.alias_name = jm.away_team
    JOIN team_master AS tm
      ON tm.team_id = ta.team_id
    WHERE jm.season = ?
)
SELECT
    st.team_id,
    st.short_name,
    tsm.external_team_id,
    tsm.external_name,
    tsm.source_url,
    CASE
        WHEN tsm.team_source_map_id IS NULL THEN 'MISSING'
        ELSE 'MAPPED'
    END AS mapping_status
FROM season_teams AS st
LEFT JOIN team_source_map AS tsm
  ON tsm.team_id = st.team_id
 AND lower(tsm.source_name) = lower(?)
ORDER BY
    CASE
        WHEN tsm.team_source_map_id IS NULL THEN 0
        ELSE 1
    END,
    st.team_id
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "指定シーズンのJリーグ参加クラブとFootyStatsの"
            "team_source_map登録状況を確認します。"
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
        help=f"対象シーズン (default: {DEFAULT_SEASON})",
    )
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="未登録クラブだけ表示します。",
    )
    return parser.parse_args()


def validate_database(con: sqlite3.Connection) -> None:
    required_tables = {
        "jleague_matches",
        "team_alias_v2",
        "team_master",
        "team_source_map",
    }

    existing = {
        row[0]
        for row in con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )
    }

    missing_tables = sorted(required_tables - existing)
    if missing_tables:
        raise RuntimeError(
            "必要なテーブルがありません: " + ", ".join(missing_tables)
        )


def fetch_rows(
    con: sqlite3.Connection,
    season: int,
) -> list[sqlite3.Row]:
    con.row_factory = sqlite3.Row
    return con.execute(
        QUERY,
        (season, season, SOURCE_NAME),
    ).fetchall()


def print_table(
    title: str,
    rows: Sequence[sqlite3.Row],
    include_mapping: bool,
) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)

    if not rows:
        print("(none)")
        return

    for row in rows:
        team_id = row["team_id"]
        short_name = row["short_name"]

        if not include_mapping:
            print(f"{team_id:>4}  {short_name}")
            continue

        external_team_id = row["external_team_id"] or "-"
        external_name = row["external_name"] or "-"
        source_url = row["source_url"] or "-"

        print(
            f"{team_id:>4}  "
            f"{short_name:<16}  "
            f"external_id={external_team_id:<8}  "
            f"external_name={external_name}"
        )
        print(f"      {source_url}")


def main() -> int:
    args = parse_args()
    db_path = args.db.expanduser().resolve()

    if not db_path.exists():
        print(
            f"ERROR: database not found: {db_path}",
            file=sys.stderr,
        )
        return 1

    try:
        with sqlite3.connect(db_path) as con:
            validate_database(con)
            rows = fetch_rows(con, args.season)

    except sqlite3.Error as exc:
        print(f"SQLite error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    mapped = [
        row
        for row in rows
        if row["mapping_status"] == "MAPPED"
    ]
    missing = [
        row
        for row in rows
        if row["mapping_status"] == "MISSING"
    ]

    print("=" * 120)
    print("FootyStats team mapping check")
    print("=" * 120)
    print(f"database : {db_path}")
    print(f"season   : {args.season}")
    print(f"source   : {SOURCE_NAME}")
    print("-" * 120)
    print(f"TOTAL    : {len(rows)}")
    print(f"MAPPED   : {len(mapped)}")
    print(f"MISSING  : {len(missing)}")

    print_table(
        title="MISSING TEAMS",
        rows=missing,
        include_mapping=False,
    )

    if not args.missing_only:
        print_table(
            title="MAPPED TEAMS",
            rows=mapped,
            include_mapping=True,
        )

    print()
    if not rows:
        print(
            f"WARNING: season={args.season} の参加クラブを取得できませんでした。"
        )
        return 2

    if missing:
        print(
            f"RESULT: {len(missing)} club(s) still need "
            "FootyStats mapping."
        )
        return 3

    print("RESULT: all participating clubs are mapped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
