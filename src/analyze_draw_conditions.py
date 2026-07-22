from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


CONDITIONS = {
    "elo_diff_abs": {
        "source": "elo_diff",
        "absolute": True,
        "bins": [
            -0.001,
            25,
            50,
            100,
            150,
            200,
            np.inf,
        ],
        "labels": [
            "0-25",
            "26-50",
            "51-100",
            "101-150",
            "151-200",
            "201+",
        ],
    },
    "rank_diff_abs": {
        "source": "rank_diff",
        "absolute": True,
        "bins": [
            -0.001,
            1,
            2,
            4,
            6,
            10,
            np.inf,
        ],
        "labels": [
            "0-1",
            "2",
            "3-4",
            "5-6",
            "7-10",
            "11+",
        ],
    },
    "points_diff_abs": {
        "source": "points_diff",
        "absolute": True,
        "bins": [
            -0.001,
            2,
            5,
            10,
            20,
            30,
            np.inf,
        ],
        "labels": [
            "0-2",
            "3-5",
            "6-10",
            "11-20",
            "21-30",
            "31+",
        ],
    },
    "goal_diff_diff_abs": {
        "source": "goal_diff_diff",
        "absolute": True,
        "bins": [
            -0.001,
            2,
            5,
            10,
            20,
            30,
            np.inf,
        ],
        "labels": [
            "0-2",
            "3-5",
            "6-10",
            "11-20",
            "21-30",
            "31+",
        ],
    },
    "form_diff_abs": {
        "source": "form_diff",
        "absolute": True,
        "bins": [
            -0.001,
            1,
            3,
            5,
            8,
            12,
            np.inf,
        ],
        "labels": [
            "0-1",
            "2-3",
            "4-5",
            "6-8",
            "9-12",
            "13+",
        ],
    },
    "venue_form_diff_abs": {
        "source": "venue_form_diff",
        "absolute": True,
        "bins": [
            -0.001,
            1,
            3,
            5,
            8,
            12,
            np.inf,
        ],
        "labels": [
            "0-1",
            "2-3",
            "4-5",
            "6-8",
            "9-12",
            "13+",
        ],
    },
    "rest_diff_abs": {
        "source": "rest_diff",
        "absolute": True,
        "bins": [
            -0.001,
            0,
            1,
            2,
            3,
            5,
            np.inf,
        ],
        "labels": [
            "0",
            "1",
            "2",
            "3",
            "4-5",
            "6+",
        ],
    },
}


def prepare_data():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required = {
        "season",
        "league",
        "result",
    }

    for config in CONDITIONS.values():
        required.add(config["source"])

    missing = required - set(df.columns)

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

    df["actual"] = (
        df["result"]
        .astype(str)
        .str.strip()
        .astype(int)
    )

    df["is_draw"] = (
        df["actual"] == 0
    ).astype(int)

    return df


def summarize_condition(
    df,
    condition_name,
    config,
):
    source = config["source"]

    values = pd.to_numeric(
        df[source],
        errors="coerce",
    )

    if config.get("absolute"):
        values = values.abs()

    working = df.copy()
    working["condition_value"] = values

    working = working.dropna(
        subset=["condition_value"]
    ).copy()

    working["condition_band"] = pd.cut(
        working["condition_value"],
        bins=config["bins"],
        labels=config["labels"],
        include_lowest=True,
        right=True,
    )

    summary = (
        working.groupby(
            "condition_band",
            observed=False,
        )
        .agg(
            matches=("is_draw", "size"),
            draws=("is_draw", "sum"),
            average_value=(
                "condition_value",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["draw_rate"] = (
        summary["draws"]
        / summary["matches"]
    )

    summary["condition"] = condition_name

    return summary[
        [
            "condition",
            "condition_band",
            "matches",
            "draws",
            "draw_rate",
            "average_value",
        ]
    ]


def print_summary(
    condition_name,
    summary,
):
    print()
    print(condition_name)
    print("-" * 88)

    print(
        summary.to_string(
            index=False,
            formatters={
                "draw_rate": "{:.2%}".format,
                "average_value": "{:.2f}".format,
            },
        )
    )


def main():
    df = prepare_data()

    print("=" * 88)
    print("Draw Condition Research 2002-2025")
    print("=" * 88)
    print(f"対象試合数: {len(df)}")
    print(f"引分数: {int(df['is_draw'].sum())}")
    print(
        f"全体引分率: "
        f"{df['is_draw'].mean():.2%}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_results = []

    for condition_name, config in CONDITIONS.items():
        summary = summarize_condition(
            df=df,
            condition_name=condition_name,
            config=config,
        )

        all_results.append(summary)

        print_summary(
            condition_name,
            summary,
        )

        summary.to_csv(
            OUTPUT_DIR
            / f"draw_condition_{condition_name}.csv",
            index=False,
            encoding="utf-8-sig",
        )

    combined = pd.concat(
        all_results,
        ignore_index=True,
    )

    combined.to_csv(
        OUTPUT_DIR
        / "draw_conditions_all.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 88)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
