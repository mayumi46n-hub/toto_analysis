#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = PROJECT_ROOT / "data/toto.db"
DEFAULT_CSV = (
    PROJECT_ROOT
    / "data/master/footystats_match_candidates_2025_all.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "FootyStats Fixtures HTMLから生成した候補CSVを"
            "footystats_match_urlsへ登録します。"
        )
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="SQLite DB。初期値: data/toto.db",
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help=(
            "候補CSV。初期値: "
            "data/master/footystats_match_candidates_2025_all.csv"
        ),
    )

    parser.add_argument(
        "--season",
        type=int,
        default=2025,
        help="対象シーズン。初期値: 2025",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="検証のみ行い、DBへ書き込みません。",
    )

    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def validate_schema(con: sqlite3.Connection) -> None:
    columns = {
        row[1]
        for row in con.execute(
            "PRAGMA table_info(footystats_match_urls)"
        )
    }

    required = {
        "season",
        "match_slug",
        "source_url",
        "source_team_id",
        "source_team_name",
        "download_status",
        "parse_status",
        "import_status",
        "link_status",
    }

    missing = sorted(required - columns)

    if missing:
        raise RuntimeError(
            "footystats_match_urls列不足: "
            + ", ".join(missing)
        )


def read_rows(
    csv_path: Path,
    expected_season: int,
) -> list[dict[str, str]]:
    with csv_path.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "season",
            "league",
            "footystats_match_id",
            "match_slug",
            "url",
        }

        fieldnames = set(reader.fieldnames or [])
        missing = sorted(required - fieldnames)

        if missing:
            raise RuntimeError(
                "CSV列不足: " + ", ".join(missing)
            )

        rows: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        seen_ids: set[str] = set()

        for line_no, row in enumerate(reader, start=2):
            season_text = (row["season"] or "").strip()
            league = (row["league"] or "").strip()
            match_id = (
                row["footystats_match_id"] or ""
            ).strip()
            match_slug = (
                row["match_slug"] or ""
            ).strip()
            source_url = (row["url"] or "").strip()

            if not season_text.isdigit():
                raise RuntimeError(
                    f"{line_no}行目: seasonが不正です"
                )

            season = int(season_text)

            if season != expected_season:
                raise RuntimeError(
                    f"{line_no}行目: season={season} "
                    f"expected={expected_season}"
                )

            if league not in {"J1", "J2", "J3"}:
                raise RuntimeError(
                    f"{line_no}行目: leagueが不正です: "
                    f"{league}"
                )

            if not match_id.isdigit():
                raise RuntimeError(
                    f"{line_no}行目: Match IDが不正です: "
                    f"{match_id}"
                )

            if not match_slug.endswith("-h2h-stats"):
                raise RuntimeError(
                    f"{line_no}行目: match_slugが不正です: "
                    f"{match_slug}"
                )

            parsed = urlsplit(source_url)

            if parsed.netloc not in {
                "footystats.org",
                "www.footystats.org",
            }:
                raise RuntimeError(
                    f"{line_no}行目: URLドメインが不正です"
                )

            if parsed.fragment != match_id:
                raise RuntimeError(
                    f"{line_no}行目: URL fragmentと"
                    f"Match IDが一致しません"
                )

            if source_url in seen_urls:
                raise RuntimeError(
                    f"{line_no}行目: URL重複: {source_url}"
                )

            if match_id in seen_ids:
                raise RuntimeError(
                    f"{line_no}行目: Match ID重複: "
                    f"{match_id}"
                )

            seen_urls.add(source_url)
            seen_ids.add(match_id)

            rows.append(
                {
                    "season": str(season),
                    "league": league,
                    "footystats_match_id": match_id,
                    "match_slug": match_slug,
                    "source_url": source_url,
                }
            )

    return rows


def import_rows(
    con: sqlite3.Connection,
    rows: list[dict[str, str]],
    *,
    season: int,
) -> tuple[int, int, int]:
    inserted = 0
    existing_same_season = 0
    conflicts = 0

    for row in rows:
        existing = con.execute(
            """
            SELECT
                footystats_match_url_id,
                season,
                match_slug
            FROM footystats_match_urls
            WHERE source_url = ?
            """,
            (row["source_url"],),
        ).fetchone()

        if existing is not None:
            if int(existing["season"]) == season:
                existing_same_season += 1
                continue

            conflicts += 1
            raise RuntimeError(
                "同じsource_urlが別シーズンに登録済みです: "
                f"url={row['source_url']} "
                f"existing_season={existing['season']} "
                f"new_season={season}"
            )

        con.execute(
            """
            INSERT INTO footystats_match_urls (
                season,
                match_slug,
                source_url,
                source_team_id,
                source_team_name,
                download_status,
                parse_status,
                import_status,
                link_status
            )
            VALUES (
                ?, ?, ?, NULL, NULL,
                'pending',
                'pending',
                'pending',
                'pending'
            )
            """,
            (
                season,
                row["match_slug"],
                row["source_url"],
            ),
        )

        inserted += 1

    return inserted, existing_same_season, conflicts


def summarize_csv(
    rows: list[dict[str, str]],
) -> dict[str, int]:
    result = {"J1": 0, "J2": 0, "J3": 0}

    for row in rows:
        result[row["league"]] += 1

    return result


def run(args: argparse.Namespace) -> int:
    db_path = resolve_path(args.db)
    csv_path = resolve_path(args.csv)

    if not db_path.is_file():
        raise FileNotFoundError(
            f"DBが見つかりません: {db_path}"
        )

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"CSVが見つかりません: {csv_path}"
        )

    rows = read_rows(
        csv_path,
        expected_season=args.season,
    )

    by_league = summarize_csv(rows)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 30000")

    try:
        validate_schema(con)

        existing_before = con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_urls
            WHERE season = ?
            """,
            (args.season,),
        ).fetchone()[0]

        inserted = 0
        existing_same_season = 0
        conflicts = 0

        con.execute("BEGIN")

        inserted, existing_same_season, conflicts = (
            import_rows(
                con,
                rows,
                season=args.season,
            )
        )

        if args.dry_run:
            con.rollback()
        else:
            con.commit()

        existing_after = con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_urls
            WHERE season = ?
            """,
            (args.season,),
        ).fetchone()[0]

        print("=" * 100)
        print("FootyStats Match URL Import")
        print("=" * 100)
        print(f"database          : {display_path(db_path)}")
        print(f"csv               : {display_path(csv_path)}")
        print(f"season            : {args.season}")
        print(f"csv rows          : {len(rows)}")
        print(f"J1 rows           : {by_league['J1']}")
        print(f"J2 rows           : {by_league['J2']}")
        print(f"J3 rows           : {by_league['J3']}")
        print(f"existing before   : {existing_before}")
        print(f"inserted          : {inserted}")
        print(f"already existing  : {existing_same_season}")
        print(f"conflicts         : {conflicts}")
        print(f"existing after    : {existing_after}")
        print(f"dry run           : {args.dry_run}")

        if args.dry_run:
            print()
            print("RESULT: validation completed; DB unchanged.")
        else:
            print()
            print("RESULT: match URLs imported successfully.")

        return 0

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def main() -> int:
    args = parse_args()

    try:
        return run(args)
    except KeyboardInterrupt:
        print("ERROR: interrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
