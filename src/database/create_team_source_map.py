# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path


DB_PATH = Path("data/toto.db")


def create_team_source_map(con: sqlite3.Connection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS team_source_map (
            team_source_map_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id            INTEGER NOT NULL,
            source_name        TEXT NOT NULL,
            external_team_id   TEXT,
            external_name      TEXT NOT NULL,
            source_url         TEXT,
            is_primary         INTEGER NOT NULL DEFAULT 0
                               CHECK (is_primary IN (0, 1)),
            created_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (team_id)
                REFERENCES team_master(team_id),

            UNIQUE (
                source_name,
                external_name
            )
        )
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS
            idx_team_source_map_team_id
        ON team_source_map(team_id)
    """)

    con.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
            idx_team_source_external_id
        ON team_source_map(
            source_name,
            external_team_id
        )
        WHERE external_team_id IS NOT NULL
    """)


def seed_existing_names(con: sqlite3.Connection) -> None:
    con.execute("""
        INSERT OR IGNORE INTO team_source_map (
            team_id,
            source_name,
            external_name,
            is_primary
        )
        SELECT
            team_id,
            'toto',
            short_name,
            1
        FROM team_master
        WHERE short_name IS NOT NULL
          AND TRIM(short_name) <> ''
    """)

    con.execute("""
        INSERT OR IGNORE INTO team_source_map (
            team_id,
            source_name,
            external_name,
            is_primary
        )
        SELECT
            team_id,
            'team_master',
            full_name,
            1
        FROM team_master
        WHERE full_name IS NOT NULL
          AND TRIM(full_name) <> ''
    """)


def print_summary(con: sqlite3.Connection) -> None:
    count = con.execute("""
        SELECT COUNT(*)
        FROM team_source_map
    """).fetchone()[0]

    print("=" * 80)
    print("team_source_map created")
    print("=" * 80)
    print(f"登録件数: {count}")
    print()

    rows = con.execute("""
        SELECT
            tsm.team_id,
            tm.short_name,
            tsm.source_name,
            tsm.external_team_id,
            tsm.external_name
        FROM team_source_map AS tsm
        JOIN team_master AS tm
          ON tm.team_id = tsm.team_id
        ORDER BY
            tsm.team_id,
            tsm.source_name
        LIMIT 20
    """).fetchall()

    for row in rows:
        print(row)


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        con.execute("PRAGMA foreign_keys = ON")

        create_team_source_map(con)
        seed_existing_names(con)

        con.commit()

        print_summary(con)

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
