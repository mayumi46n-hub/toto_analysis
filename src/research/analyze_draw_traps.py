from pathlib import Path

import pandas as pd

INPUT_PATH = Path(
    "data/evaluation/toto_2025_prediction_details_v2.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


FEATURES = [
    "elo_diff",
    "points_diff",
    "goal_diff_diff",
    "form_diff",
    "rank_diff",
    "elo_expected_draw_base",
]


def summarize(name, df):

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    print(f"試合数: {len(df)}")

    if len(df) == 0:
        return

    result = (
        df[FEATURES]
        .mean()
        .to_frame("average")
    )

    print(
        result.to_string(
            float_format="%.3f"
        )
    )

    return result


def main():

    df = pd.read_csv(INPUT_PATH)

    for c in FEATURES:
        df[c] = pd.to_numeric(
            df[c],
            errors="coerce",
        )

    df["prediction"] = (
        df["prediction"]
        .astype(int)
    )

    df["actual"] = (
        df["actual"]
        .astype(int)
    )

    home_correct = df[
        (df.prediction == 1)
        &
        (df.actual == 1)
    ]

    home_draw_trap = df[
        (df.prediction == 1)
        &
        (df.actual == 0)
    ]

    away_correct = df[
        (df.prediction == 2)
        &
        (df.actual == 2)
    ]

    away_draw_trap = df[
        (df.prediction == 2)
        &
        (df.actual == 0)
    ]

    print("=" * 80)
    print("Draw Trap Research v1")
    print("=" * 80)

    r1 = summarize(
        "HOME Prediction Correct",
        home_correct,
    )

    r2 = summarize(
        "HOME -> DRAW Trap",
        home_draw_trap,
    )

    r3 = summarize(
        "AWAY Prediction Correct",
        away_correct,
    )

    r4 = summarize(
        "AWAY -> DRAW Trap",
        away_draw_trap,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if r1 is not None:
        r1.columns = [
            "home_correct"
        ]

    if r2 is not None:
        r2.columns = [
            "home_draw_trap"
        ]

    if r3 is not None:
        r3.columns = [
            "away_correct"
        ]

    if r4 is not None:
        r4.columns = [
            "away_draw_trap"
        ]

    result = pd.concat(
        [
            r1,
            r2,
            r3,
            r4,
        ],
        axis=1,
    )

    output = (
        OUTPUT_DIR
        / "draw_trap_research_v1.csv"
    )

    result.to_csv(
        output,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print(output)


if __name__ == "__main__":
    main()
