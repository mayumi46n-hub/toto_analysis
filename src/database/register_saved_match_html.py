#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = PROJECT_ROOT / "data/toto.db"
DEFAULT_HTML_ROOT = PROJECT_ROOT / "data/raw/footystats/matches"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "手動保存したFootyStats試合HTMLを検出し、"
            "footystats_match_urlsへ一括登録します。"
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
        "--html-root",
        type=Path,
        default=DEFAULT_HTML_ROOT,
        help=(
            "試合HTMLルート。初期値: "
            "data/raw/footystats/matches"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="検証のみ行い、DBを更新しません。",
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
        "html_path",
        "download_status",
        "last_error",
        "downloaded_at",
        "updated_at",
    }
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError(
            "footystats_match_urls列不足: "
            + ", ".join(missing)
        )


def collect_html_files(
    season_dir: Path,
) -> list[Path]:
    if not season_dir.is_dir():
        raise FileNotFoundError(
            f"HTMLディレクトリが見つかりません: {season_dir}"
        )
    return sorted(
        path
        for path in season_dir.glob("*.html")
        if path.is_file()
    )


def run(args: argparse.Namespace) -> int:
    db_path = resolve_path(args.db)
    html_root = resolve_path(args.html_root)
    season_dir = html_root / str(args.season)

    if not db_path.is_file():
        raise FileNotFoundError(
            f"DBが見つかりません: {db_path}"
        )

    html_files = collect_html_files(season_dir)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout = 30000")

    found = len(html_files)
    updated = 0
    already_registered = 0
    missing_in_db = 0
    ambiguous = 0

    try:
        validate_schema(con)
        con.execute("BEGIN")

        for html_path in html_files:
            match_slug = html_path.stem

            rows = con.execute(
                """
                SELECT
                    footystats_match_url_id,
                    html_path,
                    download_status
                FROM footystats_match_urls
                WHERE season = ?
                  AND match_slug = ?
                ORDER BY footystats_match_url_id
                """,
                (args.season, match_slug),
            ).fetchall()

            if not rows:
                missing_in_db += 1
                print(
                    "MISSING IN DB: "
                    f"{display_path(html_path)}"
                )
                continue

            if len(rows) > 1:
                ambiguous += 1
                print(
                    "AMBIGUOUS: "
                    f"{match_slug} -> {len(rows)} rows"
                )
                continue

            row = rows[0]
            relative_html = display_path(html_path)

            if (
                row["download_status"] == "downloaded"
                and row["html_path"] == relative_html
            ):
                already_registered += 1
                continue

            con.execute(
                """
                UPDATE footystats_match_urls
                SET
                    html_path = ?,
                    download_status = 'downloaded',
                    downloaded_at = COALESCE(
                        downloaded_at,
                        CURRENT_TIMESTAMP
                    ),
                    last_error = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE footystats_match_url_id = ?
                """,
                (
                    relative_html,
                    row["footystats_match_url_id"],
                ),
            )
            updated += 1

        if args.dry_run:
            con.rollback()
        else:
            con.commit()

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    print("=" * 100)
    print("Register Saved FootyStats HTML")
    print("=" * 100)
    print(f"database           : {display_path(db_path)}")
    print(f"season             : {args.season}")
    print(f"HTML directory     : {display_path(season_dir)}")
    print(f"HTML found         : {found}")
    print(f"updated            : {updated}")
    print(f"already registered : {already_registered}")
    print(f"missing in DB      : {missing_in_db}")
    print(f"ambiguous          : {ambiguous}")
    print(f"dry run            : {args.dry_run}")

    if missing_in_db or ambiguous:
        print()
        print(
            "RESULT: completed with unresolved files."
        )
        return 2

    print()
    if args.dry_run:
        print("RESULT: validation completed; DB unchanged.")
    else:
        print("RESULT: saved HTML registration completed.")
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
