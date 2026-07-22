# -*- coding: utf-8 -*-

"""
totoLABO

File:
    migrate_team_alias_v2.py

Version:
    1.0

Purpose:
    文字列同士を結ぶ旧 team_alias から、
    alias_name を直接 team_id へ結ぶ team_alias_v2 を作成する。
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("data/toto.db")


def create_team_alias_v2(con: sqlite3.Connection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS team_alias_v2 (
            alias_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            alias_name     TEXT NOT NULL UNIQUE,
            team_id        INTEGER NOT NULL,
            source_name    TEXT,
            created_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (team_id)
                REFERENCES team_master(team_id)
        )
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS
            idx_team_alias_v2_team_id
        ON team_alias_v2(team_id)
    """)


def seed_short_names(con: sqlite3.Connection) -> int:
    cursor = con.execute("""
        INSERT OR IGNORE INTO team_alias_v2 (
            alias_name,
            team_id,
            source_name
        )
        SELECT
            short_name,
            team_id,
            'team_master'
        FROM team_master
        WHERE short_name IS NOT NULL
          AND TRIM(short_name) <> ''
    """)

    return cursor.rowcount


def seed_full_names(con: sqlite3.Connection) -> int:
    cursor = con.execute("""
        INSERT OR IGNORE INTO team_alias_v2 (
            alias_name,
            team_id,
            source_name
        )
        SELECT
            full_name,
            team_id,
            'team_master'
        FROM team_master
        WHERE full_name IS NOT NULL
          AND TRIM(full_name) <> ''
    """)

    return cursor.rowcount


def migrate_resolvable_legacy_aliases(
    con: sqlite3.Connection,
) -> int:
    cursor = con.execute("""
        INSERT OR IGNORE INTO team_alias_v2 (
            alias_name,
            team_id,
            source_name
        )
        SELECT
            ta.alias_name,
            tm.team_id,
            'legacy_team_alias'
        FROM team_alias AS ta
        JOIN team_master AS tm
          ON tm.short_name = ta.official_name
          OR tm.full_name = ta.official_name
        WHERE ta.alias_name IS NOT NULL
          AND TRIM(ta.alias_name) <> ''
    """)

    return cursor.rowcount


def print_summary(con: sqlite3.Connection) -> None:
    total = con.execute("""
        SELECT COUNT(*)
        FROM team_alias_v2
    """).fetchone()[0]

    unresolved = con.execute("""
        SELECT
            ta.alias_name,
            ta.official_name
        FROM team_alias AS ta
        WHERE NOT EXISTS (
            SELECT 1
            FROM team_master AS tm
            WHERE tm.short_name = ta.official_name
               OR tm.full_name = ta.official_name
        )
        ORDER BY ta.alias_name
    """).fetchall()

    print("=" * 80)
    print("team_alias_v2 Migration")
    print("=" * 80)
    print(f"team_alias_v2 total : {total}")
    print(f"legacy unresolved   : {len(unresolved)}")
    print()

    print("UNRESOLVED LEGACY ALIASES")
    print("-" * 80)

    if not unresolved:
        print("None")
    else:
        for alias_name, official_name in unresolved:
            print(
                f"{alias_name:<30}"
                f" -> {official_name}"
            )

    print()
    print("SAMPLE")
    print("-" * 80)

    rows = con.execute("""
        SELECT
            tav.alias_name,
            tav.team_id,
            tm.short_name,
            tav.source_name
        FROM team_alias_v2 AS tav
        JOIN team_master AS tm
          ON tm.team_id = tav.team_id
        ORDER BY
            tav.team_id,
            tav.alias_name
        LIMIT 30
    """).fetchall()

    for alias_name, team_id, short_name, source_name in rows:
        print(
            f"{alias_name:<30}"
            f" -> team_id={team_id:<4}"
            f"{short_name:<12}"
            f"[{source_name}]"
        )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        con.execute("PRAGMA foreign_keys = ON")

        create_team_alias_v2(con)

        short_inserted = seed_short_names(con)
        full_inserted = seed_full_names(con)
        legacy_inserted = migrate_resolvable_legacy_aliases(con)

        con.commit()

        print(f"short_name inserted : {short_inserted}")
        print(f"full_name inserted  : {full_inserted}")
        print(f"legacy inserted     : {legacy_inserted}")
        print()

        print_summary(con)

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
