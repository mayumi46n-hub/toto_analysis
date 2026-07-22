# -*- coding: utf-8 -*-

"""
totoLABO

File:
    import_footystats_team.py

Version:
    1.0

Updated:
    2026-07-18

Purpose:
    保存済みFootyStatsクラブHTMLを解析し、次をSQLiteへ保存する。

    1. team_alias_v2
       FootyStats上のチーム名から内部team_idへの対応

    2. team_source_map
       FootyStats固有チームIDから内部team_idへの対応

    3. footystats_match_schedule_raw
       FootyStatsに埋め込まれた試合日程の未加工データ

Important:
    このHTMLにある試合は未来の日程であり、
    試合後スタッツではない。

    jleague_match_idとの照合が完了するまでは、
    team_match_statsへ登録しない。
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.parsers.parse_footystats_team import (  # noqa: E402
    build_result,
    read_html,
)


DB_PATH = PROJECT_ROOT / "data/toto.db"

DEFAULT_HTML_PATH = (
    PROJECT_ROOT
    / "data/raw/footystats/2026/avispa_fukuoka_877.html"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStatsクラブHTMLを"
            "totoLABOデータベースへ取り込みます。"
        )
    )

    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help=(
            "保存済みFootyStats HTMLのパス。"
            f"省略時: {DEFAULT_HTML_PATH}"
        ),
    )

    parser.add_argument(
        "--team-id",
        type=int,
        required=True,
        help=(
            "totoLABO内部のteam_master.team_id。"
            "アビスパ福岡は31。"
        ),
    )

    return parser.parse_args()


def resolve_path(
    path: Path,
) -> Path:
    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute(
        "PRAGMA foreign_keys = ON"
    )

    return con


def validate_team_id(
    con: sqlite3.Connection,
    team_id: int,
) -> str:
    row = con.execute(
        """
        SELECT short_name
        FROM team_master
        WHERE team_id = ?
        """,
        (team_id,),
    ).fetchone()

    if row is None:
        raise ValueError(
            "team_masterに存在しないteam_idです: "
            f"{team_id}"
        )

    return str(row[0])


def create_raw_schedule_table(
    con: sqlite3.Connection,
) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS
            footystats_match_schedule_raw
        (
            footystats_match_id       INTEGER PRIMARY KEY,

            subject_team_id           INTEGER NOT NULL,
            subject_external_team_id  TEXT NOT NULL,

            home_external_team_id     TEXT NOT NULL,
            away_external_team_id     TEXT NOT NULL,

            team_side                 TEXT,
            status                    TEXT,

            scheduled_at_unix         INTEGER,
            scheduled_at_utc          TEXT,

            match_winner              INTEGER,

            source_file               TEXT NOT NULL,
            source_url                TEXT,

            imported_at               TEXT NOT NULL
                                      DEFAULT CURRENT_TIMESTAMP,
            updated_at                TEXT NOT NULL
                                      DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (
                subject_team_id
            )
                REFERENCES team_master(team_id),

            CHECK (
                team_side IS NULL
                OR team_side IN ('home', 'away')
            )
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
            idx_footystats_schedule_subject
        ON footystats_match_schedule_raw(
            subject_team_id
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
            idx_footystats_schedule_date
        ON footystats_match_schedule_raw(
            scheduled_at_unix
        )
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS
            idx_footystats_schedule_home_away
        ON footystats_match_schedule_raw(
            home_external_team_id,
            away_external_team_id
        )
        """
    )


def upsert_team_alias(
    con: sqlite3.Connection,
    alias_name: str,
    team_id: int,
) -> str:
    existing = con.execute(
        """
        SELECT team_id
        FROM team_alias_v2
        WHERE alias_name = ?
        """,
        (alias_name,),
    ).fetchone()

    if existing is not None:
        existing_team_id = int(
            existing[0]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "team_alias_v2の既存対応と"
                "指定team_idが一致しません: "
                f"{alias_name} -> "
                f"{existing_team_id}, "
                f"指定={team_id}"
            )

        return "existing"

    con.execute(
        """
        INSERT INTO team_alias_v2 (
            alias_name,
            team_id,
            source_name
        )
        VALUES (?, ?, 'footystats')
        """,
        (
            alias_name,
            team_id,
        ),
    )

    return "inserted"


def upsert_team_source_map(
    con: sqlite3.Connection,
    team_id: int,
    external_team_id: int,
    external_name: str,
    source_url: str,
) -> str:
    external_id_text = str(
        external_team_id
    )

    existing = con.execute(
        """
        SELECT
            team_source_map_id,
            team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND external_team_id = ?
        """,
        (external_id_text,),
    ).fetchone()

    if existing is not None:
        map_id = int(
            existing[0]
        )
        existing_team_id = int(
            existing[1]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "team_source_mapの既存対応と"
                "指定team_idが一致しません: "
                f"footystats:{external_team_id} "
                f"-> {existing_team_id}, "
                f"指定={team_id}"
            )

        con.execute(
            """
            UPDATE team_source_map
            SET
                external_name = ?,
                source_url = ?,
                is_primary = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE team_source_map_id = ?
            """,
            (
                external_name,
                source_url,
                map_id,
            ),
        )

        return "updated"

    con.execute(
        """
        INSERT INTO team_source_map (
            team_id,
            source_name,
            external_team_id,
            external_name,
            source_url,
            is_primary
        )
        VALUES (
            ?,
            'footystats',
            ?,
            ?,
            ?,
            1
        )
        """,
        (
            team_id,
            external_id_text,
            external_name,
            source_url,
        ),
    )

    return "inserted"


def upsert_schedule_match(
    con: sqlite3.Connection,
    team_id: int,
    subject_external_team_id: int,
    source_file: str,
    source_url: str,
    match: dict[str, Any],
) -> str:
    external_match_id = match.get(
        "footystats_match_id"
    )

    home_external_id = match.get(
        "home_team_external_id"
    )

    away_external_id = match.get(
        "away_team_external_id"
    )

    if external_match_id is None:
        raise ValueError(
            "footystats_match_idがありません"
        )

    if home_external_id is None:
        raise ValueError(
            "home_team_external_idがありません: "
            f"match={external_match_id}"
        )

    if away_external_id is None:
        raise ValueError(
            "away_team_external_idがありません: "
            f"match={external_match_id}"
        )

    exists = con.execute(
        """
        SELECT 1
        FROM footystats_match_schedule_raw
        WHERE footystats_match_id = ?
        """,
        (external_match_id,),
    ).fetchone()

    con.execute(
        """
        INSERT INTO footystats_match_schedule_raw (
            footystats_match_id,
            subject_team_id,
            subject_external_team_id,
            home_external_team_id,
            away_external_team_id,
            team_side,
            status,
            scheduled_at_unix,
            scheduled_at_utc,
            match_winner,
            source_file,
            source_url,
            updated_at
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT(footystats_match_id)
        DO UPDATE SET
            subject_team_id =
                excluded.subject_team_id,

            subject_external_team_id =
                excluded.subject_external_team_id,

            home_external_team_id =
                excluded.home_external_team_id,

            away_external_team_id =
                excluded.away_external_team_id,

            team_side =
                excluded.team_side,

            status =
                excluded.status,

            scheduled_at_unix =
                excluded.scheduled_at_unix,

            scheduled_at_utc =
                excluded.scheduled_at_utc,

            match_winner =
                excluded.match_winner,

            source_file =
                excluded.source_file,

            source_url =
                excluded.source_url,

            updated_at =
                CURRENT_TIMESTAMP
        """,
        (
            external_match_id,
            team_id,
            str(subject_external_team_id),
            str(home_external_id),
            str(away_external_id),
            match.get("team_side"),
            match.get("status"),
            match.get("scheduled_at_unix"),
            match.get("scheduled_at_utc"),
            match.get("match_winner"),
            source_file,
            source_url,
        ),
    )

    if exists is None:
        return "inserted"

    return "updated"


def print_summary(
    team_id: int,
    short_name: str,
    result: dict[str, Any],
    alias_status: str,
    source_map_status: str,
    inserted: int,
    updated: int,
    total_rows: int,
) -> None:
    print("=" * 100)
    print(
        "FootyStats Team Import"
    )
    print("=" * 100)

    print(
        f"internal team_id       : "
        f"{team_id}"
    )
    print(
        f"internal short_name    : "
        f"{short_name}"
    )
    print(
        f"footystats team_name   : "
        f"{result['team_name']}"
    )
    print(
        f"footystats team_id     : "
        f"{result['footystats_team_id']}"
    )
    print(
        f"season                 : "
        f"{result['season_label']}"
    )
    print(
        f"alias status           : "
        f"{alias_status}"
    )
    print(
        f"source map status      : "
        f"{source_map_status}"
    )
    print(
        f"schedule inserted      : "
        f"{inserted}"
    )
    print(
        f"schedule updated       : "
        f"{updated}"
    )
    print(
        f"raw schedule total     : "
        f"{total_rows}"
    )

    print()
    print(
        "Note:"
    )
    print(
        "この38件は試合後スタッツではなく"
        "FootyStats上の試合日程です。"
    )
    print(
        "jleague_match_idとの照合後に"
        "正規テーブルへ移します。"
    )


def main() -> None:
    args = parse_args()

    html_path = resolve_path(
        args.html_path
    )

    html = read_html(
        html_path
    )

    result = build_result(
        html_path=html_path,
        html=html,
    )

    team_name = result.get(
        "team_name"
    )

    external_team_id = result.get(
        "footystats_team_id"
    )

    if not isinstance(
        team_name,
        str,
    ) or not team_name.strip():
        raise ValueError(
            "FootyStatsチーム名を"
            "取得できませんでした"
        )

    if not isinstance(
        external_team_id,
        int,
    ):
        raise ValueError(
            "FootyStatsチームIDを"
            "取得できませんでした"
        )

    source_url = (
        "https://footystats.org/jp/clubs/"
        f"avispa-fukuoka-{external_team_id}"
    )

    con = connect_database()

    try:
        short_name = validate_team_id(
            con,
            args.team_id,
        )

        create_raw_schedule_table(
            con
        )

        alias_status = upsert_team_alias(
            con=con,
            alias_name=team_name.strip(),
            team_id=args.team_id,
        )

        source_map_status = (
            upsert_team_source_map(
                con=con,
                team_id=args.team_id,
                external_team_id=external_team_id,
                external_name=team_name.strip(),
                source_url=source_url,
            )
        )

        inserted = 0
        updated = 0

        for match in result["matches"]:
            status = upsert_schedule_match(
                con=con,
                team_id=args.team_id,
                subject_external_team_id=(
                    external_team_id
                ),
                source_file=str(
                    html_path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                source_url=source_url,
                match=match,
            )

            if status == "inserted":
                inserted += 1
            else:
                updated += 1

        con.commit()

        total_rows = con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_schedule_raw
            """
        ).fetchone()[0]

        print_summary(
            team_id=args.team_id,
            short_name=short_name,
            result=result,
            alias_status=alias_status,
            source_map_status=source_map_status,
            inserted=inserted,
            updated=updated,
            total_rows=int(total_rows),
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
