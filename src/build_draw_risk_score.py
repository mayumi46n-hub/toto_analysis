from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


def prepare_data():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    required_columns = {
        "season",
        "league",
        "result",
        "elo_diff",
        "rank_diff",
        "points_diff",
        "goal_diff_diff",
        "form_diff",
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

    numeric_columns = [
        "elo_diff",
        "rank_diff",
        "points_diff",
        "goal_diff_diff",
        "form_diff",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=numeric_columns
    ).copy()

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


def add_draw_risk_score(df):
    result = df.copy()

    result["elo_diff_abs"] = (
        result["elo_diff"].abs()
    )

    result["rank_diff_abs"] = (
        result["rank_diff"].abs()
    )

    result["points_diff_abs"] = (
        result["points_diff"].abs()
    )

    result["goal_diff_diff_abs"] = (
        result["goal_diff_diff"].abs()
    )

    result["form_diff_abs"] = (
        result["form_diff"].abs()
    )

    result["score_elo"] = (
        result["elo_diff_abs"] <= 50
    ).astype(int) * 2

    result["score_rank"] = (
        result["rank_diff_abs"] <= 4
    ).astype(int) * 2

    result["score_points"] = (
        result["points_diff_abs"] <= 5
    ).astype(int) * 2

    result["score_goal_diff"] = (
        result["goal_diff_diff_abs"] <= 5
    ).astype(int)

    result["score_form"] = (
        result["form_diff_abs"] <= 3
    ).astype(int)

    result["draw_risk_score"] = (
        result["score_elo"]
        + result["score_rank"]
        + result["score_points"]
        + result["score_goal_diff"]
        + result["score_form"]
    )

    return result


def summarize_by_score(df):
    summary = (
        df.groupby(
            "draw_risk_score",
            dropna=False,
        )
        .agg(
            matches=("is_draw", "size"),
            draws=("is_draw", "sum"),
            home_wins=(
                "actual",
                lambda s: int((s == 1).sum()),
            ),
            away_wins=(
                "actual",
                lambda s: int((s == 2).sum()),
            ),
        )
        .reset_index()
        .sort_values(
            "draw_risk_score"
        )
    )

    summary["draw_rate"] = (
        summary["draws"]
        / summary["matches"]
    )

    summary["home_rate"] = (
        summary["home_wins"]
        / summary["matches"]
    )

    summary["away_rate"] = (
        summary["away_wins"]
        / summary["matches"]
    )

    return summary


def summarize_by_band(df):
    working = df.copy()

    working["risk_band"] = pd.cut(
        working["draw_risk_score"],
        bins=[
            -0.1,
            2,
            5,
            8,
        ],
        labels=[
            "Low 0-2",
            "Medium 3-5",
            "High 6-8",
        ],
        include_lowest=True,
    )

    summary = (
        working.groupby(
            "risk_band",
            observed=False,
        )
        .agg(
            matches=("is_draw", "size"),
            draws=("is_draw", "sum"),
        )
        .reset_index()
    )

    summary["draw_rate"] = (
        summary["draws"]
        / summary["matches"]
    )

    return summary


def print_table(title, df):
    print()
    print(title)
    print("-" * 88)

    formatters = {}

    for column in (
        "draw_rate",
        "home_rate",
        "away_rate",
    ):
        if column in df.columns:
            formatters[column] = (
                "{:.2%}".format
            )

    print(
        df.to_string(
            index=False,
            formatters=formatters,
        )
    )


def main():
    df = prepare_data()
    df = add_draw_risk_score(df)

    by_score = summarize_by_score(df)
    by_band = summarize_by_band(df)

    print("=" * 88)
    print("Draw Risk Score v1 Research")
    print("=" * 88)

    print(f"対象試合数: {len(df)}")
    print(f"引分数: {int(df['is_draw'].sum())}")
    print(
        f"全体引分率: "
        f"{df['is_draw'].mean():.2%}"
    )

    print_table(
        "By Draw Risk Score",
        by_score,
    )

    print_table(
        "By Risk Band",
        by_band,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    by_score.to_csv(
        OUTPUT_DIR
        / "draw_risk_score_v1_by_score.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_band.to_csv(
        OUTPUT_DIR
        / "draw_risk_score_v1_by_band.csv",
        index=False,
        encoding="utf-8-sig",
    )

    detail_columns = [
        "season",
        "league",
        "result",
        "actual",
        "is_draw",
        "elo_diff_abs",
        "rank_diff_abs",
        "points_diff_abs",
        "goal_diff_diff_abs",
        "form_diff_abs",
        "score_elo",
        "score_rank",
        "score_points",
        "score_goal_diff",
        "score_form",
        "draw_risk_score",
    ]

    available_columns = [
        column
        for column in detail_columns
        if column in df.columns
    ]

    df[available_columns].to_csv(
        OUTPUT_DIR
        / "draw_risk_score_v1_details.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 88)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
