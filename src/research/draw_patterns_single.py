from itertools import combinations
from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_PATH = Path(
    "data/evaluation/draw_research/"
    "draw_patterns_single.csv"
)


CONDITIONS = [
    {
        "name": "Elo差 <= 30",
        "column": "elo_diff",
        "threshold": 30,
    },
    {
        "name": "Elo差 <= 50",
        "column": "elo_diff",
        "threshold": 50,
    },
    {
        "name": "順位差 <= 2",
        "column": "rank_diff",
        "threshold": 2,
    },
    {
        "name": "順位差 <= 4",
        "column": "rank_diff",
        "threshold": 4,
    },
    {
        "name": "勝点差 <= 3",
        "column": "points_diff",
        "threshold": 3,
    },
    {
        "name": "勝点差 <= 5",
        "column": "points_diff",
        "threshold": 5,
    },
    {
        "name": "得失点差 <= 3",
        "column": "goal_diff_diff",
        "threshold": 3,
    },
    {
        "name": "得失点差 <= 5",
        "column": "goal_diff_diff",
        "threshold": 5,
    },
    {
        "name": "フォーム差 <= 2",
        "column": "form_diff",
        "threshold": 2,
    },
    {
        "name": "フォーム差 <= 3",
        "column": "form_diff",
        "threshold": 3,
    },
]


def load_data():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = {
        "result",
        *[
            condition["column"]
            for condition in CONDITIONS
        ],
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise RuntimeError(
            "必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    df = df[
        df["result"]
        .astype(str)
        .str.strip()
        .isin({"0", "1", "2"})
    ].copy()

    for column in {
        condition["column"]
        for condition in CONDITIONS
    }:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df["is_draw"] = (
        df["result"]
        .astype(str)
        .str.strip()
        .eq("0")
    )

    return df


def evaluate_condition(
    df,
    condition,
):
    column = condition["column"]
    threshold = condition["threshold"]

    mask = (
        df[column].abs()
        <= threshold
    )

    matched = df[mask].copy()

    matches = len(matched)
    draws = int(
        matched["is_draw"].sum()
    )

    draw_rate = (
        draws / matches
        if matches
        else 0.0
    )

    return {
        "condition": condition["name"],
        "column": column,
        "threshold": threshold,
        "matches": matches,
        "draws": draws,
        "draw_rate": draw_rate,
    }


def main():
    df = load_data()

    overall_draw_rate = (
        df["is_draw"].mean()
    )

    rows = [
        evaluate_condition(
            df=df,
            condition=condition,
        )
        for condition in CONDITIONS
    ]

    result = pd.DataFrame(rows)

    result["lift_vs_overall"] = (
        result["draw_rate"]
        - overall_draw_rate
    )

    result = result.sort_values(
        by=[
            "draw_rate",
            "matches",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)

    result.insert(
        0,
        "rank",
        range(1, len(result) + 1),
    )

    print("=" * 88)
    print("Draw Pattern Miner - Single Conditions")
    print("=" * 88)
    print(f"対象試合数: {len(df)}")
    print(
        f"全体引分率: "
        f"{overall_draw_rate:.2%}"
    )
    print()

    print(
        result.to_string(
            index=False,
            formatters={
                "draw_rate": "{:.2%}".format,
                "lift_vs_overall": (
                    "{:+.2%}".format
                ),
            },
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print(f"CSV Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
