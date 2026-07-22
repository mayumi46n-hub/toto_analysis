# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import sqlite3
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"


def normalize_jleague_date(
    season: int,
    raw_date: str | None,
) -> str | None:
    """
    Jリーグ公式DBの日付をISO形式へ変換する。

    例:
        season=2026
        raw_date='26/08/08(土)'
        → '2026-08-08'
    """

    if not raw_date:
        return None

    match = re.search(
        r"(\d{2})/(\d{1,2})/(\d{1,2})",
        raw_date,
    )

    if match is None:
        return None

    month = int(match.group(2))
    day = int(match.group(3))

    try:
        return date(
            season,
            month,
            day,
        ).isoformat()
    except ValueError:
        return None


def load_footystats_pages(
    con: sqlite3.Connection,
) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT
            id,
            match_date,
            home_team_id,
            away_team_id,
            home_team_name,
            away_team_name,
            jleague_match_id
        FROM footystats_match_pages
        WHERE match_date IS NOT NULL
          AND home_team_id IS NOT NULL
          AND away_team_id IS NOT NULL
        ORDER BY id
        """
    ).fetchall()


def load_jleague_candidates(
    con: sqlite3.Connection,
    season: int,
) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT
            jm.jleague_match_id,
            jm.season,
            jm.match_date,
            jm.home_team,
            jm.away_team,
            hm.team_id AS home_team_id,
            am.team_id AS away_team_id
        FROM jleague_matches AS jm
        LEFT JOIN team_alias_v2 AS ha
          ON ha.alias_name = jm.home_team
        LEFT JOIN team_master AS hm
          ON hm.team_id = ha.team_id
        LEFT JOIN team_alias_v2 AS aa
          ON aa.alias_name = jm.away_team
        LEFT JOIN team_master AS am
          ON am.team_id = aa.team_id
        WHERE jm.season = ?
        ORDER BY jm.jleague_match_id
        """,
        (season,),
    ).fetchall()


def find_match(
    page: sqlite3.Row,
    candidates: list[sqlite3.Row],
) -> tuple[int | None, str]:
    footystats_date = str(
        page["match_date"]
    )

    home_team_id = int(
        page["home_team_id"]
    )

    away_team_id = int(
        page["away_team_id"]
    )

    matches: list[int] = []

    for candidate in candidates:
        candidate_date = normalize_jleague_date(
            season=int(candidate["season"]),
            raw_date=candidate["match_date"],
        )

        if candidate_date != footystats_date:
            continue

        if candidate["home_team_id"] is None:
            continue

        if candidate["away_team_id"] is None:
            continue

        if int(candidate["home_team_id"]) != home_team_id:
            continue

        if int(candidate["away_team_id"]) != away_team_id:
            continue

        matches.append(
            int(candidate["jleague_match_id"])
        )

    if len(matches) == 1:
        return (
            matches[0],
            "matched",
        )

    if len(matches) == 0:
        return (
            None,
            "not_found",
        )

    raise RuntimeError(
        "同一日・同一対戦の公式試合が複数見つかりました: "
        f"page_id={page['id']}, "
        f"matches={matches}"
    )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(
        DB_PATH
    )

    con.row_factory = sqlite3.Row

    try:
        pages = load_footystats_pages(
            con
        )

        matched_count = 0
        not_found_count = 0
        unchanged_count = 0

        print("=" * 110)
        print("FootyStats → J.League Match Link")
        print("=" * 110)

        for page in pages:
            season = int(
                str(page["match_date"])[:4]
            )

            candidates = load_jleague_candidates(
                con=con,
                season=season,
            )

            jleague_match_id, status = find_match(
                page=page,
                candidates=candidates,
            )

            if status == "not_found":
                not_found_count += 1

                print(
                    f"NOT FOUND  "
                    f"page_id={page['id']} "
                    f"date={page['match_date']} "
                    f"{page['home_team_name']} "
                    f"vs {page['away_team_name']}"
                )

                continue

            current_id = page[
                "jleague_match_id"
            ]

            if (
                current_id is not None
                and int(current_id)
                == int(jleague_match_id)
            ):
                unchanged_count += 1

                print(
                    f"UNCHANGED  "
                    f"page_id={page['id']} "
                    f"jleague_match_id={jleague_match_id}"
                )

                continue

            con.execute(
                """
                UPDATE footystats_match_pages
                SET
                    jleague_match_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    jleague_match_id,
                    int(page["id"]),
                ),
            )

            matched_count += 1

            print(
                f"MATCHED    "
                f"page_id={page['id']} "
                f"jleague_match_id={jleague_match_id} "
                f"date={page['match_date']} "
                f"{page['home_team_name']} "
                f"vs {page['away_team_name']}"
            )

        con.commit()

        print()
        print("SUMMARY")
        print("-" * 110)
        print(
            f"FootyStats pages : {len(pages)}"
        )
        print(
            f"linked           : {matched_count}"
        )
        print(
            f"unchanged        : {unchanged_count}"
        )
        print(
            f"not found        : {not_found_count}"
        )
        print(
            f"database         : "
            f"{DB_PATH.relative_to(PROJECT_ROOT)}"
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()