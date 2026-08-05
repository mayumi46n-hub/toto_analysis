from __future__ import annotations

from pathlib import Path

import pandas as pd

from footystats_loader import (
    get_team_stats,
    load_footystats,
)


DATA_ROOT = Path("data/footystats/csv")

LEAGUES = ("J1", "J2", "J3")
YEARS = (2025, 2026)


def find_teams_csv(
    year: int,
    league: str,
) -> Path:
    directory = DATA_ROOT / str(year) / league

    if not directory.exists():
        raise FileNotFoundError(
            f"ディレクトリがありません: {directory}"
        )

    candidates = sorted(
        path
        for path in directory.glob(
            "japan-*-league-teams-*-stats.csv"
        )
        if "-teams2-" not in path.name
    )

    if not candidates:
        raise FileNotFoundError(
            f"Teams CSVがありません: {directory}"
        )

    if len(candidates) > 1:
        raise ValueError(
            "Teams CSVが複数あります: "
            + ", ".join(str(path) for path in candidates)
        )

    return candidates[0]


def load_one_league(
    year: int,
    league: str,
) -> pd.DataFrame:
    path = find_teams_csv(
        year,
        league,
    )

    df = load_footystats(path).copy()

    df["source_year"] = year
    df["source_league"] = league
    df["source_file"] = str(path)

    return df


def load_all_footystats() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for year in YEARS:
        for league in LEAGUES:
            frame = load_one_league(
                year,
                league,
            )
            frames.append(frame)

    return pd.concat(
        frames,
        ignore_index=True,
    )


def select_best_team_rows(
    all_df: pd.DataFrame,
) -> pd.DataFrame:
    working = all_df.copy()

    working["matches_played"] = pd.to_numeric(
        working["matches_played"],
        errors="coerce",
    ).fillna(0)

    working["usable_2026"] = (
        (working["source_year"] == 2026)
        & (working["matches_played"] > 0)
    )

    # 優先順位:
    # 1. 試合実績がある2026
    # 2. 2025
    # 3. 試合数0の2026
    working["priority"] = 3

    working.loc[
        working["source_year"] == 2025,
        "priority",
    ] = 2

    working.loc[
        working["usable_2026"],
        "priority",
    ] = 1

    working = working.sort_values(
        [
            "team_norm",
            "priority",
            "matches_played",
        ],
        ascending=[
            True,
            True,
            False,
        ],
    )

    selected = (
        working
        .drop_duplicates(
            subset=["team_norm"],
            keep="first",
        )
        .copy()
    )

    selected["footystats_available"] = (
        selected["matches_played"] > 0
    )

    selected["fallback_used"] = (
        selected["source_year"] == 2025
    )

    return selected.reset_index(drop=True)


def load_footystats_current() -> pd.DataFrame:
    all_df = load_all_footystats()
    return select_best_team_rows(all_df)


def main() -> None:
    df = load_footystats_current()

    print("採用チーム数:", len(df))
    print(
        "利用可能チーム数:",
        int(df["footystats_available"].sum()),
    )

    print("\n【採用年度】")
    print(
        df["source_year"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    columns = [
        "common_name",
        "team_norm",
        "source_year",
        "source_league",
        "matches_played",
        "points_per_game",
        "xg_for_avg_overall",
        "xg_against_avg_overall",
        "fallback_used",
    ]

    print("\n【採用データ一覧】")
    print(
        df[columns]
        .sort_values(
            ["source_league", "team_norm"]
        )
        .to_string(index=False)
    )

    for team in [
        "Ｃ大阪",
        "岡山",
        "FC東京",
        "町田",
    ]:
        row = get_team_stats(
            df,
            team,
        )

        print(f"\n検索: {team}")

        if row is None:
            print("  該当なし")
            continue

        print(
            f"  {row['common_name']} / "
            f"{row['source_year']} / "
            f"{row['source_league']} / "
            f"{row['matches_played']}試合"
        )


if __name__ == "__main__":
    main()
