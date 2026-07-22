#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = PROJECT_ROOT / "data/toto.db"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="DBから未保存のFootyStats URLを少数だけブラウザで開きます。"
    )
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--season", type=int, required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--browser", choices=["default", "safari", "chrome"], default="default")
    p.add_argument("--include-errors", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def resolve(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path

def open_url(url: str, browser: str) -> None:
    if browser == "default":
        cmd = ["open", url]
    elif browser == "safari":
        cmd = ["open", "-a", "Safari", url]
    else:
        cmd = ["open", "-a", "Google Chrome", url]
    subprocess.run(cmd, check=False)

def main() -> int:
    args = parse_args()
    db = resolve(args.db)
    if not db.is_file():
        print(f"ERROR: DB not found: {db}", file=sys.stderr)
        return 1
    if args.count < 1 or args.count > 5:
        print("ERROR: --count must be between 1 and 5", file=sys.stderr)
        return 1

    statuses = ["pending"]
    if args.include_errors:
        statuses.append("error")
    marks = ",".join("?" for _ in statuses)

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            f"""
            SELECT footystats_match_url_id, match_slug, source_url, download_status
            FROM footystats_match_urls
            WHERE season = ?
              AND download_status IN ({marks})
            ORDER BY footystats_match_url_id
            LIMIT ?
            """,
            (args.season, *statuses, args.count),
        ).fetchall()
    finally:
        con.close()

    if not rows:
        print("No target URLs.")
        return 0

    print("=" * 90)
    print("Open Missing FootyStats URLs")
    print("=" * 90)
    print(f"season : {args.season}")
    print(f"count  : {len(rows)}")
    print(f"browser: {args.browser}")
    print(f"dry run: {args.dry_run}")
    print()

    for i, row in enumerate(rows, 1):
        print(f"[{i}] id={row['footystats_match_url_id']} {row['match_slug']}")
        print(f"    {row['source_url']}")
        if not args.dry_run:
            open_url(str(row["source_url"]), args.browser)

    print()
    print("NOTE: Free access limits may apply. Open one page at a time.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
