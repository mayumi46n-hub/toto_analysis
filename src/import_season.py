# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from normalize_team import normalize_team_name


DB_PATH = Path("data/toto.db")
INPUT_ROOT = Path("data/jleague_seasons")


def parse_attendance(
    text: str | None,
) -> int | None:
    digits = re.sub(
        r"[^\d]",
        "",
        text or "",
    )

    return int(digits) if digits else None


def parse_season(
    text: str | None,
) -> int | None:
    if not text:
        return None

    match = re.match(
        r"\s*(\d{4})",
        text,
    )

    if match is None:
        return None

    return int(match.group(1))


def parse_score(
    text: str | None,
) -> tuple[int | None, int | None]:
    if not text:
        return None, None

    match = re.fullmatch(
        r"\s*(\d+)\s*-\s*(\d+)\s*",
        text,
    )

    if match is None:
        return None, None

    return (
        int(match.group(1)),
        int(match.group(2)),
    )


def parse_html(
    html_path: Path,
    expected_year: int,
) -> list[tuple[Any, ...]]:
    html = html_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    matches: list[tuple[Any, ...]] = []

    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [
                cell.get_text(
                    " ",
                    strip=True,
                )
                for cell in tr.find_all(
                    ["td", "th"]
                )
            ]

            if len(cells) < 10:
                continue

            season = parse_season(
                cells[0]
            )

            if season is None:
                continue

            if season != expected_year:
                continue

            home_team = normalize_team_name(
                cells[5]
            )

            away_team = normalize_team_name(
                cells[7]
            )

            if not home_team or not away_team:
                continue

            home_score, away_score = parse_score(
                cells[6]
            )

            matches.append(
                (
                    season,
                    cells[1],
                    cells[2],
                    cells[3],
                    cells[4],
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    cells[8],
                    parse_attendance(
                        cells[9]
                    ),
                    None,
                )
            )

    return matches


def load_season_matches(
    year: int,
) -> list[tuple[Any, ...]]:
    season_dir = (
        INPUT_ROOT
        / str(year)
    )

    html_files = [
        season_dir / "j1.html",
        season_dir / "j2.html",
    ]

    missing = [
        str(path)
        for path in html_files
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "HTMLがありません:\n"
            + "\n".join(missing)
        )

    all_matches: list[
        tuple[Any, ...]
    ] = []

    for html_path in html_files:
        matches = parse_html(
            html_path=html_path,
            expected_year=year,
        )

        completed_count = sum(
            1
            for row in matches
            if (
                row[7] is not None
                and row[8] is not None
            )
        )

        scheduled_count = (
            len(matches)
            - completed_count
        )

        print(
            f"{html_path}: "
            f"{len(matches)}試合 "
            f"(結果あり={completed_count}, "
            f"未開催={scheduled_count})"
        )

        all_matches.extend(
            matches
        )

    return all_matches


def save_matches(
    year: int,
    matches: list[tuple[Any, ...]],
) -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(
        DB_PATH
    )

    try:
        cur = con.cursor()

        cur.execute(
            """
            DELETE FROM jleague_matches
            WHERE season = ?
            """,
            (year,),
        )

        cur.executemany(
            """
            INSERT INTO jleague_matches (
                season,
                competition,
                section,
                match_date,
                kickoff_time,
                home_team,
                away_team,
                home_score,
                away_score,
                stadium,
                attendance,
                match_url
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            matches,
        )

        inserted_count = int(
            cur.execute(
                """
                SELECT COUNT(*)
                FROM jleague_matches
                WHERE season = ?
                """,
                (year,),
            ).fetchone()[0]
        )

        if inserted_count != len(matches):
            raise RuntimeError(
                "保存件数が一致しません: "
                f"expected={len(matches)}, "
                f"actual={inserted_count}"
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def print_summary(
    year: int,
    matches: list[tuple[Any, ...]],
) -> None:
    completed_count = sum(
        1
        for row in matches
        if (
            row[7] is not None
            and row[8] is not None
        )
    )

    scheduled_count = (
        len(matches)
        - completed_count
    )

    print("=" * 100)
    print(
        "J.League Season Import"
    )
    print("=" * 100)

    print(
        f"season           : {year}"
    )
    print(
        f"total matches    : {len(matches)}"
    )
    print(
        f"completed        : {completed_count}"
    )
    print(
        f"scheduled        : {scheduled_count}"
    )
    print(
        f"database         : {DB_PATH}"
    )


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "使い方: "
            "python src/import_season.py YEAR"
        )
        print(
            "例: "
            "python src/import_season.py 2026"
        )
        sys.exit(1)

    try:
        year = int(
            sys.argv[1]
        )
    except ValueError as exc:
        raise ValueError(
            "YEARは整数で指定してください"
        ) from exc

    matches = load_season_matches(
        year
    )

    if not matches:
        raise RuntimeError(
            f"{year}年の試合を"
            "HTMLから取得できませんでした"
        )

    save_matches(
        year=year,
        matches=matches,
    )

    print_summary(
        year=year,
        matches=matches,
    )


if __name__ == "__main__":
    main()