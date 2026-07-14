import argparse
import sqlite3
from pathlib import Path

import joblib
import pandas as pd

from normalize_toto_team import normalize_toto_team_name


DB_PATH = Path("data/toto.db")
MODEL_PATH = Path(
    "data/models/gradient_boosting_v1.pkl"
)

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
    normalized = normalize_toto_team_name(
        team_name
    )

    return EXTRA_TEAM_ALIASES.get(
        normalized,
        normalized,
    )


def result_name(result):
    names = {
        1: "ホーム勝ち",
        0: "引分",
        2: "アウェイ勝ち",
    }

    try:
        key = int(result)
    except (TypeError, ValueError):
        return str(result)

    return names.get(
        key,
        str(result),
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

    missing = (
        required_keys
        - set(artifact)
    )

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


def load_toto_matches(
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

            "saved_jleague_match_id": (
                row["jleague_match_id"]
            ),
        })

    return matches


def toto_date_to_jleague_like(
    match_date,
):
    """
    toto側:
        20251130

    Jリーグ側:
        25/11/30(日)

    LIKE用:
        25/11/30%
    """

    if (
        match_date is None
        or len(match_date) != 8
        or not match_date.isdigit()
    ):
        return None

    return (
        f"{match_date[2:4]}/"
        f"{match_date[4:6]}/"
        f"{match_date[6:8]}%"
    )


def find_jleague_match(
    con,
    toto_match,
):
    match_date = toto_match["match_date"]

    date_like = toto_date_to_jleague_like(
        match_date
    )

    if date_like is None:
        return None, (
            "開催日が未登録または不正です"
        )

    season = int(
        match_date[:4]
    )

    rows = con.execute("""
        SELECT
            jm.jleague_match_id,
            jm.season,
            jm.competition,
            jm.match_date,
            jm.kickoff_time,
            jm.home_team,
            jm.away_team,
            jm.home_score,
            jm.away_score
        FROM jleague_matches AS jm
        WHERE jm.season = ?
          AND jm.match_date LIKE ?
        ORDER BY
            jm.jleague_match_id
    """, (
        season,
        date_like,
    )).fetchall()

    candidates = []

    for row in rows:
        jleague_home = normalize_team(
            row["home_team"]
        )
        jleague_away = normalize_team(
            row["away_team"]
        )

        if (
            jleague_home
            == toto_match["home_team"]
            and jleague_away
            == toto_match["away_team"]
        ):
            candidates.append(row)

    if not candidates:
        return None, (
            "開催日・ホーム・アウェイで"
            "Jリーグ試合と照合できません"
        )

    if len(candidates) > 1:
        return None, (
            f"候補が複数あります"
            f"（{len(candidates)}件）"
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

    input_values = {
        column: feature_row[column]
        for column in feature_columns
    }

    return pd.DataFrame(
        [input_values],
        columns=feature_columns,
    )


def probability_map(
    model,
    probabilities,
):
    return {
        int(class_label): probability
        for class_label, probability
        in zip(
            model.classes_,
            probabilities,
        )
    }


def predict_round(
    con,
    artifact,
    round_no,
):
    model = artifact["model"]

    feature_columns = (
        artifact["feature_columns"]
    )

    toto_matches = load_toto_matches(
        con=con,
        round_no=round_no,
    )

    if not toto_matches:
        raise RuntimeError(
            f"第{round_no}回の試合がありません"
        )

    print()
    print(f"第{round_no}回 toto 再予測")
    print("=" * 72)

    predicted_count = 0
    correct_count = 0
    unmatched_count = 0
    linked_count = 0

    for toto_match in toto_matches:
        match_no = toto_match["match_no"]

        print()
        print(
            f"[{match_no:02d}] "
            f"{toto_match['match_date']} "
            f"{toto_match['home_team_raw']} "
            f"vs "
            f"{toto_match['away_team_raw']}"
        )

        if (
            toto_match["home_team_raw"]
            != toto_match["home_team"]
            or toto_match["away_team_raw"]
            != toto_match["away_team"]
        ):
            print(
                "     正規化: "
                f"{toto_match['home_team']} "
                f"vs "
                f"{toto_match['away_team']}"
            )

        (
            jleague_match,
            error_message,
        ) = find_jleague_match(
            con=con,
            toto_match=toto_match,
        )

        if jleague_match is None:
            unmatched_count += 1

            print(
                f"     対象外: {error_message}"
            )

            continue

        jleague_match_id = (
            jleague_match[
                "jleague_match_id"
            ]
        )

        save_jleague_match_id(
            con=con,
            round_no=round_no,
            match_no=match_no,
            jleague_match_id=(
                jleague_match_id
            ),
        )

        linked_count += 1

        feature_row = load_feature_row(
            con=con,
            season=jleague_match["season"],
            jleague_match_id=(
                jleague_match_id
            ),
        )

        if feature_row is None:
            unmatched_count += 1

            print(
                "     対象外: "
                "特徴量が見つかりません"
            )

            continue

        X = build_input_frame(
            feature_row=feature_row,
            feature_columns=feature_columns,
        )

        prediction = int(
            model.predict(X)[0]
        )

        probabilities = (
            model.predict_proba(X)[0]
        )

        probs = probability_map(
            model=model,
            probabilities=probabilities,
        )

        actual = None

        if (
            toto_match["result"]
            is not None
            and str(
                toto_match["result"]
            ) in {"0", "1", "2"}
        ):
            actual = int(
                toto_match["result"]
            )

        is_correct = (
            actual is not None
            and prediction == actual
        )

        predicted_count += 1

        if is_correct:
            correct_count += 1

        print(
            "     Jリーグ照合: "
            f"ID={jleague_match_id} "
            f"{jleague_match['season']} "
            f"{jleague_match['match_date']} "
            f"{jleague_match['competition']}"
        )

        print(
            "     Jリーグカード: "
            f"{jleague_match['home_team']} "
            f"vs "
            f"{jleague_match['away_team']}"
        )

        print(
            f"     AI予想: {prediction} "
            f"({result_name(prediction)})"
        )

        if actual is not None:
            mark = (
                "○"
                if is_correct
                else "×"
            )

            print(
                f"     実際結果: {actual} "
                f"({result_name(actual)}) "
                f"{mark}"
            )
        else:
            print(
                "     実際結果: 未確定"
            )

        print(
            "     "
            f"1: {probs.get(1, 0.0) * 100:5.1f}%  "
            f"0: {probs.get(0, 0.0) * 100:5.1f}%  "
            f"2: {probs.get(2, 0.0) * 100:5.1f}%"
        )

    con.commit()

    print()
    print("=" * 72)
    print("集計")
    print("-" * 72)

    print(
        f"toto試合数: {len(toto_matches)}"
    )

    print(
        f"JリーグID保存: {linked_count}"
    )

    print(
        f"予測可能: {predicted_count}"
    )

    print(
        f"照合不可・対象外: {unmatched_count}"
    )

    print(
        f"的中: {correct_count}"
        f" / {predicted_count}"
    )

    if predicted_count:
        accuracy = (
            correct_count
            / predicted_count
        )

        print(
            f"的中率: {accuracy:.2%}"
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "指定したtoto回を、"
            "開催日・ホーム・アウェイで"
            "Jリーグ試合と照合し、"
            "GradientBoostingモデルで"
            "再予測します。"
        )
    )

    parser.add_argument(
        "round_no",
        type=int,
        help="toto回号。例: 1591",
    )

    args = parser.parse_args()

    artifact = load_artifact()

    con = sqlite3.connect(
        DB_PATH
    )

    con.row_factory = sqlite3.Row

    try:
        predict_round(
            con=con,
            artifact=artifact,
            round_no=args.round_no,
        )
    finally:
        con.close()


if __name__ == "__main__":
    main()