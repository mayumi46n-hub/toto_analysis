from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_PATH = Path(
    "data/evaluation/draw_research/"
    "draw_probability_distribution.csv"
)


BINS = [
    -0.001,
    0.50,
    0.60,
    0.70,
    0.80,
    0.85,
    0.90,
    0.95,
    1.00,
]

LABELS = [
    "0.00-0.50",
    "0.50-0.60",
    "0.60-0.70",
    "0.70-0.80",
    "0.80-0.85",
    "0.85-0.90",
    "0.90-0.95",
    "0.95-1.00",
]


def load_data():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = {
        "season",
        "league",
        "result",
        "elo_expected_draw_base",
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

    df["elo_expected_draw_base"] = (
        pd.to_numeric(
            df["elo_expected_draw_base"],
            errors="coerce",
        )
    )

    df["season"] = pd.to_numeric(
        df["season"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "season",
            "elo_expected_draw_base",
        ]
    ).copy()

    df["season"] = (
        df["season"].astype(int)
    )

    df["is_draw"] = (
        df["result"]
        .astype(str)
        .str.strip()
        .eq("0")
        .astype(int)
    )

    return df


def build_band_summary(df):
    working = df.copy()

    working["draw_base_band"] = pd.cut(
        working["elo_expected_draw_base"],
        bins=BINS,
        labels=LABELS,
        include_lowest=True,
        right=True,
    )

    summary = (
        working.groupby(
            "draw_base_band",
            observed=False,
        )
        .agg(
            matches=("is_draw", "size"),
            draws=("is_draw", "sum"),
            average_draw_base=(
                "elo_expected_draw_base",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["draw_rate"] = (
        summary["draws"]
        / summary["matches"]
    )

    overall_draw_rate = (
        working["is_draw"].mean()
    )

    summary["lift_vs_overall"] = (
        summary["draw_rate"]
        - overall_draw_rate
    )

    return summary


def build_threshold_summary(df):
    thresholds = np.arange(
        0.50,
        1.001,
        0.05,
    )

    rows = []

    total_draws = int(
        df["is_draw"].sum()
    )

    for threshold in thresholds:
        matched = df[
            df["elo_expected_draw_base"]
            >= threshold
        ]

        matches = len(matched)
        draws = int(
            matched["is_draw"].sum()
        )

        draw_rate = (
            draws / matches
            if matches
            else 0.0
        )

        draw_recall = (
            draws / total_draws
            if total_draws
            else 0.0
        )

        rows.append({
            "threshold": threshold,
            "matches": matches,
            "draws": draws,
            "draw_rate": draw_rate,
            "draw_recall": draw_recall,
        })

    return pd.DataFrame(rows)


def print_table(title, df):
    print()
    print(title)
    print("-" * 88)

    formatters = {}

    for column in (
        "draw_rate",
        "draw_recall",
        "lift_vs_overall",
    ):
        if column in df.columns:
            if column == "lift_vs_overall":
                formatters[column] = (
                    "{:+.2%}".format
                )
            else:
                formatters[column] = (
                    "{:.2%}".format
                )

    for column in (
        "average_draw_base",
        "threshold",
    ):
        if column in df.columns:
            formatters[column] = (
                "{:.3f}".format
            )

    print(
        df.to_string(
            index=False,
            formatters=formatters,
        )
    )


def main():
    df = load_data()

    overall_draw_rate = (
        df["is_draw"].mean()
    )

    band_summary = (
        build_band_summary(df)
    )

    threshold_summary = (
        build_threshold_summary(df)
    )

    print("=" * 88)
    print(
        "Elo Expected Draw Base Research "
        "2002-2025"
    )
    print("=" * 88)

    print(f"対象試合数: {len(df)}")
    print(
        f"引分数: "
        f"{int(df['is_draw'].sum())}"
    )
    print(
        f"全体引分率: "
        f"{overall_draw_rate:.2%}"
    )
    print(
        "注意: elo_expected_draw_base は"
        "引分確率ではなく互角度"
    )

    print_table(
        "By Draw Base Band",
        band_summary,
    )

    print_table(
        "By Minimum Threshold",
        threshold_summary,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    band_summary.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    threshold_summary.to_csv(
        OUTPUT_PATH.with_name(
            "draw_probability_thresholds.csv"
        ),
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 88)
    print(OUTPUT_PATH)
    print(
        OUTPUT_PATH.with_name(
            "draw_probability_thresholds.csv"
        )
    )


if __name__ == "__main__":
    main()
