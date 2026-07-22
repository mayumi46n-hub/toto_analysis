# -*- coding: utf-8 -*-

"""
Project AKAMURASAKI

File:
    migrate_footystats_match_pages_v2.py

Purpose:
    footystats_match_pagesへ、試合日・ホーム／アウェイ・
    内部team_id・Jリーグ公式試合IDを保存する列を追加する。

Added columns:
    match_date
    home_team_name
    away_team_name
    home_external_team_id
    away_external_team_id
    home_team_id
    away_team_id
    jleague_match_id
    updated_at

Notes:
    - 既存データは保持する。
    - 既に存在する列は追加しない。
    - 再実行可能。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

TABLE_NAME = "footystats_match_pages"

COLUMNS: list[tuple[str, str]] = [
    (
        "match_date",
        "TEXT",
    ),
    (
        "home_team_name",
        "TEXT",
    ),
    (
        "away_team_name",
        "TEXT",
    ),
    (
        "home_external_team_id",
        "INTEGER",
    ),
    (
        "away_external_team_id",
        "INTEGER",
    ),
    (
        "home_team_id",
        "INTEGER",
    ),
    (
        "away_team_id",
        "INTEGER",
    ),
    (
        "jleague_match_id",
        "INTEGER",
    ),
    (
        "updated_at",
        "TEXT",
    ),
]


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")

    return con


def table_exists(
    con: sqlite3.Connection,
    table_name: str,
) -> bool:
    row = con.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def get_existing_columns(
    con: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    rows = con.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return {
        str(row[1])
        for row in rows
    }


def add_missing_columns(
    con: sqlite3.Connection,
) -> tuple[list[str], list[str]]:
    existing_columns = get_existing_columns(
        con,
        TABLE_NAME,
    )

    inserted: list[str] = []
    skipped: list[str] = []

    for column_name, column_type in COLUMNS:
        if column_name in existing_columns:
            skipped.append(column_name)
            continue

        con.execute(
            f"""
            ALTER TABLE {TABLE_NAME}
            ADD COLUMN {column_name} {column_type}
            """
        )

        inserted.append(column_name)

    return inserted, skipped


def create_indexes(
    con: sqlite3.Connection,
) -> None:
    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_footystats_match_pages_match_date
        ON footystats_match_pages (
            match_date
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_footystats_match_pages_external_teams
        ON footystats_match_pages (
            home_external_team_id,
            away_external_team_id
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_footystats_match_pages_internal_teams
        ON footystats_match_pages (
            home_team_id,
            away_team_id
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_footystats_match_pages_jleague_match
        ON footystats_match_pages (
            jleague_match_id
        )
        """
    )


def print_summary(
    inserted: list[str],
    skipped: list[str],
) -> None:
    print("=" * 100)
    print("FootyStats Match Pages V2 Migration")
    print("=" * 100)

    print(f"database         : {DB_PATH.relative_to(PROJECT_ROOT)}")
    print(f"table            : {TABLE_NAME}")
    print(f"columns inserted : {len(inserted)}")
    print(f"columns existing : {len(skipped)}")

    print()
    print("INSERTED")
    print("-" * 100)

    if inserted:
        for column_name in inserted:
            print(column_name)
    else:
        print("なし")

    print()
    print("ALREADY EXISTS")
    print("-" * 100)

    if skipped:
        for column_name in skipped:
            print(column_name)
    else:
        print("なし")


def main() -> None:
    con = connect_database()

    try:
        if not table_exists(
            con,
            TABLE_NAME,
        ):
            raise RuntimeError(
                f"テーブルが存在しません: {TABLE_NAME}"
            )

        inserted, skipped = add_missing_columns(
            con
        )

        create_indexes(
            con
        )

        con.commit()

        print_summary(
            inserted=inserted,
            skipped=skipped,
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
