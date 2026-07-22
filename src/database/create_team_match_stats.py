# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path


DB_PATH = Path("data/toto.db")


def create_team_match_stats(con: sqlite3.Connection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS team_match_stats (
            team_match_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

            jleague_match_id   INTEGER NOT NULL,
            team_id            INTEGER NOT NULL,
            opponent_team_id   INTEGER,
            source_name        TEXT NOT NULL,

            season             INTEGER NOT NULL,
            match_date         TEXT,
            venue_side         TEXT NOT NULL
                               CHECK (venue_side IN ('home', 'away')),

            goals_for          INTEGER,
            goals_against      INTEGER,

            shots              REAL,
            shots_on_target    REAL,
            possession         REAL,
            expected_goals     REAL,
            expected_goals_against REAL,

            corners            REAL,
            offsides           REAL,
            fouls              REAL,
            yellow_cards       REAL,
            red_cards          REAL,

            passes             REAL,
            pass_accuracy      REAL,
            crosses            REAL,

            tackles            REAL,
            interceptions      REAL,
            clearances         REAL,
            blocks             REAL,

            clean_sheet        INTEGER
                               CHECK (
                                   clean_sheet IS NULL
                                   OR clean_sheet IN (0, 1)
                               ),

            failed_to_score    INTEGER
                               CHECK (
                                   failed_to_score IS NULL
                                   OR failed_to_score IN (0, 1)
                               ),

            btts               INTEGER
                               CHECK (
                                   btts IS NULL
                                   OR btts IN (0, 1)
                               ),

            source_url         TEXT,
            fetched_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at         TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (jleague_match_id)
                REFERENCES jleague_matches(jleague_match_id),

            FOREIGN KEY (team_id)
                REFERENCES team_master(team_id),

            FOREIGN KEY (opponent_team_id)
                REFERENCES team_master(team_id),

            UNIQUE (
                jleague_match_id,
                team_id,
                source_name
            )
        )
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS
            idx_team_match_stats_match
        ON team_match_stats(jleague_match_id)
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS
            idx_team_match_stats_team_season
        ON team_match_stats(team_id, season)
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS
            idx_team_match_stats_source
        ON team_match_stats(source_name)
    """)


def print_summary(con: sqlite3.Connection) -> None:
    columns = con.execute("""
        PRAGMA table_info(team_match_stats)
    """).fetchall()

    print("=" * 80)
    print("team_match_stats created")
    print("=" * 80)
    print(f"カラム数: {len(columns)}")
    print()

    for column in columns:
        print(
            f"{column[1]:<30}"
            f"{column[2]:<15}"
            f"{'PK' if column[5] else ''}"
        )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        con.execute("PRAGMA foreign_keys = ON")

        create_team_match_stats(con)
        con.commit()

        print_summary(con)

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
