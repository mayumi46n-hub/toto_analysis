import sqlite3
from pathlib import Path

import joblib
import pandas as pd

from normalize_toto_team import normalize_toto_team_name


DB_PATH = Path("data/toto.db")
MODEL_PATH = Path(
    "data/models/gradient_boosting_v2.pkl"
)
OUTPUT_PATH = Path(
    "data/evaluation/toto_2025_evaluation.csv"
)

TARGET_YEAR = 2025
FEATURE_VERSION = 1


EXTRA_TEAM_ALIASES = {
    "川崎Ｆ": "川崎フロンターレ",
    "千葉": "ジェフユナイテッド市原・千葉",
    "横浜FM": "横浜Ｆ・マリノス",
    "横浜ＦＭ": "横浜Ｆ・マリノス",
    "東京Ｖ": "東京ヴェルディ",
    "Ｃ大阪": "セレッソ大阪",
    "C大阪": "セレッソ大阪",
    "FC東京": "ＦＣ東京",
    "ＦＣ東京": "ＦＣ東京",
}


def normalize_team(team_name):
    if team_name is None:
        return None

    normalized = normalize_toto_team_name(
        team_name
    )

    return EXTRA_TEAM_ALIASES.get(
        normalized,
        normalized,
    )


def load_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"モデルがありません: {MODEL_PATH}"
        )

    artifact = joblib.load(
        MODEL_PATH
    )

    required_keys = {
        "model",
        "feature_columns",
    }

    missing = required_keys - set(artifact)

    if missing:
        raise RuntimeError(
            "モデル情報が不足しています: "
            + ", ".join(sorted(missing))
        )

    print("Model Loaded")
    print("-" * 72)
    print(f"Path: {MODEL_PATH}")
    print(
        "Name: "
        f"{artifact.get('model_name', 'unknown')}"
    )
    print(
        "Accuracy: "
        f"{artifact.get('test_accuracy', 0.0):.4f}"
    )

    return artifact


def ensure_database_columns(con):
    columns = {
        row["name"]
        for row in con.execute(
            "PRAGMA table_info(toto_matches)"
        ).fetchall()
    }

    if "match_date" not in columns:
        raise RuntimeError(
            "toto_matches.match_date がありません。"
            "先に build_toto_round_dates.py を"
            "実行してください。"
        )

    if "jleague_match_id" not in columns:
        con.execute("""
            ALTER TABLE toto_matches
            ADD COLUMN jleague_match_id INTEGER
        """)

        con.commit()


def load_target_rounds(con):
    rows = con.execute("""
        SELECT
            round_no,
            COUNT(*) AS match_count,
            SUM(
                CASE
                    WHEN match_date IS NOT NULL
                     AND match_date != ''
                    THEN 1
                    ELSE 0
                END
            ) AS dated_count
        FROM toto_matches
        WHERE match_date >= ?
          AND match_date <= ?
        GROUP BY round_no
        HAVING COUNT(*) = 13
           AND dated_count = 13
        ORDER BY round_no
    """, (
        f"{TARGET_YEAR}0101",
        f"{TARGET_YEAR}1231",
    )).fetchall()

    return [
        row["round_no"]
        for row in rows
    ]


def load_round_matches(
    con,
    round_no,
):
    rows = con.execute("""
        SELECT
            round_no,
            match_no,
            match_date,
            home_team,
            away_team,
            result,
            home_score,
            away_score,
            jleague_match_id
        FROM toto_matches
        WHERE round_no = ?
        ORDER BY match_no
    """, (
        round_no,
    )).fetchall()

    matches = []

    for row in rows:
        matches.append({
            "round_no": row["round_no"],
            "match_no": row["match_no"],
            "match_date": row["match_date"],

            "home_team_raw": row["home_team"],
            "away_team_raw": row["away_team"],

            "home_team": normalize_team(
                row["home_team"]
            ),
            "away_team": normalize_team(
                row["away_team"]
            ),

            "result": row["result"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],

            "jleague_match_id": (
                row["jleague_match_id"]
            ),
        })

    return matches


def make_jleague_date_pattern(
    match_date,
):
    if (
        match_date is None
        or len(match_date) != 8
        or not match_date.isdigit()
    ):
        return None

    return (
        match_date[2:4]
        + "/"
        + match_date[4:6]
        + "/"
        + match_date[6:8]
        + "%"
    )


def load_saved_jleague_match(
    con,
    jleague_match_id,
):
    if jleague_match_id is None:
        return None

    return con.execute("""
        SELECT
            jleague_match_id,
            season,
            competition,
            match_date,
            home_team,
            away_team,
            home_score,
            away_score
        FROM jleague_matches
        WHERE jleague_match_id = ?
    """, (
        jleague_match_id,
    )).fetchone()


def find_jleague_match(
    con,
    toto_match,
):
    saved = load_saved_jleague_match(
        con,
        toto_match["jleague_match_id"],
    )

    if saved is not None:
        return saved, None

    match_date = toto_match["match_date"]

    date_pattern = make_jleague_date_pattern(
        match_date
    )

    if date_pattern is None:
        return None, "開催日なし"

    season = int(
        match_date[:4]
    )

    rows = con.execute("""
        SELECT
            jm.jleague_match_id,
            jm.season,
            jm.competition,
            jm.match_date,
            jm.home_team,
            jm.away_team,
            jm.home_score,
            jm.away_score
        FROM jleague_matches AS jm
        INNER JOIN match_features_season AS mf
            ON mf.season = jm.season
           AND mf.jleague_match_id =
               jm.jleague_match_id
           AND mf.feature_version = ?
        INNER JOIN match_elo AS elo
            ON elo.season = jm.season
           AND elo.jleague_match_id =
               jm.jleague_match_id
        INNER JOIN match_rest AS rest
            ON rest.season = jm.season
           AND rest.jleague_match_id =
               jm.jleague_match_id
        WHERE jm.season = ?
          AND jm.match_date LIKE ?
        ORDER BY jm.jleague_match_id
    """, (
        FEATURE_VERSION,
        season,
        date_pattern,
    )).fetchall()

    candidates = []

    for row in rows:
        home_team = normalize_team(
            row["home_team"]
        )
        away_team = normalize_team(
            row["away_team"]
        )

        if (
            home_team
            == toto_match["home_team"]
            and away_team
            == toto_match["away_team"]
        ):
            candidates.append(row)

    if not candidates:
        return None, "Jリーグ対象外または照合不可"

    if len(candidates) > 1:
        return (
            None,
            f"候補複数（{len(candidates)}件）",
        )

    return candidates[0], None


def save_jleague_match_id(
    con,
    round_no,
    match_no,
    jleague_match_id,
):
    con.execute("""
        UPDATE toto_matches
        SET jleague_match_id = ?
        WHERE round_no = ?
          AND match_no = ?
    """, (
        jleague_match_id,
        round_no,
        match_no,
    ))


def load_feature_row(
    con,
    season,
    jleague_match_id,
):
    row = con.execute("""
        SELECT
            mf.home_rank,
            mf.away_rank,
            mf.rank_diff,

            mf.home_played,
            mf.away_played,

            mf.home_points,
            mf.away_points,
            mf.points_diff,

            mf.home_goal_diff,
            mf.away_goal_diff,
            mf.goal_diff_diff,

            mf.home_form_matches,
            mf.away_form_matches,
            mf.home_form_points,
            mf.away_form_points,
            mf.form_diff,

            mf.home_home_form_matches,
            mf.away_away_form_matches,
            mf.home_home_form_points,
            mf.away_away_form_points,
            mf.venue_form_diff,

            mf.h2h_last5_matches,
            mf.h2h_last5_home_points,
            mf.h2h_last5_away_points,
            mf.h2h_last5_diff,

            mf.h2h_last10_matches,
            mf.h2h_last10_home_points,
            mf.h2h_last10_away_points,
            mf.h2h_last10_diff,

            mf.h2h_all_matches,
            mf.h2h_all_home_points,
            mf.h2h_all_away_points,
            mf.h2h_all_diff,

            mf.h2h_same_venue_last5_matches,
            mf.h2h_same_venue_last5_home_points,
            mf.h2h_same_venue_last5_away_points,
            mf.h2h_same_venue_last5_diff,

            elo.home_elo,
            elo.away_elo,
            elo.elo_diff,

            elo.expected_home
                AS elo_expected_home,

            elo.expected_draw_base
                AS elo_expected_draw_base,

            elo.expected_away
                AS elo_expected_away,

            rest.home_rest_days,
            rest.away_rest_days,
            rest.rest_diff,
            rest.home_first_match,
            rest.away_first_match

        FROM match_features_season AS mf

        INNER JOIN match_elo AS elo
            ON elo.season = mf.season
           AND elo.jleague_match_id =
               mf.jleague_match_id

        INNER JOIN match_rest AS rest
            ON rest.season = mf.season
           AND rest.jleague_match_id =
               mf.jleague_match_id

        WHERE mf.feature_version = ?
          AND mf.season = ?
          AND mf.jleague_match_id = ?
    """, (
        FEATURE_VERSION,
        season,
        jleague_match_id,
    )).fetchone()

    if row is None:
        return None

    return dict(row)


def build_input_frame(
    feature_row,
    feature_columns,
):
    missing = [
        column
        for column in feature_columns
        if column not in feature_row
    ]

    if missing:
        raise RuntimeError(
            "不足している特徴量: "
            + ", ".join(missing)
        )

    values = {
        column: feature_row[column]
        for column in feature_columns
    }

    return pd.DataFrame(
        [values],
        columns=feature_columns,
    )


def parse_result(result):
    if result is None:
        return None

    result_text = str(result).strip()

    if result_text not in {
        "0",
        "1",
        "2",
    }:
        return None

    return int(result_text)


def evaluate_round(
    con,
    model,
    feature_columns,
    round_no,
):
    matches = load_round_matches(
        con,
        round_no,
    )

    total_count = len(matches)
    linked_count = 0
    predicted_count = 0
    correct_count = 0
    unresolved_count = 0
    excluded_count = 0

    j1_count = 0
    j2_count = 0
    other_league_count = 0

    prediction_details = []

    for toto_match in matches:
        (
            jleague_match,
            error_message,
        ) = find_jleague_match(
            con,
            toto_match,
        )

        if jleague_match is None:
            excluded_count += 1

            prediction_details.append({
                "round_no": round_no,
                "match_no": toto_match["match_no"],
                "match_date": toto_match["match_date"],
                "home_team": toto_match[
                    "home_team_raw"
                ],
                "away_team": toto_match[
                    "away_team_raw"
                ],
                "jleague_match_id": None,
                "league": None,
                "actual": parse_result(
                    toto_match["result"]
                ),
                "prediction": None,
                "correct": None,
                "status": error_message,
            })

            continue

        jleague_match_id = (
            jleague_match[
                "jleague_match_id"
            ]
        )

        save_jleague_match_id(
            con,
            round_no,
            toto_match["match_no"],
            jleague_match_id,
        )

        linked_count += 1

        competition = str(
            jleague_match["competition"]
        )

        if competition.startswith("Ｊ１"):
            league = "J1"
            j1_count += 1
        elif competition.startswith("Ｊ２"):
            league = "J2"
            j2_count += 1
        else:
            league = competition
            other_league_count += 1

        feature_row = load_feature_row(
            con,
            jleague_match["season"],
            jleague_match_id,
        )

        if feature_row is None:
            excluded_count += 1

            prediction_details.append({
                "round_no": round_no,
                "match_no": toto_match["match_no"],
                "match_date": toto_match["match_date"],
                "home_team": toto_match[
                    "home_team_raw"
                ],
                "away_team": toto_match[
                    "away_team_raw"
                ],
                "jleague_match_id": (
                    jleague_match_id
                ),
                "league": league,
                "actual": parse_result(
                    toto_match["result"]
                ),
                "prediction": None,
                "correct": None,
                "status": "特徴量なし",
            })

            continue

        X = build_input_frame(
            feature_row,
            feature_columns,
        )

        prediction = int(
            model.predict(X)[0]
        )

        probabilities = (
            model.predict_proba(X)[0]
        )

        probability_by_class = {
            int(class_label): float(probability)
            for class_label, probability
            in zip(
                model.classes_,
                probabilities,
            )
        }

        actual = parse_result(
            toto_match["result"]
        )

        if actual is None:
            unresolved_count += 1
            correct = None
            status = "結果未確定"
        else:
            predicted_count += 1
            correct = int(
                prediction == actual
            )

            if correct:
                correct_count += 1

            status = "OK"

        prediction_details.append({
            "round_no": round_no,
            "match_no": toto_match["match_no"],
            "match_date": toto_match["match_date"],
            "home_team": toto_match[
                "home_team_raw"
            ],
            "away_team": toto_match[
                "away_team_raw"
            ],
            "jleague_match_id": (
                jleague_match_id
            ),
            "league": league,
            "actual": actual,
            "prediction": prediction,
            "correct": correct,
            "prob_home": probability_by_class.get(
                1,
                0.0,
            ),
            "prob_draw": probability_by_class.get(
                0,
                0.0,
            ),
            "prob_away": probability_by_class.get(
                2,
                0.0,
            ),
            "status": status,
        })

    accuracy = (
        correct_count / predicted_count
        if predicted_count
        else None
    )

    summary = {
        "round_no": round_no,
        "total_matches": total_count,
        "linked_matches": linked_count,
        "predicted_matches": predicted_count,
        "correct_matches": correct_count,
        "accuracy": accuracy,
        "excluded_matches": excluded_count,
        "unresolved_matches": unresolved_count,
        "j1_matches": j1_count,
        "j2_matches": j2_count,
        "other_league_matches": (
            other_league_count
        ),
    }

    return summary, prediction_details


def print_round_summary(summary):
    accuracy = summary["accuracy"]

    accuracy_text = (
        f"{accuracy:.2%}"
        if accuracy is not None
        else "-"
    )

    print(
        f"第{summary['round_no']}回 "
        f"J連携={summary['linked_matches']:2d}/"
        f"{summary['total_matches']:2d} "
        f"予測={summary['predicted_matches']:2d} "
        f"的中={summary['correct_matches']:2d} "
        f"的中率={accuracy_text:>7} "
        f"対象外={summary['excluded_matches']:2d}"
    )


def save_results(
    round_summaries,
    prediction_details,
):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_df = pd.DataFrame(
        round_summaries
    )

    details_df = pd.DataFrame(
        prediction_details
    )

    summary_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    detail_path = OUTPUT_PATH.with_name(
        "toto_2025_prediction_details.csv"
    )

    details_df.to_csv(
        detail_path,
        index=False,
        encoding="utf-8-sig",
    )

    return OUTPUT_PATH, detail_path


def print_total_summary(round_summaries):
    if not round_summaries:
        print("評価対象がありません")
        return

    valid_summaries = [
        row
        for row in round_summaries
        if row["predicted_matches"] > 0
    ]

    total_rounds = len(
        round_summaries
    )

    total_matches = sum(
        row["total_matches"]
        for row in round_summaries
    )

    total_linked = sum(
        row["linked_matches"]
        for row in round_summaries
    )

    total_predicted = sum(
        row["predicted_matches"]
        for row in round_summaries
    )

    total_correct = sum(
        row["correct_matches"]
        for row in round_summaries
    )

    total_excluded = sum(
        row["excluded_matches"]
        for row in round_summaries
    )

    total_accuracy = (
        total_correct / total_predicted
        if total_predicted
        else 0.0
    )

    print()
    print("=" * 72)
    print("2025年 toto AI評価結果")
    print("=" * 72)
    print(f"対象回数: {total_rounds}")
    print(f"総試合数: {total_matches}")
    print(f"Jリーグ連携: {total_linked}")
    print(f"予測可能: {total_predicted}")
    print(f"対象外: {total_excluded}")
    print(
        f"総的中: {total_correct}"
        f" / {total_predicted}"
    )
    print(
        f"全体的中率: {total_accuracy:.2%}"
    )

    if valid_summaries:
        best = max(
            valid_summaries,
            key=lambda row: row["accuracy"],
        )

        worst = min(
            valid_summaries,
            key=lambda row: row["accuracy"],
        )

        complete_rounds = [
            row
            for row in valid_summaries
            if row["predicted_matches"] == 13
        ]

        ten_or_more = [
            row
            for row in complete_rounds
            if row["correct_matches"] >= 10
        ]

        print()
        print(
            "最高回: "
            f"第{best['round_no']}回 "
            f"{best['correct_matches']}"
            f"/{best['predicted_matches']} "
            f"({best['accuracy']:.2%})"
        )

        print(
            "最低回: "
            f"第{worst['round_no']}回 "
            f"{worst['correct_matches']}"
            f"/{worst['predicted_matches']} "
            f"({worst['accuracy']:.2%})"
        )

        print(
            "13試合すべて予測できた回: "
            f"{len(complete_rounds)}"
        )

        print(
            "10試合以上的中した回: "
            f"{len(ten_or_more)}"
        )


def main():
    artifact = load_artifact()

    model = artifact["model"]
    feature_columns = (
        artifact["feature_columns"]
    )

    con = sqlite3.connect(
        DB_PATH
    )

    con.row_factory = sqlite3.Row

    try:
        ensure_database_columns(con)

        round_numbers = load_target_rounds(
            con
        )

        print()
        print("2025年 toto 一括評価")
        print("=" * 72)
        print(
            f"対象回数: {len(round_numbers)}"
        )
        print()

        round_summaries = []
        prediction_details = []

        for round_no in round_numbers:
            summary, details = evaluate_round(
                con=con,
                model=model,
                feature_columns=feature_columns,
                round_no=round_no,
            )

            round_summaries.append(
                summary
            )

            prediction_details.extend(
                details
            )

            print_round_summary(
                summary
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()

    print_total_summary(
        round_summaries
    )

    (
        summary_path,
        detail_path,
    ) = save_results(
        round_summaries,
        prediction_details,
    )

    print()
    print("CSV Saved")
    print("-" * 72)
    print(f"回別集計: {summary_path}")
    print(f"試合別詳細: {detail_path}")


if __name__ == "__main__":
    main()
