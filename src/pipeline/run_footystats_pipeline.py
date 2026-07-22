# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

DOWNLOADER = PROJECT_ROOT / "src/crawler/download_footystats_match_pages.py"
PARSER = PROJECT_ROOT / "src/pipeline/parse_pending_footystats_matches.py"
PROCESSOR = PROJECT_ROOT / "src/pipeline/process_pending_footystats_matches.py"
LINKER = PROJECT_ROOT / "src/database/link_footystats_jleague_match.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "FootyStatsの未処理試合を、ダウンロード・解析・"
            "DB取込・Jリーグ公式試合リンクまで一括処理します。"
        )
    )
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--limit", type=int, default=999999)
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retry-errors", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-parse", action="store_true")
    parser.add_argument("--skip-process", action="store_true")
    parser.add_argument("--skip-link", action="store_true")
    return parser.parse_args()


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def validate_environment() -> None:
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"DBが見つかりません: {DB_PATH}")

    missing = [
        relative_path(path)
        for path in (DOWNLOADER, PARSER, PROCESSOR, LINKER)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(
            "必要なスクリプトがありません:\n" + "\n".join(missing)
        )


def run_step(title: str, command: list[str]) -> None:
    print()
    print("=" * 110)
    print(title)
    print("=" * 110)
    print("COMMAND : " + " ".join(command))
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{title} が失敗しました: returncode={result.returncode}"
        )


def synchronize_link_statuses(season: int) -> tuple[int, int]:
    con = sqlite3.connect(DB_PATH)

    try:
        con.execute(
            """
            UPDATE footystats_match_urls
            SET
                link_status = 'linked',
                jleague_match_id = (
                    SELECT p.jleague_match_id
                    FROM footystats_match_pages AS p
                    WHERE p.id = footystats_match_urls.footystats_page_id
                ),
                last_error = NULL,
                linked_at = COALESCE(linked_at, CURRENT_TIMESTAMP),
                updated_at = CURRENT_TIMESTAMP
            WHERE season = ?
              AND import_status = 'imported'
              AND footystats_page_id IS NOT NULL
              AND EXISTS (
                  SELECT 1
                  FROM footystats_match_pages AS p
                  WHERE p.id = footystats_match_urls.footystats_page_id
                    AND p.jleague_match_id IS NOT NULL
              )
            """,
            (season,),
        )

        con.execute(
            """
            UPDATE footystats_match_urls
            SET
                link_status = 'not_found',
                jleague_match_id = NULL,
                last_error = 'Jリーグ公式試合との一致が見つかりません',
                updated_at = CURRENT_TIMESTAMP
            WHERE season = ?
              AND import_status = 'imported'
              AND footystats_page_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM footystats_match_pages AS p
                  WHERE p.id = footystats_match_urls.footystats_page_id
                    AND p.jleague_match_id IS NOT NULL
              )
            """,
            (season,),
        )

        con.commit()

        linked = int(
            con.execute(
                """
                SELECT COUNT(*)
                FROM footystats_match_urls
                WHERE season = ?
                  AND link_status = 'linked'
                """,
                (season,),
            ).fetchone()[0]
        )

        not_found = int(
            con.execute(
                """
                SELECT COUNT(*)
                FROM footystats_match_urls
                WHERE season = ?
                  AND link_status = 'not_found'
                """,
                (season,),
            ).fetchone()[0]
        )

        return linked, not_found

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def print_database_summary(season: int) -> None:
    con = sqlite3.connect(DB_PATH)

    try:
        rows = con.execute(
            """
            SELECT
                download_status,
                parse_status,
                import_status,
                link_status,
                COUNT(*) AS count
            FROM footystats_match_urls
            WHERE season = ?
            GROUP BY
                download_status,
                parse_status,
                import_status,
                link_status
            ORDER BY 1, 2, 3, 4
            """,
            (season,),
        ).fetchall()

        total = int(
            con.execute(
                """
                SELECT COUNT(*)
                FROM footystats_match_urls
                WHERE season = ?
                """,
                (season,),
            ).fetchone()[0]
        )
    finally:
        con.close()

    print()
    print("=" * 110)
    print("FINAL DATABASE STATUS")
    print("=" * 110)
    print(f"season : {season}")
    print(f"total  : {total}")
    print()

    if not rows:
        print("対象URLは登録されていません。")
        return

    for row in rows:
        print(row)


def main() -> None:
    args = parse_args()

    if args.limit <= 0:
        raise ValueError("--limitは1以上で指定してください")
    if args.delay < 0:
        raise ValueError("--delayは0以上で指定してください")
    if args.timeout <= 0:
        raise ValueError("--timeoutは1以上で指定してください")

    validate_environment()

    print("=" * 110)
    print("FootyStats Full Pipeline")
    print("=" * 110)
    print(f"season          : {args.season}")
    print(f"limit           : {args.limit}")
    print(f"delay           : {args.delay} sec")
    print(f"timeout         : {args.timeout} sec")
    print(f"retry errors    : {args.retry_errors}")
    print(f"overwrite       : {args.overwrite}")

    if not args.skip_download:
        command = [
            sys.executable,
            str(DOWNLOADER),
            "--season",
            str(args.season),
            "--limit",
            str(args.limit),
            "--delay",
            str(args.delay),
            "--timeout",
            str(args.timeout),
        ]
        if args.retry_errors:
            command.append("--retry-errors")
        if args.overwrite:
            command.append("--overwrite")
        run_step("STEP 1 / 4 : Download", command)

    if not args.skip_parse:
        command = [
            sys.executable,
            str(PARSER),
            "--season",
            str(args.season),
            "--limit",
            str(args.limit),
        ]
        if args.retry_errors:
            command.append("--retry-errors")
        run_step("STEP 2 / 4 : Parse", command)

    if not args.skip_process:
        command = [
            sys.executable,
            str(PROCESSOR),
            "--season",
            str(args.season),
            "--limit",
            str(args.limit),
        ]
        if args.retry_errors:
            command.append("--retry-errors")
        run_step("STEP 3 / 4 : Enrich / Import", command)

    if not args.skip_link:
        run_step(
            "STEP 4 / 4 : J.League Link",
            [sys.executable, str(LINKER)],
        )
        linked, not_found = synchronize_link_statuses(args.season)
        print()
        print("LINK STATUS SYNC")
        print("-" * 110)
        print(f"linked       : {linked}")
        print(f"not found    : {not_found}")

    print_database_summary(args.season)

    print()
    print("=" * 110)
    print("PIPELINE FINISHED")
    print("=" * 110)


if __name__ == "__main__":
    main()
