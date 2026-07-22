from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


def normalize_league(value):
    text = str(value).strip().upper()

    if text in {"J1", "Ｊ１"}:
        return "J1"

    if text in {"J2", "Ｊ２"}:
        return "J2"

    if text in {"J3", "Ｊ３"}:
        return "J3"

    return str(value).strip()


def add_result_flags(df):
    result = (
        df["result"]
        .astype(str)
        .str.strip()
    )

    df = df.copy()

    df["is_home_win"] = (
        result == "1"
    ).astype(int)

    df["is_draw"] = (
        result == "0"
    ).astype(int)

    df["is_away_win"] = (
        result == "2"
    ).astype(int)

    return df


def summarize_group(
    df,
    group_columns,
):
    summary = (
        df.groupby(
            group_columns,
            dropna=False,
        )
        .agg(
            matches=("result", "size"),
            home_wins=(
                "is_home_win",
                "sum",
            ),
            draws=(
                "is_draw",
                "sum",
            ),
            away_wins=(
                "is_away_win",
                "sum",
            ),
        )
        .reset_index()
    )

    summary["home_rate"] = (
        summary["home_wins"]
        / summary["matches"]
    )

    summary["draw_rate"] = (
        summary["draws"]
        / summary["matches"]
    )

    summary["away_rate"] = (
        summary["away_wins"]
        / summary["matches"]
    )

    summary["home_advantage"] = (
        summary["home_rate"]
        - summary["away_rate"]
    )

    return summary


def print_table(
    title,
    df,
):
    print()
    print(title)
    print("-" * 88)

    formatters = {}

    for column in (
        "home_rate",
        "draw_rate",
        "away_rate",
        "home_advantage",
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
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: "
            f"{INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH
    )

    required_columns = {
        "season",
        "league",
        "result",
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise RuntimeError(
            "必要な列がありません: "
            + ", ".join(
                sorted(missing)
            )
        )

    df = df[
        df["result"]
        .astype(str)
        .str.strip()
        .isin(
            {"0", "1", "2"}
        )
    ].copy()

    df["season"] = (
        pd.to_numeric(
            df["season"],
            errors="coerce",
        )
    )

    df = df.dropna(
        subset=["season"]
    ).copy()

    df["season"] = (
        df["season"].astype(int)
    )

    df["league"] = (
        df["league"]
        .map(normalize_league)
    )

    df = add_result_flags(df)

    overall = pd.DataFrame(
        [
            {
                "season_start": int(
                    df["season"].min()
                ),
                "season_end": int(
                    df["season"].max()
                ),
                "matches": len(df),
                "home_wins": int(
                    df["is_home_win"].sum()
                ),
                "draws": int(
                    df["is_draw"].sum()
                ),
                "away_wins": int(
                    df["is_away_win"].sum()
                ),
            }
        ]
    )

    overall["home_rate"] = (
        overall["home_wins"]
        / overall["matches"]
    )

    overall["draw_rate"] = (
        overall["draws"]
        / overall["matches"]
    )

    overall["away_rate"] = (
        overall["away_wins"]
        / overall["matches"]
    )

    overall["home_advantage"] = (
        overall["home_rate"]
        - overall["away_rate"]
    )

    by_league = summarize_group(
        df,
        ["league"],
    ).sort_values(
        by=[
            "draw_rate",
            "matches",
        ],
        ascending=[
            False,
            False,
        ],
    )

    by_season = summarize_group(
        df,
        ["season"],
    ).sort_values(
        "season"
    )

    by_season_league = (
        summarize_group(
            df,
            [
                "season",
                "league",
            ],
        )
        .sort_values(
            [
                "season",
                "league",
            ]
        )
    )

    print("=" * 88)
    print(
        "Draw Distribution Research "
        "2002-2025"
    )
    print("=" * 88)

    print_table(
        "Overall",
        overall,
    )

    print_table(
        "By League",
        by_league,
    )

    print_table(
        "By Season",
        by_season,
    )

    highest_draw_seasons = (
        by_season.sort_values(
            by=[
                "draw_rate",
                "matches",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .head(10)
    )

    lowest_draw_seasons = (
        by_season.sort_values(
            by=[
                "draw_rate",
                "matches",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .head(10)
    )

    print_table(
        "Top 10 Draw Seasons",
        highest_draw_seasons,
    )

    print_table(
        "Bottom 10 Draw Seasons",
        lowest_draw_seasons,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    overall.to_csv(
        OUTPUT_DIR
        / "draw_distribution_overall.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_league.to_csv(
        OUTPUT_DIR
        / "draw_distribution_by_league.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_season.to_csv(
        OUTPUT_DIR
        / "draw_distribution_by_season.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_season_league.to_csv(
        OUTPUT_DIR
        / (
            "draw_distribution_"
            "by_season_league.csv"
        ),
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print("-" * 88)
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
