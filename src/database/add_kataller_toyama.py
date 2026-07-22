# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

TEAM_ID = 12
SHORT_NAME = "富山"
FULL_NAME = "カターレ富山"
ENGLISH_NAME = "Kataller Toyama"

FOOTYSTATS_ID = "880"
FOOTYSTATS_URL = (
    "https://footystats.org/jp/clubs/"
    "kataller-toyama-880"
)


def main() -> None:
    con = sqlite3.connect(DB_PATH)

    try:
        team = con.execute(
            """
            SELECT
                team_id,
                short_name
            FROM team_master
            WHERE team_id = ?
            """,
            (TEAM_ID,),
        ).fetchone()

        if team is None:
            raise RuntimeError(
                f"team_id={TEAM_ID} が存在しません"
            )

        con.execute(
            """
            UPDATE team_master
            SET full_name = ?
            WHERE team_id = ?
            """,
            (
                FULL_NAME,
                TEAM_ID,
            ),
        )

        alias_results: dict[str, str] = {}

        for alias_name in (
            SHORT_NAME,
            FULL_NAME,
            ENGLISH_NAME,
        ):
            row = con.execute(
                """
                SELECT team_id
                FROM team_alias_v2
                WHERE alias_name = ?
                """,
                (alias_name,),
            ).fetchone()

            if row is None:
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
                        TEAM_ID,
                        "manual_mapping",
                    ),
                )

                alias_results[alias_name] = "inserted"
                continue

            if int(row[0]) != TEAM_ID:
                raise ValueError(
                    "別team_idへ登録済みのaliasです: "
                    f"{alias_name} -> {row[0]}"
                )

            alias_results[alias_name] = "existing"

        source = con.execute(
            """
            SELECT
                team_source_map_id,
                team_id
            FROM team_source_map
            WHERE source_name = 'footystats'
              AND external_team_id = ?
            """,
            (FOOTYSTATS_ID,),
        ).fetchone()

        if source is None:
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
                    TEAM_ID,
                    "footystats",
                    FOOTYSTATS_ID,
                    FULL_NAME,
                    FOOTYSTATS_URL,
                    1,
                ),
            )

            source_status = "inserted"

        else:
            if int(source[1]) != TEAM_ID:
                raise ValueError(
                    "FootyStats ID 880が別team_idへ"
                    f"登録されています: {source[1]}"
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
                    int(source[0]),
                ),
            )

            source_status = "updated"

        con.commit()

        print("=" * 90)
        print("Kataller Toyama Registration")
        print("=" * 90)
        print(f"team_id              : {TEAM_ID}")
        print(f"short_name           : {team[1]}")
        print(f"full_name            : {FULL_NAME}")
        print(f"footystats id        : {FOOTYSTATS_ID}")
        print(f"footystats source map: {source_status}")

        print()
        print("ALIASES")
        print("-" * 90)

        for alias_name, status in alias_results.items():
            print(f"{alias_name:<30}: {status}")

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()


