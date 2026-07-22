from itertools import combinations
from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)

MIN_MATCHES = 300
MIN_DRAW_RATE = 0.30


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


def condition_mask(
    df,
    condition,
):
    return (
        df[condition["column"]].abs()
        <= condition["threshold"]
    )


def evaluate_pattern(
    df,
    conditions,
):
    mask = pd.Series(
        True,
        index=df.index,
    )

    for condition in conditions:
        mask &= condition_mask(
            df=df,
            condition=condition,
        )

    matched = df[mask]

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
        "condition_count": len(conditions),
        "condition": " & ".join(
            condition["name"]
            for condition in conditions
        ),
        "matches": matches,
        "draws": draws,
        "draw_rate": draw_rate,
    }


def build_result(
    df,
    condition_count,
    overall_draw_rate,
):
    rows = []

    for condition_group in combinations(
        CONDITIONS,
        condition_count,
    ):
        rows.append(
            evaluate_pattern(
                df=df,
                conditions=condition_group,
            )
        )

    result = pd.DataFrame(rows)

    result["lift_vs_overall"] = (
        result["draw_rate"]
        - overall_draw_rate
    )

    result["qualifies"] = (
        (result["matches"] >= MIN_MATCHES)
        & (
            result["draw_rate"]
            >= MIN_DRAW_RATE
        )
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

    return result


def print_result(
    title,
    result,
    top_n=None,
):
    print()
    print(title)
    print("-" * 100)

    display = (
        result.head(top_n)
        if top_n is not None
        else result
    )

    print(
        display.to_string(
            index=False,
            formatters={
                "draw_rate": "{:.2%}".format,
                "lift_vs_overall": (
                    "{:+.2%}".format
                ),
            },
        )
    )


def main():
    df = load_data()

    overall_draw_rate = (
        df["is_draw"].mean()
    )

    single_result = build_result(
        df=df,
        condition_count=1,
        overall_draw_rate=overall_draw_rate,
    )

    pair_result = build_result(
        df=df,
        condition_count=2,
        overall_draw_rate=overall_draw_rate,
    )

    qualified_pairs = pair_result[
        pair_result["qualifies"]
    ].copy()

    print("=" * 100)
    print("Draw Pattern Miner")
    print("=" * 100)
    print(f"対象試合数: {len(df)}")
    print(
        f"全体引分率: "
        f"{overall_draw_rate:.2%}"
    )
    print(
        f"採用基準: "
        f"{MIN_MATCHES}試合以上 / "
        f"引分率{MIN_DRAW_RATE:.0%}以上"
    )

    print_result(
        "Single Conditions",
        single_result,
    )

    print_result(
        "Two-Condition Patterns - Top 20",
        pair_result,
        top_n=20,
    )

    print_result(
        "Qualified Two-Condition Patterns",
        qualified_pairs,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    single_result.to_csv(
        OUTPUT_DIR
        / "draw_patterns_single.csv",
        index=False,
        encoding="utf-8-sig",
    )

    pair_result.to_csv(
        OUTPUT_DIR
        / "draw_patterns_pairs.csv",
        index=False,
        encoding="utf-8-sig",
    )

    qualified_pairs.to_csv(
        OUTPUT_DIR
        / "draw_patterns_pairs_qualified.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 100)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
