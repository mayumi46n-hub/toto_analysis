import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("data/toto.db")
OUTPUT_PATH = Path("data/training_data_v1.csv")
FEATURE_VERSION = 1


def connect_db():
    return sqlite3.connect(DB_PATH)


def load_training_rows(con):
    cursor = con.execute("""
        SELECT
            season,
            league,

            home_rank,
            away_rank,
            rank_diff,

            home_played,
            away_played,

            home_points,
            away_points,
            points_diff,

            home_goal_diff,
            away_goal_diff,
            goal_diff_diff,

            home_form_matches,
            away_form_matches,

            home_form_points,
            away_form_points,
            form_diff,

            home_home_form_matches,
            away_away_form_matches,
            home_home_form_points,
            away_away_form_points,
            venue_form_diff,

            h2h_last5_matches,
            h2h_last5_home_points,
            h2h_last5_away_points,
            h2h_last5_diff,

            h2h_last10_matches,
            h2h_last10_home_points,
            h2h_last10_away_points,
            h2h_last10_diff,

            h2h_all_matches,
            h2h_all_home_points,
            h2h_all_away_points,
            h2h_all_diff,

            h2h_same_venue_last5_matches,
            h2h_same_venue_last5_home_points,
            h2h_same_venue_last5_away_points,
            h2h_same_venue_last5_diff,

            result
        FROM match_features_season
        WHERE feature_version = ?
        ORDER BY
            season,
            jleague_match_id
    """, (FEATURE_VERSION,))

    column_names = [
        description[0]
        for description in cursor.description
    ]

    rows = [
        dict(zip(column_names, row))
        for row in cursor.fetchall()
    ]

    return column_names, rows


def validate_rows(rows):
    if not rows:
        raise RuntimeError(
            "学習データが0件です。"
            "match_features_seasonを確認してください。"
        )

    valid_results = {"1", "0", "2"}

    invalid_result_count = sum(
        row["result"] not in valid_results
        for row in rows
    )

    if invalid_result_count:
        raise RuntimeError(
            f"不正なresultが"
            f"{invalid_result_count}件あります"
        )

    null_count = sum(
        value is None
        for row in rows
        for value in row.values()
    )

    if null_count:
        raise RuntimeError(
            f"NULL値が{null_count}個あります"
        )


def export_csv(column_names, rows):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=column_names,
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    con = connect_db()

    try:
        column_names, rows = load_training_rows(con)
    finally:
        con.close()

    validate_rows(rows)
    export_csv(column_names, rows)

    seasons = sorted({
        row["season"]
        for row in rows
    })

    print("学習データ作成完了")
    print()
    print(f"出力: {OUTPUT_PATH}")
    print(f"件数: {len(rows)}")
    print(f"列数: {len(column_names)}")
    print(f"対象年度: {seasons[0]}〜{seasons[-1]}")
    print(f"Feature Version: {FEATURE_VERSION}")


if __name__ == "__main__":
    main()