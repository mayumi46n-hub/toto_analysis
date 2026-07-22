from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


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
        "elo_diff",
        "rank_diff",
        "points_diff",
        "goal_diff_diff",
        "form_diff",
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

    numeric_columns = [
        "elo_diff",
        "rank_diff",
        "points_diff",
        "goal_diff_diff",
        "form_diff",
        "elo_expected_draw_base",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df[
        df["result"]
        .astype(str)
        .str.strip()
        .isin({"0", "1", "2"})
    ].copy()

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


def add_draw_intelligence_score(df):
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

    result["score_points"] = (
        result["points_diff_abs"] <= 5
    ).astype(int) * 2

    result["score_goal_diff"] = (
        result["goal_diff_diff_abs"] <= 5
    ).astype(int) * 2

    result["score_form"] = (
        result["form_diff_abs"] <= 3
    ).astype(int)

    result["score_rank"] = (
        result["rank_diff_abs"] <= 4
    ).astype(int)

    result["score_draw_base"] = (
        result["elo_expected_draw_base"]
        .between(
            0.70,
            0.85,
            inclusive="both",
        )
    ).astype(int) * 2

    result["draw_intelligence_score"] = (
        result["score_elo"]
        + result["score_points"]
        + result["score_goal_diff"]
        + result["score_form"]
        + result["score_rank"]
        + result["score_draw_base"]
    )

    return result


def summarize_by_score(df):
    summary = (
        df.groupby(
            "draw_intelligence_score"
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
            "draw_intelligence_score"
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

    overall_draw_rate = (
        df["is_draw"].mean()
    )

    summary["lift_vs_overall"] = (
        summary["draw_rate"]
        - overall_draw_rate
    )

    return summary


def summarize_by_band(df):
    working = df.copy()

    working["risk_band"] = pd.cut(
        working["draw_intelligence_score"],
        bins=[
            -0.1,
            3,
            6,
            8,
            10,
        ],
        labels=[
            "Low 0-3",
            "Medium 4-6",
            "High 7-8",
            "Very High 9-10",
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

    overall_draw_rate = (
        working["is_draw"].mean()
    )

    summary["lift_vs_overall"] = (
        summary["draw_rate"]
        - overall_draw_rate
    )

    return summary


def summarize_components(df):
    component_columns = [
        "score_elo",
        "score_points",
        "score_goal_diff",
        "score_form",
        "score_rank",
        "score_draw_base",
    ]

    rows = []

    for column in component_columns:
        active = df[df[column] > 0]

        matches = len(active)
        draws = int(
            active["is_draw"].sum()
        )

        draw_rate = (
            draws / matches
            if matches
            else 0.0
        )

        rows.append({
            "component": column,
            "matches": matches,
            "draws": draws,
            "draw_rate": draw_rate,
        })

    return pd.DataFrame(rows).sort_values(
        by=[
            "draw_rate",
            "matches",
        ],
        ascending=[
            False,
            False,
        ],
    )


def print_table(title, df):
    print()
    print(title)
    print("-" * 100)

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

    if "lift_vs_overall" in df.columns:
        formatters["lift_vs_overall"] = (
            "{:+.2%}".format
        )

    print(
        df.to_string(
            index=False,
            formatters=formatters,
        )
    )


def main():
    df = load_data()
    df = add_draw_intelligence_score(df)

    by_score = summarize_by_score(df)
    by_band = summarize_by_band(df)
    by_component = summarize_components(df)

    print("=" * 100)
    print("Draw Intelligence Score v1 Research")
    print("=" * 100)

    print(f"対象試合数: {len(df)}")
    print(
        f"引分数: "
        f"{int(df['is_draw'].sum())}"
    )
    print(
        f"全体引分率: "
        f"{df['is_draw'].mean():.2%}"
    )
    print("スコア範囲: 0〜10")

    print_table(
        "By Draw Intelligence Score",
        by_score,
    )

    print_table(
        "By Risk Band",
        by_band,
    )

    print_table(
        "By Score Component",
        by_component,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    by_score.to_csv(
        OUTPUT_DIR
        / "draw_intelligence_v1_by_score.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_band.to_csv(
        OUTPUT_DIR
        / "draw_intelligence_v1_by_band.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_component.to_csv(
        OUTPUT_DIR
        / "draw_intelligence_v1_by_component.csv",
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
        "elo_expected_draw_base",
        "score_elo",
        "score_points",
        "score_goal_diff",
        "score_form",
        "score_rank",
        "score_draw_base",
        "draw_intelligence_score",
    ]

    df[detail_columns].to_csv(
        OUTPUT_DIR
        / "draw_intelligence_v1_details.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 100)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
