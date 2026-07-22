# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS footystats_match_urls (
    footystats_match_url_id INTEGER PRIMARY KEY AUTOINCREMENT,

    season INTEGER,
    match_slug TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,

    source_team_id INTEGER,
    source_team_name TEXT,

    html_path TEXT,
    json_path TEXT,

    download_status TEXT NOT NULL DEFAULT 'pending',
    parse_status TEXT NOT NULL DEFAULT 'pending',
    import_status TEXT NOT NULL DEFAULT 'pending',
    link_status TEXT NOT NULL DEFAULT 'pending',

    footystats_page_id INTEGER,
    jleague_match_id INTEGER,

    last_error TEXT,

    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    downloaded_at TEXT,
    parsed_at TEXT,
    imported_at TEXT,
    linked_at TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


INDEX_SQLS = (
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_season
    ON footystats_match_urls (
        season
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_download_status
    ON footystats_match_urls (
        download_status
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_parse_status
    ON footystats_match_urls (
        parse_status
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_import_status
    ON footystats_match_urls (
        import_status
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_link_status
    ON footystats_match_urls (
        link_status
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_footystats_match_urls_jleague_match_id
    ON footystats_match_urls (
        jleague_match_id
    )
    """,
)


def table_columns(
    con: sqlite3.Connection,
) -> list[str]:
    rows = con.execute(
        """
        PRAGMA table_info(
            footystats_match_urls
        )
        """
    ).fetchall()

    return [
        str(row[1])
        for row in rows
    ]


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        con.execute(CREATE_TABLE_SQL)

        for sql in INDEX_SQLS:
            con.execute(sql)

        con.commit()

        columns = table_columns(con)

        print("=" * 100)
        print("FootyStats Match URL Table")
        print("=" * 100)
        print(
            "database : "
            f"{DB_PATH.relative_to(PROJECT_ROOT)}"
        )
        print(
            "table    : footystats_match_urls"
        )
        print(
            f"columns  : {len(columns)}"
        )

        print()
        print("COLUMN LIST")
        print("-" * 100)

        for column in columns:
            print(column)

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()