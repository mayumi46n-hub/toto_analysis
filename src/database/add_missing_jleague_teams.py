# -*- coding: utf-8 -*-

"""
totoLABO

File:
    add_missing_jleague_teams.py

Version:
    1.0

Updated:
    2026-07-16

Purpose:
    jleague_matches に存在するが team_alias_v2 で解決できない
    Jリーグクラブを team_master に追加し、名称を team_id に接続する。

Notes:
    - セレッソ大阪は既存の short_name='C大阪' に接続する。
    - 草津は暫定的に short_name='群馬' の別名として接続する。
    - 正式名称や歴史的名称は、将来の club_history で精査する。
"""

import sqlite3
from pathlib import Path


DB_PATH = Path("data/toto.db")


NEW_TEAMS = [
    "北九州",
    "山口",
    "山形",
    "岐阜",
    "岩手",
    "愛媛",
    "新潟",
    "松本",
    "栃木",
    "湘南",
    "熊本",
    "相模原",
    "群馬",
    "讃岐",
    "金沢",
    "鹿児島",
]


ALIASES = {
    # 既存チーム
    "セレッソ大阪": "Ｃ大阪",

    # 新規追加チームの正式・長形式名称
    "ギラヴァンツ北九州": "北九州",
    "レノファ山口ＦＣ": "山口",
    "モンテディオ山形": "山形",
    "ＦＣ岐阜": "岐阜",
    "いわてグルージャ盛岡": "岩手",
    "アルビレックス新潟": "新潟",
    "松本山雅ＦＣ": "松本",
    "栃木ＳＣ": "栃木",
    "湘南ベルマーレ": "湘南",
    "ロアッソ熊本": "熊本",
    "ＳＣ相模原": "相模原",
    "ザスパクサツ群馬": "群馬",
    "ザスパ草津": "群馬",
    "草津": "群馬",
    "カマタマーレ讃岐": "讃岐",
    "ツエーゲン金沢": "金沢",
    "鹿児島ユナイテッドＦＣ": "鹿児島",
}


def get_team_id(
    con: sqlite3.Connection,
    short_name: str,
) -> int:
    row = con.execute(
        """
        SELECT team_id
        FROM team_master
        WHERE short_name = ?
        """,
        (short_name,),
    ).fetchone()

    if row is None:
        raise ValueError(
            f"team_masterに存在しません: {short_name}"
        )

    return int(row[0])


def insert_new_teams(
    con: sqlite3.Connection,
) -> tuple[int, int]:
    inserted = 0
    existing = 0

    for short_name in NEW_TEAMS:
        row = con.execute(
            """
            SELECT team_id
            FROM team_master
            WHERE short_name = ?
            """,
            (short_name,),
        ).fetchone()

        if row is not None:
            existing += 1
            continue

        con.execute(
            """
            INSERT INTO team_master (
                short_name,
                category
            )
            VALUES (?, 'club')
            """,
            (short_name,),
        )

        inserted += 1

    return inserted, existing


def insert_canonical_aliases(
    con: sqlite3.Connection,
) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    for short_name in NEW_TEAMS:
        team_id = get_team_id(con, short_name)

        cursor = con.execute(
            """
            INSERT OR IGNORE INTO team_alias_v2 (
                alias_name,
                team_id,
                source_name
            )
            VALUES (?, ?, 'team_master')
            """,
            (
                short_name,
                team_id,
            ),
        )

        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped


def insert_aliases(
    con: sqlite3.Connection,
) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    for alias_name, canonical_short_name in ALIASES.items():
        team_id = get_team_id(
            con,
            canonical_short_name,
        )

        cursor = con.execute(
            """
            INSERT OR IGNORE INTO team_alias_v2 (
                alias_name,
                team_id,
                source_name
            )
            VALUES (?, ?, 'manual_jleague')
            """,
            (
                alias_name,
                team_id,
            ),
        )

        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped


def find_unresolved_match_teams(
    con: sqlite3.Connection,
) -> list[str]:
    rows = con.execute(
        """
        WITH match_teams AS (
            SELECT home_team AS team_name
            FROM jleague_matches

            UNION

            SELECT away_team AS team_name
            FROM jleague_matches
        )
        SELECT mt.team_name
        FROM match_teams AS mt
        LEFT JOIN team_alias_v2 AS tav
          ON tav.alias_name = mt.team_name
        WHERE tav.team_id IS NULL
        ORDER BY mt.team_name
        """
    ).fetchall()

    return [
        str(row[0])
        for row in rows
    ]


def print_summary(
    con: sqlite3.Connection,
    team_inserted: int,
    team_existing: int,
    canonical_inserted: int,
    canonical_skipped: int,
    alias_inserted: int,
    alias_skipped: int,
) -> None:
    team_total = con.execute(
        """
        SELECT COUNT(*)
        FROM team_master
        """
    ).fetchone()[0]

    alias_total = con.execute(
        """
        SELECT COUNT(*)
        FROM team_alias_v2
        """
    ).fetchone()[0]

    unresolved = find_unresolved_match_teams(con)

    print("=" * 80)
    print("Missing J.League Team Registration")
    print("=" * 80)

    print(f"team_master inserted       : {team_inserted}")
    print(f"team_master already exists : {team_existing}")
    print(f"canonical alias inserted   : {canonical_inserted}")
    print(f"canonical alias skipped    : {canonical_skipped}")
    print(f"additional alias inserted  : {alias_inserted}")
    print(f"additional alias skipped   : {alias_skipped}")

    print()
    print(f"team_master total          : {team_total}")
    print(f"team_alias_v2 total        : {alias_total}")
    print(f"unresolved match teams     : {len(unresolved)}")

    print()
    print("UNRESOLVED MATCH TEAMS")
    print("-" * 80)

    if not unresolved:
        print("OK - All match team names resolved.")
    else:
        for team_name in unresolved:
            print(team_name)

    print()
    print("NEW TEAM SAMPLE")
    print("-" * 80)

    placeholders = ",".join(
        "?"
        for _ in NEW_TEAMS
    )

    rows = con.execute(
        f"""
        SELECT
            team_id,
            short_name,
            category
        FROM team_master
        WHERE short_name IN ({placeholders})
        ORDER BY team_id
        """,
        NEW_TEAMS,
    ).fetchall()

    for team_id, short_name, category in rows:
        print(
            f"team_id={team_id:<4}"
            f"{short_name:<12}"
            f"category={category}"
        )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        con.execute("PRAGMA foreign_keys = ON")

        team_inserted, team_existing = (
            insert_new_teams(con)
        )

        canonical_inserted, canonical_skipped = (
            insert_canonical_aliases(con)
        )

        alias_inserted, alias_skipped = (
            insert_aliases(con)
        )

        con.commit()

        print_summary(
            con=con,
            team_inserted=team_inserted,
            team_existing=team_existing,
            canonical_inserted=canonical_inserted,
            canonical_skipped=canonical_skipped,
            alias_inserted=alias_inserted,
            alias_skipped=alias_skipped,
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
