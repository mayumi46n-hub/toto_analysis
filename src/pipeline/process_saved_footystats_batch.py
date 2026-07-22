#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REGISTER = PROJECT_ROOT / "src/database/register_saved_match_html.py"
PARSE = PROJECT_ROOT / "src/pipeline/parse_pending_footystats_matches.py"
PROCESS = PROJECT_ROOT / "src/pipeline/process_pending_footystats_matches.py"
EXPORT = PROJECT_ROOT / "src/database/export_missing_match_urls.py"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="保存済みFootyStats HTMLを登録・解析・取込・リンクします。"
    )
    p.add_argument("--season", type=int, required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--retry-errors", action="store_true")
    p.add_argument("--skip-export", action="store_true")
    return p.parse_args()

def run_step(label: str, command: list[str]) -> None:
    print()
    print("=" * 100)
    print(label)
    print("=" * 100)
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")

def main() -> int:
    args = parse_args()
    py = sys.executable

    try:
        run_step(
            "1/4 Register saved HTML",
            [py, str(REGISTER), "--db", "data/toto.db", "--season", str(args.season)],
        )

        run_step(
            "2/4 Parse pending HTML",
            [py, str(PARSE), "--season", str(args.season), "--limit", str(args.limit)],
        )

        process_cmd = [
            py, str(PROCESS),
            "--season", str(args.season),
            "--limit", str(args.limit),
        ]
        if args.retry_errors:
            process_cmd.append("--retry-errors")

        run_step("3/4 Import and link", process_cmd)

        if not args.skip_export:
            run_step(
                "4/4 Export remaining URLs",
                [py, str(EXPORT), "--db", "data/toto.db", "--season", str(args.season), "--include-errors"],
            )

        print()
        print("RESULT: saved-match batch completed.")
        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
