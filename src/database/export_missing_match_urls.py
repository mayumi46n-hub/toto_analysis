#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = PROJECT_ROOT / "data/toto.db"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/master"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "未保存のFootyStats試合URLをCSVへ出力します。"
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="SQLite DB。初期値: data/toto.db",
    )
    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="対象シーズン。例: 2025",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "出力CSV。未指定時は"
            "data/master/footystats_missing_urls_<season>.csv"
        ),
    )
    parser.add_argument(
        "--include-errors",
        action="store_true",
        help=(
            "download_status='error'も出力対象に含めます。"
        ),
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
        str(row[1])
        for row in con.execute(
            "PRAGMA table_info(footystats_match_urls)"
        )
    }
    required = {
        "footystats_match_url_id",
        "season",
        "match_slug",
        "source_url",
        "download_status",
        "html_path",
        "last_error",
    }
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError(
            "footystats_match_urls列不足: "
            + ", ".join(missing)
        )


def infer_league(
    con: sqlite3.Connection,
    season: int,
    match_id: str,
) -> str:
    table_exists = con.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type='table'
          AND name='footystats_team_catalog'
        """
    ).fetchone()

    if not table_exists:
        return ""

    return ""


def run(args: argparse.Namespace) -> int:
    db_path = resolve_path(args.db)

    if args.output:
        output_path = resolve_path(args.output)
    else:
        output_path = (
            DEFAULT_OUTPUT_DIR
            / f"footystats_missing_urls_{args.season}.csv"
        )

    if not db_path.is_file():
        raise FileNotFoundError(
            f"DBが見つかりません: {db_path}"
        )

    statuses = ["pending"]
    if args.include_errors:
        statuses.append("error")

    placeholders = ",".join("?" for _ in statuses)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    try:
        validate_schema(con)

        rows = con.execute(
            f"""
            SELECT
                footystats_match_url_id,
                season,
                match_slug,
                source_url,
                download_status,
                html_path,
                last_error
            FROM footystats_match_urls
            WHERE season = ?
              AND download_status IN ({placeholders})
            ORDER BY footystats_match_url_id
            """,
            (args.season, *statuses),
        ).fetchall()
    finally:
        con.close()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "footystats_match_url_id",
                "season",
                "match_slug",
                "url",
                "download_status",
                "html_filename",
                "last_error",
            ],
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "footystats_match_url_id": (
                        row["footystats_match_url_id"]
                    ),
                    "season": row["season"],
                    "match_slug": row["match_slug"],
                    "url": row["source_url"],
                    "download_status": (
                        row["download_status"]
                    ),
                    "html_filename": (
                        f"{row['match_slug']}.html"
                    ),
                    "last_error": (
                        row["last_error"] or ""
                    ),
                }
            )

    print("=" * 100)
    print("Export Missing FootyStats URLs")
    print("=" * 100)
    print(f"database      : {display_path(db_path)}")
    print(f"season        : {args.season}")
    print(f"statuses      : {', '.join(statuses)}")
    print(f"missing URLs  : {len(rows)}")
    print(f"output        : {display_path(output_path)}")
    print()
    print("RESULT: missing URL export completed.")

    return 0


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
    raise SystemExit(main())
