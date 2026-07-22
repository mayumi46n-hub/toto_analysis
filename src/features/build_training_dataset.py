# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

DEFAULT_FEATURE_CSV = PROJECT_ROOT / "data/features" / "footystats_match_features_{season}.csv"
DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "data/features" / "training_dataset_{season}.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "FootyStats特徴量CSVとJリーグ公式結果を結合し、"
            "教師あり学習用CSVを生成します。"
        )
    )
    parser.add_argument("--season", type=int, required=True, help="対象シーズン")
    parser.add_argument(
        "--features",
        type=Path,
        help=(
            "入力特徴量CSV。省略時は "
            "data/features/footystats_match_features_<season>.csv"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "出力CSV。省略時は "
            "data/features/training_dataset_<season>.csv"
        ),
    )
    parser.add_argument(
        "--include-unplayed",
        action="store_true",
        help="未開催試合も残し、その場合target列を空欄にします。",
    )
    return parser.parse_args()


def resolve_project_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def resolve_feature_path(season: int, supplied: Path | None) -> Path:
    if supplied is not None:
        return resolve_project_path(supplied)
    return Path(str(DEFAULT_FEATURE_CSV).format(season=season))


def resolve_output_path(season: int, supplied: Path | None) -> Path:
    if supplied is not None:
        return resolve_project_path(supplied)
    return Path(str(DEFAULT_OUTPUT_CSV).format(season=season))


def load_feature_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise FileNotFoundError(f"特徴量CSVが見つかりません: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("特徴量CSVにヘッダーがありません")
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if "jleague_match_id" not in fieldnames:
        raise ValueError("特徴量CSVにjleague_match_id列がありません")

    return fieldnames, rows


def load_results(season: int) -> dict[int, dict[str, Any]]:
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"DBが見つかりません: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT
                jleague_match_id,
                season,
                competition,
                match_date,
                kickoff_time,
                home_team,
                away_team,
                home_score,
                away_score,
                stadium,
                attendance,
                section
            FROM jleague_matches
            WHERE season = ?
            ORDER BY jleague_match_id
            """,
            (season,),
        ).fetchall()
    finally:
        con.close()

    results: dict[int, dict[str, Any]] = {}
    for row in rows:
        match_id = int(row["jleague_match_id"])
        if match_id in results:
            raise RuntimeError(f"jleague_matchesに重複IDがあります: {match_id}")
        results[match_id] = dict(row)
    return results


def parse_match_id(raw: str | None) -> int:
    text = "" if raw is None else str(raw).strip()
    if not text:
        raise ValueError("jleague_match_idが空です")
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"jleague_match_idが整数ではありません: {text}") from exc


def build_targets(home_score: int | None, away_score: int | None) -> dict[str, int | None]:
    if home_score is None or away_score is None:
        return {
            "target_home_win": None,
            "target_draw": None,
            "target_away_win": None,
            "target_toto": None,
        }
    if home_score > away_score:
        return {
            "target_home_win": 1,
            "target_draw": 0,
            "target_away_win": 0,
            "target_toto": 0,
        }
    if home_score == away_score:
        return {
            "target_home_win": 0,
            "target_draw": 1,
            "target_away_win": 0,
            "target_toto": 1,
        }
    return {
        "target_home_win": 0,
        "target_draw": 0,
        "target_away_win": 1,
        "target_toto": 2,
    }


RESULT_COLUMNS = [
    "result_season",
    "result_competition",
    "result_match_date",
    "result_kickoff_time",
    "result_home_team",
    "result_away_team",
    "home_score",
    "away_score",
    "result_stadium",
    "result_attendance",
    "result_section",
]

TARGET_COLUMNS = [
    "target_home_win",
    "target_draw",
    "target_away_win",
    "target_toto",
]


def merge_rows(
    feature_rows: list[dict[str, str]],
    results: dict[int, dict[str, Any]],
    include_unplayed: bool,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    merged: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    stats = {
        "feature_rows": len(feature_rows),
        "completed": 0,
        "unplayed_included": 0,
        "unplayed_excluded": 0,
        "missing_result": 0,
    }

    for feature_row in feature_rows:
        match_id = parse_match_id(feature_row.get("jleague_match_id"))
        if match_id in seen_ids:
            raise RuntimeError(
                f"特徴量CSVに同一jleague_match_idが複数あります: {match_id}"
            )
        seen_ids.add(match_id)

        result = results.get(match_id)
        if result is None:
            stats["missing_result"] += 1
            continue

        home_score = result["home_score"]
        away_score = result["away_score"]
        played = home_score is not None and away_score is not None

        if not played and not include_unplayed:
            stats["unplayed_excluded"] += 1
            continue

        output_row: dict[str, Any] = dict(feature_row)
        output_row.update(
            {
                "result_season": result["season"],
                "result_competition": result["competition"],
                "result_match_date": result["match_date"],
                "result_kickoff_time": result["kickoff_time"],
                "result_home_team": result["home_team"],
                "result_away_team": result["away_team"],
                "home_score": home_score,
                "away_score": away_score,
                "result_stadium": result["stadium"],
                "result_attendance": result["attendance"],
                "result_section": result["section"],
            }
        )
        output_row.update(build_targets(home_score, away_score))
        merged.append(output_row)

        if played:
            stats["completed"] += 1
        else:
            stats["unplayed_included"] += 1

    return merged, stats


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()

    feature_path = resolve_feature_path(args.season, args.features)
    output_path = resolve_output_path(args.season, args.output)

    feature_columns, feature_rows = load_feature_rows(feature_path)
    results = load_results(args.season)

    merged_rows, stats = merge_rows(
        feature_rows=feature_rows,
        results=results,
        include_unplayed=args.include_unplayed,
    )

    fieldnames = feature_columns + RESULT_COLUMNS + TARGET_COLUMNS
    write_csv(output_path, fieldnames, merged_rows)

    target_counts = {0: 0, 1: 0, 2: 0}
    for row in merged_rows:
        target = row.get("target_toto")
        if target in target_counts:
            target_counts[int(target)] += 1

    print("=" * 110)
    print("Training Dataset Builder")
    print("=" * 110)
    print(f"season              : {args.season}")
    print(f"input               : {relative_path(feature_path)}")
    print(f"feature rows        : {stats['feature_rows']}")
    print(f"completed included  : {stats['completed']}")
    print(f"unplayed included   : {stats['unplayed_included']}")
    print(f"unplayed excluded   : {stats['unplayed_excluded']}")
    print(f"missing result rows : {stats['missing_result']}")
    print(f"output rows         : {len(merged_rows)}")
    print(f"total columns       : {len(fieldnames)}")
    print(f"home wins           : {target_counts[0]}")
    print(f"draws               : {target_counts[1]}")
    print(f"away wins           : {target_counts[2]}")
    print(f"output              : {relative_path(output_path)}")


if __name__ == "__main__":
    main()
