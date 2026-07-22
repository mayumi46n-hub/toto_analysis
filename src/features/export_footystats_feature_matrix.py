# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data/features"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "footystats_match_featuresを"
            "1試合1行のワイド形式CSVへ出力します。"
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="対象シーズン",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "出力CSVパス。省略時は"
            "data/features/"
            "footystats_match_features_<season>.csv"
        ),
    )

    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help=(
            "試合日・チーム名・リーグなどの"
            "メタデータ列も出力する"
        ),
    )

    return parser.parse_args()


def resolve_output_path(
    season: int,
    output: Path | None,
) -> Path:
    if output is None:
        return (
            DEFAULT_OUTPUT_DIR
            / (
                "footystats_match_features_"
                f"{season}.csv"
            )
        )

    if output.is_absolute():
        return output

    return PROJECT_ROOT / output


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    return con


def validate_tables(
    con: sqlite3.Connection,
) -> None:
    required_tables = {
        "footystats_match_features",
        "footystats_match_pages",
        "jleague_matches",
    }

    existing_tables = {
        str(row["name"])
        for row in con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        )
    }

    missing = sorted(
        required_tables
        - existing_tables
    )

    if missing:
        raise RuntimeError(
            "必要なテーブルがありません: "
            + ", ".join(missing)
        )


def load_matches(
    con: sqlite3.Connection,
    season: int,
) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT DISTINCT
            f.jleague_match_id,
            p.id AS footystats_page_id,
            p.season,
            p.league,
            p.match_date,
            p.home_team_name,
            p.away_team_name,
            p.home_team_id,
            p.away_team_id,
            jm.competition,
            jm.kickoff_time,
            jm.stadium
        FROM footystats_match_features AS f
        JOIN footystats_match_pages AS p
          ON p.id = f.footystats_page_id
        LEFT JOIN jleague_matches AS jm
          ON jm.jleague_match_id =
             f.jleague_match_id
        WHERE p.season = ?
        ORDER BY f.jleague_match_id
        """,
        (season,),
    ).fetchall()


def load_feature_keys(
    con: sqlite3.Connection,
    season: int,
) -> list[str]:
    rows = con.execute(
        """
        SELECT DISTINCT
            f.feature_key
        FROM footystats_match_features AS f
        JOIN footystats_match_pages AS p
          ON p.id = f.footystats_page_id
        WHERE p.season = ?
        ORDER BY f.feature_key
        """,
        (season,),
    ).fetchall()

    return [
        str(row["feature_key"])
        for row in rows
    ]


def load_feature_values(
    con: sqlite3.Connection,
    season: int,
) -> dict[int, dict[str, float | None]]:
    rows = con.execute(
        """
        SELECT
            f.jleague_match_id,
            f.feature_key,
            f.feature_value
        FROM footystats_match_features AS f
        JOIN footystats_match_pages AS p
          ON p.id = f.footystats_page_id
        WHERE p.season = ?
        ORDER BY
            f.jleague_match_id,
            f.feature_key
        """,
        (season,),
    ).fetchall()

    values: dict[
        int,
        dict[str, float | None],
    ] = {}

    for row in rows:
        match_id = int(
            row["jleague_match_id"]
        )

        feature_key = str(
            row["feature_key"]
        )

        feature_value = row[
            "feature_value"
        ]

        match_values = values.setdefault(
            match_id,
            {},
        )

        if feature_key in match_values:
            existing_value = match_values[
                feature_key
            ]

            if (
                existing_value is not None
                and feature_value is not None
                and float(existing_value)
                != float(feature_value)
            ):
                raise RuntimeError(
                    "同一試合・同一feature_keyに"
                    "異なる値があります: "
                    f"jleague_match_id={match_id}, "
                    f"feature_key={feature_key}, "
                    f"values="
                    f"{existing_value},"
                    f"{feature_value}"
                )

        match_values[
            feature_key
        ] = (
            None
            if feature_value is None
            else float(feature_value)
        )

    return values


def metadata_columns() -> list[str]:
    return [
        "footystats_page_id",
        "season",
        "league",
        "match_date",
        "home_team_name",
        "away_team_name",
        "home_team_id",
        "away_team_id",
        "competition",
        "kickoff_time",
        "stadium",
    ]


def build_output_rows(
    matches: list[sqlite3.Row],
    feature_keys: list[str],
    feature_values: dict[
        int,
        dict[str, float | None],
    ],
    include_metadata: bool,
) -> tuple[
    list[str],
    list[dict[str, Any]],
]:
    fieldnames = [
        "jleague_match_id",
    ]

    if include_metadata:
        fieldnames.extend(
            metadata_columns()
        )

    fieldnames.extend(
        feature_keys
    )

    output_rows: list[
        dict[str, Any]
    ] = []

    for match in matches:
        match_id = int(
            match["jleague_match_id"]
        )

        output_row: dict[
            str,
            Any,
        ] = {
            "jleague_match_id": match_id,
        }

        if include_metadata:
            for column in metadata_columns():
                output_row[column] = (
                    match[column]
                )

        match_feature_values = (
            feature_values.get(
                match_id,
                {},
            )
        )

        for feature_key in feature_keys:
            output_row[feature_key] = (
                match_feature_values.get(
                    feature_key
                )
            )

        output_rows.append(
            output_row
        )

    return fieldnames, output_rows


def write_csv(
    output_path: Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
) -> None:
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
            fieldnames=fieldnames,
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerows(
            rows
        )


def relative_path(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
    except ValueError:
        return str(path)


def count_non_null_features(
    rows: list[dict[str, Any]],
    feature_keys: list[str],
) -> int:
    count = 0

    for row in rows:
        for feature_key in feature_keys:
            if row.get(
                feature_key
            ) is not None:
                count += 1

    return count


def main() -> None:
    args = parse_args()

    output_path = resolve_output_path(
        season=args.season,
        output=args.output,
    )

    con = connect_database()

    try:
        validate_tables(
            con
        )

        matches = load_matches(
            con=con,
            season=args.season,
        )

        feature_keys = load_feature_keys(
            con=con,
            season=args.season,
        )

        feature_values = load_feature_values(
            con=con,
            season=args.season,
        )

    finally:
        con.close()

    if not matches:
        raise RuntimeError(
            f"{args.season}年の特徴量対象試合が"
            "見つかりません"
        )

    if not feature_keys:
        raise RuntimeError(
            f"{args.season}年のfeature_keyが"
            "見つかりません"
        )

    fieldnames, rows = (
        build_output_rows(
            matches=matches,
            feature_keys=feature_keys,
            feature_values=feature_values,
            include_metadata=(
                args.include_metadata
            ),
        )
    )

    write_csv(
        output_path=output_path,
        fieldnames=fieldnames,
        rows=rows,
    )

    non_null_count = (
        count_non_null_features(
            rows=rows,
            feature_keys=feature_keys,
        )
    )

    print("=" * 110)
    print(
        "FootyStats Feature Matrix Export"
    )
    print("=" * 110)
    print(
        f"season              : "
        f"{args.season}"
    )
    print(
        f"matches             : "
        f"{len(rows)}"
    )
    print(
        f"feature columns     : "
        f"{len(feature_keys)}"
    )
    print(
        f"metadata columns    : "
        f"{len(metadata_columns()) if args.include_metadata else 0}"
    )
    print(
        f"total columns       : "
        f"{len(fieldnames)}"
    )
    print(
        f"non-null features   : "
        f"{non_null_count}"
    )
    print(
        f"output              : "
        f"{relative_path(output_path)}"
    )

    print()
    print("FIRST MATCH")
    print("-" * 110)

    first_row = rows[0]

    print(
        f"jleague_match_id    : "
        f"{first_row['jleague_match_id']}"
    )

    shown = 0

    for feature_key in feature_keys:
        value = first_row.get(
            feature_key
        )

        if value is None:
            continue

        print(
            f"{feature_key} = {value}"
        )

        shown += 1

        if shown >= 15:
            break


if __name__ == "__main__":
    main()
