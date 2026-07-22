#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_ROOT = PROJECT_ROOT / "data/raw/footystats/fixtures"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/master"
LEAGUES = ("j1", "j2", "j3")
FIELDNAMES = ["season", "league", "footystats_match_id", "match_slug", "url"]
MATCH_URL_RE = re.compile(
    r'href="(?P<url>'
    r'https?://(?:www\.)?footystats\.org/'
    r'(?:jp/)?japan/'
    r'[^\"]+-h2h-stats'
    r'#(?P<match_id>\d+)'
    r')"',
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStats Fixtures HTMLから、"
            "試合単位のURLとMatch IDを抽出してCSV保存します。"
        )
    )
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--league", action="append", choices=LEAGUES)
    parser.add_argument("--min-matches", type=int, default=1)
    parser.add_argument("--strict-expected", action="store_true")
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def normalize_match_url(raw_url: str) -> tuple[str, str, str]:
    parts = urlsplit(raw_url)
    match_id = parts.fragment.strip()
    if not match_id.isdigit():
        raise ValueError(f"FootyStats Match IDが不正です: {raw_url}")
    match_slug = parts.path.rstrip("/").rsplit("/", maxsplit=1)[-1]
    source_url = urlunsplit(("https", "footystats.org", parts.path, "", match_id))
    return match_id, match_slug, source_url


def extract_rows(html_path: Path, *, season: int, league: str) -> tuple[list[dict[str, str]], int]:
    if not html_path.is_file():
        raise FileNotFoundError(f"Fixtures HTMLが見つかりません: {html_path}")

    html = html_path.read_text(encoding="utf-8", errors="replace")
    matches: dict[str, dict[str, str]] = {}
    alias_conflicts = 0

    for match in MATCH_URL_RE.finditer(html):
        raw_url = match.group("url")
        match_id, match_slug, source_url = normalize_match_url(raw_url)
        row = {
            "season": str(season),
            "league": league.upper(),
            "footystats_match_id": match_id,
            "match_slug": match_slug,
            "url": source_url,
        }
        existing = matches.get(match_id)
        if existing is not None:
            if existing["url"] != row["url"]:
                alias_conflicts += 1
                # 同一試合がホーム/アウェー順の異なるH2H URLで
                # 複数掲載されることがある。Match IDを正とし、
                # 再現性のため辞書順で小さいURLを代表として採用する。
                if row["url"] < existing["url"]:
                    matches[match_id] = row
            continue
        matches[match_id] = row

    rows = sorted(
        matches.values(),
        key=lambda row: int(row["footystats_match_id"]),
    )
    return rows, alias_conflicts


def validate_rows(rows: list[dict[str, str]], *, league: str, min_matches: int, strict_expected: bool) -> None:
    if len(rows) < min_matches:
        raise RuntimeError(f"{league.upper()}の抽出件数が不足しています: {len(rows)} < {min_matches}")
    if strict_expected:
        if league == "j1" and len(rows) != 380:
            raise RuntimeError(f"J1の期待件数は380ですが、{len(rows)}件です。")
        if league in {"j2", "j3"} and len(rows) < 380:
            raise RuntimeError(f"{league.upper()}は380件以上を期待していますが、{len(rows)}件です。")


def write_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def ensure_unique_match_ids(rows: list[dict[str, str]]) -> None:
    seen: dict[str, str] = {}
    for row in rows:
        match_id = row["footystats_match_id"]
        league = row["league"]
        existing = seen.get(match_id)
        if existing is not None and existing != league:
            raise RuntimeError(f"複数リーグで同じMatch IDがあります: {match_id} ({existing}, {league})")
        seen[match_id] = league


def run(args: argparse.Namespace) -> int:
    input_root = resolve_path(args.input_root)
    output_dir = resolve_path(args.output_dir)
    leagues = tuple(args.league or LEAGUES)
    season_dir = input_root / str(args.season)
    all_rows: list[dict[str, str]] = []

    print("=" * 100)
    print("FootyStats Fixture Link Extraction")
    print("=" * 100)
    print(f"season       : {args.season}")
    print(f"input root   : {display_path(input_root)}")
    print(f"output dir   : {display_path(output_dir)}")
    print(f"leagues      : {', '.join(x.upper() for x in leagues)}")
    print()

    for league in leagues:
        html_path = season_dir / f"{league}_fixtures.html"
        output_path = output_dir / f"footystats_match_candidates_{args.season}_{league}.csv"
        rows, alias_conflicts = extract_rows(
            html_path,
            season=args.season,
            league=league,
        )
        validate_rows(
            rows,
            league=league,
            min_matches=args.min_matches,
            strict_expected=args.strict_expected,
        )
        write_csv(output_path, rows)
        all_rows.extend(rows)
        print(
            f"{league.upper():<3}: {len(rows):>4} matches "
            f"(alternate URLs: {alias_conflicts}) -> "
            f"{display_path(output_path)}"
        )

    ensure_unique_match_ids(all_rows)
    all_rows = sorted(all_rows, key=lambda row: (row["league"], int(row["footystats_match_id"])))
    combined_path = output_dir / f"footystats_match_candidates_{args.season}_all.csv"
    write_csv(combined_path, all_rows)

    print("-" * 100)
    print(f"ALL: {len(all_rows):>4} matches -> {display_path(combined_path)}")
    print()
    print("RESULT: fixture link extraction completed.")
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
    sys.exit(main())
