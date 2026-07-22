# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

SHORT_NAME = "八戸"
FULL_NAME = "ヴァンラーレ八戸"
ENGLISH_NAME = "Vanraure Hachinohe"

FOOTYSTATS_ID = "8112"
FOOTYSTATS_URL = (
    "https://footystats.org/jp/clubs/"
    "vanraure-hachinohe-8112"
)


def find_team_id(
    con: sqlite3.Connection,
) -> int | None:
    row = con.execute(
        """
        SELECT team_id
        FROM team_master
        WHERE short_name = ?
           OR full_name = ?
        LIMIT 1
        """,
        (
            SHORT_NAME,
            FULL_NAME,
        ),
    ).fetchone()

    if row is None:
        return None

    return int(row[0])


def insert_team_master(
    con: sqlite3.Connection,
) -> int:
    cursor = con.execute(
        """
        INSERT INTO team_master (
            short_name,
            full_name,
            league,
            category
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            SHORT_NAME,
            FULL_NAME,
            "J2",
            "club",
        ),
    )

    if cursor.lastrowid is None:
        raise RuntimeError(
            "team_idを取得できませんでした"
        )

    return int(cursor.lastrowid)


def register_alias(
    con: sqlite3.Connection,
    team_id: int,
    alias_name: str,
) -> str:
    row = con.execute(
        """
        SELECT team_id
        FROM team_alias_v2
        WHERE alias_name = ?
        LIMIT 1
        """,
        (alias_name,),
    ).fetchone()

    if row is not None:
        existing_team_id = int(row[0])

        if existing_team_id != team_id:
            raise ValueError(
                "別team_idへ登録済みのaliasです: "
                f"{alias_name} -> {existing_team_id}"
            )

        return "existing"

    con.execute(
        """
        INSERT INTO team_alias_v2 (
            alias_name,
            team_id,
            source_name
        )
        VALUES (?, ?, ?)
        """,
        (
            alias_name,
            team_id,
            "manual_mapping",
        ),
    )

    return "inserted"


def register_source_map(
    con: sqlite3.Connection,
    team_id: int,
) -> str:
    row = con.execute(
        """
        SELECT
            team_source_map_id,
            team_id
        FROM team_source_map
        WHERE source_name = ?
          AND external_team_id = ?
        LIMIT 1
        """,
        (
            "footystats",
            FOOTYSTATS_ID,
        ),
    ).fetchone()

    if row is not None:
        existing_team_id = int(row[1])

        if existing_team_id != team_id:
            raise ValueError(
                "FootyStats外部IDが別team_idへ"
                "登録されています: "
                f"{FOOTYSTATS_ID} -> {existing_team_id}"
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
                FULL_NAME,
                FOOTYSTATS_URL,
                int(row[0]),
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
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            team_id,
            "footystats",
            FOOTYSTATS_ID,
            FULL_NAME,
            FOOTYSTATS_URL,
            1,
        ),
    )

    return "inserted"


def verify_registration(
    con: sqlite3.Connection,
    team_id: int,
) -> None:
    team_row = con.execute(
        """
        SELECT
            short_name,
            full_name
        FROM team_master
        WHERE team_id = ?
        """,
        (team_id,),
    ).fetchone()

    if team_row is None:
        raise RuntimeError(
            "team_masterへの登録確認に失敗しました"
        )

    alias_count = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM team_alias_v2
            WHERE team_id = ?
              AND alias_name IN (?, ?, ?)
            """,
            (
                team_id,
                SHORT_NAME,
                FULL_NAME,
                ENGLISH_NAME,
            ),
        ).fetchone()[0]
    )

    if alias_count != 3:
        raise RuntimeError(
            "alias登録件数が一致しません: "
            f"{alias_count}"
        )

    source_row = con.execute(
        """
        SELECT team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND external_team_id = ?
        """,
        (FOOTYSTATS_ID,),
    ).fetchone()

    if source_row is None:
        raise RuntimeError(
            "team_source_mapへの登録確認に失敗しました"
        )

    if int(source_row[0]) != team_id:
        raise RuntimeError(
            "team_source_mapのteam_idが一致しません"
        )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        team_id = find_team_id(
            con
        )

        if team_id is None:
            team_id = insert_team_master(
                con
            )
            team_status = "inserted"
        else:
            team_status = "existing"

            con.execute(
                """
                UPDATE team_master
                SET
                    full_name = COALESCE(
                        NULLIF(full_name, ''),
                        ?
                    ),
                    league = COALESCE(
                        NULLIF(league, ''),
                        ?
                    ),
                    category = COALESCE(
                        NULLIF(category, ''),
                        ?
                    )
                WHERE team_id = ?
                """,
                (
                    FULL_NAME,
                    "J2",
                    "club",
                    team_id,
                ),
            )

        alias_results = {}

        for alias_name in (
            SHORT_NAME,
            FULL_NAME,
            ENGLISH_NAME,
        ):
            alias_results[alias_name] = (
                register_alias(
                    con=con,
                    team_id=team_id,
                    alias_name=alias_name,
                )
            )

        source_status = register_source_map(
            con=con,
            team_id=team_id,
        )

        verify_registration(
            con=con,
            team_id=team_id,
        )

        con.commit()

        print("=" * 100)
        print("Vanraure Hachinohe Registration")
        print("=" * 100)
        print(
            f"team_id              : {team_id}"
        )
        print(
            f"team_master           : {team_status}"
        )
        print(
            f"short_name            : {SHORT_NAME}"
        )
        print(
            f"full_name             : {FULL_NAME}"
        )
        print(
            f"league                : J2"
        )
        print(
            f"footystats id         : {FOOTYSTATS_ID}"
        )
        print(
            f"footystats source map : {source_status}"
        )

        print()
        print("ALIASES")
        print("-" * 100)

        for alias_name, status in alias_results.items():
            print(
                f"{alias_name:<30} : {status}"
            )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()
