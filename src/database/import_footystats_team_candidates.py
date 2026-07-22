# -*- coding: utf-8 -*-

"""
totoLABO

File:
    import_footystats_team_candidates.py

Version:
    1.0

Updated:
    2026-07-18

Purpose:
    FootyStatsクラブ候補CSVを読み込み、
    外部チームID・クラブ名・URLをteam_source_mapへ登録する。

Input:
    data/master/footystats_team_candidates_2026.csv

Processing:
    1. FootyStats上のクラブ名を補正
    2. team_alias_v2または手動対応表で内部team_idを解決
    3. 外部名称をteam_alias_v2へ登録
    4. team_source_mapへUPSERT
    5. 全件解決できない場合はロールバック

Notes:
    - FootyStats ID 877の名称「他」は「アビスパ福岡」へ補正する。
    - 手動対応表の値はteam_master.short_nameを使用する。
    - 再実行しても重複登録しない。
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data/toto.db"

CSV_PATH = (
    PROJECT_ROOT
    / "data/master/footystats_team_candidates_2026.csv"
)


# FootyStats HTML上で名称取得に失敗した項目を補正する。
NAME_CORRECTIONS: dict[str, str] = {
    "877": "アビスパ福岡",
}


# FootyStatsクラブ名から、team_master.short_nameへの正式な対応。
#
# team_alias_v2が未整備でも、安全に内部team_idへ接続できるようにする。
MANUAL_CANONICAL_SHORT_NAME: dict[str, str] = {
    "京都サンガF.C.": "京都",
    "清水エスパルス": "清水",
    "水戸ホーリーホック": "水戸",
    "ジェフユナイテッド市原・千葉": "千葉",
    "ファジアーノ岡山FC": "岡山",
    "セレッソ大阪": "Ｃ大阪",
    "東京ヴェルディ1969": "東京Ｖ",
    "FC町田ゼルビア": "町田",
    "V・ファーレン長崎": "長崎",
    "アビスパ福岡": "福岡",
    "名古屋グランパスエイト": "名古屋",
    "横浜マリノス": "横浜FM",
    "浦和レッズ": "浦和",
    "ガンバ大阪": "Ｇ大阪",
    "鹿島アントラーズ": "鹿島",
    "サンフレッチェ広島": "広島",
    "ヴィッセル神戸": "神戸",
    "FC東京": "FC東京",
    "柏レイソル": "柏",
    "川崎フロンターレ": "川崎Ｆ",
}


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    con.execute(
        "PRAGMA foreign_keys = ON"
    )

    return con


def read_candidates() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSVが見つかりません: {CSV_PATH}"
        )

    rows: list[dict[str, str]] = []

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "external_team_id",
            "team_name",
            "source_url",
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        missing_columns = (
            required_columns - actual_columns
        )

        if missing_columns:
            raise ValueError(
                "CSVの必須列が不足しています: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            external_team_id = (
                row.get("external_team_id", "")
                .strip()
            )

            team_name = (
                row.get("team_name", "")
                .strip()
            )

            source_url = (
                row.get("source_url", "")
                .strip()
            )

            if not external_team_id:
                raise ValueError(
                    f"{line_number}行目: "
                    "external_team_idが空です"
                )

            if not external_team_id.isdigit():
                raise ValueError(
                    f"{line_number}行目: "
                    "external_team_idが数値ではありません: "
                    f"{external_team_id}"
                )

            corrected_name = NAME_CORRECTIONS.get(
                external_team_id,
                team_name,
            )

            if not corrected_name:
                raise ValueError(
                    f"{line_number}行目: "
                    "team_nameが空です"
                )

            if not source_url:
                raise ValueError(
                    f"{line_number}行目: "
                    "source_urlが空です"
                )

            rows.append(
                {
                    "external_team_id": (
                        external_team_id
                    ),
                    "team_name": corrected_name,
                    "source_url": source_url,
                }
            )

    validate_candidate_duplicates(rows)

    return rows


def validate_candidate_duplicates(
    rows: list[dict[str, str]],
) -> None:
    seen_ids: set[str] = set()

    for row in rows:
        external_team_id = row[
            "external_team_id"
        ]

        if external_team_id in seen_ids:
            raise ValueError(
                "CSV内でFootyStatsチームIDが"
                "重複しています: "
                f"{external_team_id}"
            )

        seen_ids.add(
            external_team_id
        )


def get_team_by_short_name(
    con: sqlite3.Connection,
    short_name: str,
) -> tuple[int, str]:
    row = con.execute(
        """
        SELECT
            team_id,
            short_name
        FROM team_master
        WHERE short_name = ?
        """,
        (short_name,),
    ).fetchone()

    if row is None:
        raise ValueError(
            "team_masterに正規チーム名が"
            "存在しません: "
            f"{short_name}"
        )

    return int(row[0]), str(row[1])


def resolve_by_alias(
    con: sqlite3.Connection,
    team_name: str,
) -> tuple[int, str] | None:
    row = con.execute(
        """
        SELECT
            tm.team_id,
            tm.short_name
        FROM team_alias_v2 AS tav
        JOIN team_master AS tm
          ON tm.team_id = tav.team_id
        WHERE tav.alias_name = ?
        """,
        (team_name,),
    ).fetchone()

    if row is None:
        return None

    return int(row[0]), str(row[1])


def resolve_team(
    con: sqlite3.Connection,
    team_name: str,
) -> tuple[int, str, str]:
    alias_result = resolve_by_alias(
        con,
        team_name,
    )

    manual_short_name = (
        MANUAL_CANONICAL_SHORT_NAME.get(
            team_name
        )
    )

    if alias_result is not None:
        alias_team_id, alias_short_name = (
            alias_result
        )

        if manual_short_name is not None:
            manual_team_id, resolved_manual_name = (
                get_team_by_short_name(
                    con,
                    manual_short_name,
                )
            )

            if manual_team_id != alias_team_id:
                raise ValueError(
                    "team_alias_v2と手動対応表が"
                    "矛盾しています: "
                    f"{team_name} / "
                    f"alias={alias_short_name}"
                    f"(team_id={alias_team_id}) / "
                    f"manual={resolved_manual_name}"
                    f"(team_id={manual_team_id})"
                )

        return (
            alias_team_id,
            alias_short_name,
            "team_alias_v2",
        )

    if manual_short_name is None:
        raise ValueError(
            "内部チームを解決できません: "
            f"{team_name}"
        )

    team_id, short_name = (
        get_team_by_short_name(
            con,
            manual_short_name,
        )
    )

    return (
        team_id,
        short_name,
        "manual_mapping",
    )


def upsert_alias(
    con: sqlite3.Connection,
    team_name: str,
    team_id: int,
) -> str:
    existing = con.execute(
        """
        SELECT team_id
        FROM team_alias_v2
        WHERE alias_name = ?
        """,
        (team_name,),
    ).fetchone()

    if existing is not None:
        existing_team_id = int(
            existing[0]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "既存のteam_alias_v2と"
                "登録対象が矛盾しています: "
                f"{team_name} -> "
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
        VALUES (
            ?,
            ?,
            'footystats'
        )
        """,
        (
            team_name,
            team_id,
        ),
    )

    return "inserted"


def upsert_source_map(
    con: sqlite3.Connection,
    team_id: int,
    external_team_id: str,
    team_name: str,
    source_url: str,
) -> str:
    existing_by_id = con.execute(
        """
        SELECT
            team_source_map_id,
            team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND external_team_id = ?
        """,
        (external_team_id,),
    ).fetchone()

    if existing_by_id is not None:
        map_id = int(
            existing_by_id[0]
        )

        existing_team_id = int(
            existing_by_id[1]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "FootyStats外部IDの既存対応と"
                "登録対象が矛盾しています: "
                f"{external_team_id} -> "
                f"{existing_team_id}, "
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
                team_name,
                source_url,
                map_id,
            ),
        )

        return "updated"

    existing_by_name = con.execute(
        """
        SELECT
            team_source_map_id,
            team_id,
            external_team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND external_name = ?
        """,
        (team_name,),
    ).fetchone()

    if existing_by_name is not None:
        map_id = int(
            existing_by_name[0]
        )

        existing_team_id = int(
            existing_by_name[1]
        )

        existing_external_id = (
            existing_by_name[2]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "FootyStats名称の既存対応と"
                "登録対象が矛盾しています: "
                f"{team_name} -> "
                f"{existing_team_id}, "
                f"指定={team_id}"
            )

        if (
            existing_external_id is not None
            and str(existing_external_id)
            != external_team_id
        ):
            raise ValueError(
                "FootyStats名称に異なる外部IDが"
                "登録されています: "
                f"{team_name} / "
                f"既存={existing_external_id} / "
                f"指定={external_team_id}"
            )

        con.execute(
            """
            UPDATE team_source_map
            SET
                external_team_id = ?,
                source_url = ?,
                is_primary = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE team_source_map_id = ?
            """,
            (
                external_team_id,
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
            external_team_id,
            team_name,
            source_url,
        ),
    )

    return "inserted"


def process_candidates(
    con: sqlite3.Connection,
    candidates: list[dict[str, str]],
) -> tuple[
    list[dict[str, Any]],
    int,
    int,
    int,
    int,
]:
    results: list[dict[str, Any]] = []

    aliases_inserted = 0
    aliases_existing = 0

    source_maps_inserted = 0
    source_maps_updated = 0

    for candidate in candidates:
        external_team_id = candidate[
            "external_team_id"
        ]

        team_name = candidate[
            "team_name"
        ]

        source_url = candidate[
            "source_url"
        ]

        (
            team_id,
            short_name,
            resolution_method,
        ) = resolve_team(
            con,
            team_name,
        )

        alias_status = upsert_alias(
            con=con,
            team_name=team_name,
            team_id=team_id,
        )

        if alias_status == "inserted":
            aliases_inserted += 1
        else:
            aliases_existing += 1

        source_map_status = (
            upsert_source_map(
                con=con,
                team_id=team_id,
                external_team_id=(
                    external_team_id
                ),
                team_name=team_name,
                source_url=source_url,
            )
        )

        if source_map_status == "inserted":
            source_maps_inserted += 1
        else:
            source_maps_updated += 1

        results.append(
            {
                "external_team_id": (
                    external_team_id
                ),
                "external_name": team_name,
                "team_id": team_id,
                "short_name": short_name,
                "resolution_method": (
                    resolution_method
                ),
                "alias_status": alias_status,
                "source_map_status": (
                    source_map_status
                ),
            }
        )

    return (
        results,
        aliases_inserted,
        aliases_existing,
        source_maps_inserted,
        source_maps_updated,
    )


def verify_import(
    con: sqlite3.Connection,
    expected_external_ids: set[str],
) -> None:
    rows = con.execute(
        """
        SELECT external_team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND external_team_id IS NOT NULL
        """
    ).fetchall()

    registered_ids = {
        str(row[0])
        for row in rows
    }

    missing_ids = (
        expected_external_ids
        - registered_ids
    )

    if missing_ids:
        raise ValueError(
            "team_source_mapへ登録されていない"
            "FootyStats IDがあります: "
            + ", ".join(
                sorted(
                    missing_ids,
                    key=int,
                )
            )
        )


def print_summary(
    results: list[dict[str, Any]],
    aliases_inserted: int,
    aliases_existing: int,
    source_maps_inserted: int,
    source_maps_updated: int,
    total_footystats_maps: int,
) -> None:
    print("=" * 110)
    print(
        "FootyStats Team Candidate Import"
    )
    print("=" * 110)

    print(
        f"candidate rows          : "
        f"{len(results)}"
    )
    print(
        f"aliases inserted        : "
        f"{aliases_inserted}"
    )
    print(
        f"aliases existing        : "
        f"{aliases_existing}"
    )
    print(
        f"source maps inserted    : "
        f"{source_maps_inserted}"
    )
    print(
        f"source maps updated     : "
        f"{source_maps_updated}"
    )
    print(
        f"footystats map total    : "
        f"{total_footystats_maps}"
    )

    print()
    print("MAPPING RESULT")
    print("-" * 110)

    for result in results:
        print(
            f"{result['external_team_id']:<8}"
            f"{result['external_name']:<28}"
            f" -> team_id="
            f"{result['team_id']:<4}"
            f"{result['short_name']:<12}"
            f"[{result['resolution_method']}, "
            f"{result['source_map_status']}]"
        )


def main() -> None:
    candidates = read_candidates()

    expected_external_ids = {
        row["external_team_id"]
        for row in candidates
    }

    con = connect_database()

    try:
        (
            results,
            aliases_inserted,
            aliases_existing,
            source_maps_inserted,
            source_maps_updated,
        ) = process_candidates(
            con,
            candidates,
        )

        verify_import(
            con,
            expected_external_ids,
        )

        con.commit()

        total_footystats_maps = int(
            con.execute(
                """
                SELECT COUNT(*)
                FROM team_source_map
                WHERE source_name = 'footystats'
                """
            ).fetchone()[0]
        )

        print_summary(
            results=results,
            aliases_inserted=aliases_inserted,
            aliases_existing=aliases_existing,
            source_maps_inserted=(
                source_maps_inserted
            ),
            source_maps_updated=(
                source_maps_updated
            ),
            total_footystats_maps=(
                total_footystats_maps
            ),
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
