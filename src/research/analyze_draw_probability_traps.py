from pathlib import Path

import pandas as pd

INPUT_PATH = Path(
    "data/evaluation/toto_2025_prediction_details_v2.csv"
)

OUTPUT_PATH = Path(
    "data/evaluation/draw_research/draw_probability_traps.csv"
)


def summarize(name, df):

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"試合数: {len(df)}")

    if len(df) == 0:
        return None

    summary = pd.DataFrame({
        "average": [
            df["prob_home"].mean(),
            df["prob_draw"].mean(),
            df["prob_away"].mean(),
        ]
    }, index=[
        "prob_home",
        "prob_draw",
        "prob_away",
    ])

    print(summary.to_string(float_format="%.3f"))

    return summary


def main():

    df = pd.read_csv(INPUT_PATH)

    home_correct = df[
        (df.prediction == 1)
        & (df.actual == 1)
    ]

    home_draw = df[
        (df.prediction == 1)
        & (df.actual == 0)
    ]

    away_correct = df[
        (df.prediction == 2)
        & (df.actual == 2)
    ]

    away_draw = df[
        (df.prediction == 2)
        & (df.actual == 0)
    ]

    print("=" * 80)
    print("Draw Probability Trap Research")
    print("=" * 80)

    r1 = summarize(
        "HOME Correct",
        home_correct,
    )

    r2 = summarize(
        "HOME -> DRAW",
        home_draw,
    )

    r3 = summarize(
        "AWAY Correct",
        away_correct,
    )

    r4 = summarize(
        "AWAY -> DRAW",
        away_draw,
    )

    result = pd.concat(
        [
            r1.rename(columns={"average":"home_correct"}),
            r2.rename(columns={"average":"home_draw"}),
            r3.rename(columns={"average":"away_correct"}),
            r4.rename(columns={"average":"away_draw"}),
        ],
        axis=1,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
