from __future__ import annotations
from match_analyzer import (
    filter_before_date,
    load_current_match,
    load_master,
    summarize_team,
    team_side_matches,
    h2h_matches,
    provisional_probabilities,
    similar_market_results,
)
from footystats_loader import get_team_stats
from footystats_loader_v2 import load_footystats_current

from ai_score import calculate_ai_score

import argparse
import sys

import pandas as pd

from match_analyzer import (
    filter_before_date,
    load_current_match,
    load_master,
)


def print_report(
    hold_cnt_id: int,
    match_no: int,
) -> int:
    try:
        master = load_master()

        match = load_current_match(
            hold_cnt_id,
            match_no,
        )

        historical = filter_before_date(
            master,
            match["match_date"],
        )

        footy_df = load_footystats_current()
        home_team = match["home_norm"]
        away_team = match["away_norm"]

        footy_home = get_team_stats(
            footy_df,
            str(match["home"]),
        )

        footy_away = get_team_stats(
            footy_df,
            str(match["away"]),
        )

        home_matches = team_side_matches(
            historical,
            home_team,
            "home",
        )

        away_matches = team_side_matches(
            historical,
            away_team,
            "away",
        )

        home_10 = summarize_team(
            home_matches,
            10,
        )

        away_10 = summarize_team(
            away_matches,
            10,
        )
        h2h = h2h_matches(
            historical,
            home_team,
            away_team,
        )

        similar = similar_market_results(
            historical,
            float(match["home_rate"]),
            float(match["draw_rate"]),
            float(match["away_rate"]),
        )
        probabilities = provisional_probabilities(
            (
                float(match["home_rate"]),
                float(match["draw_rate"]),
                float(match["away_rate"]),
            ),
            home_10,
            away_10,
            similar,
        )

        home_h2h_wins = 0
        away_h2h_wins = 0

        for _, row in h2h.iterrows():
            home_score = float(row["home_score_jleague"])
            away_score = float(row["away_score_jleague"])

            if home_score == away_score:
                continue

            winner = (
                row["home_norm"]
                if home_score > away_score
                else row["away_norm"]
            )

            if winner == home_team:
                home_h2h_wins += 1
            elif winner == away_team:
                away_h2h_wins += 1

        h2h_edge = (
            home_h2h_wins - away_h2h_wins
        ) / max(1, len(h2h))

        footy_ppg_diff = None
        footy_xg_diff = None
        footy_xga_edge = None

        footy_available = (
            footy_home is not None
            and footy_away is not None
            and bool(footy_home["footystats_available"])
            and bool(footy_away["footystats_available"])
        )

        if footy_available:
            footy_ppg_diff = (
                float(footy_home["points_per_game_home"])
                - float(footy_away["points_per_game_away"])
            )

            footy_xg_diff = (
                float(footy_home["xg_for_avg_home"])
                - float(footy_away["xg_for_avg_away"])
            )

            footy_xga_edge = (
                float(footy_away["xg_against_avg_away"])
                - float(footy_home["xg_against_avg_home"])
            )

        ai = calculate_ai_score(
            market_value=(
                probabilities[0]
                - float(match["home_rate"])
            ),
            form_diff=(
                home_10.points_per_match
                - away_10.points_per_match
            ),
            goal_diff=(
                home_10.goals_for
                - home_10.goals_against
            ) - (
                away_10.goals_for
                - away_10.goals_against
            ),
            shot_diff=(
                home_10.shots_for
                - away_10.shots_for
            ),
            h2h_edge=h2h_edge,
            similar_edge=(
                similar["home"]
                - similar["away"]
            ),
            footy_ppg_diff=footy_ppg_diff,
            footy_xg_diff=footy_xg_diff,
            footy_xga_edge=footy_xga_edge,
        )

    except (
        FileNotFoundError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        print(
            f"エラー: {error}",
            file=sys.stderr,
        )
        return 1

    market = (
        float(match["home_rate"]),
        float(match["draw_rate"]),
        float(match["away_rate"]),
    )

    print("=" * 68)
    print("TOTO LABO MATCH REPORT v2")
    print("=" * 68)

    print(
        f"第{hold_cnt_id}回 No.{match_no}"
    )

    print(
        f"{match['home']} vs {match['away']}"
    )

    print(
        f"開催日: {match['match_date']}"
    )

    print("\n【市場・toto投票率】")
    print(f"  1 ホーム勝ち : {market[0]:.2f}%")
    print(f"  0 引き分け   : {market[1]:.2f}%")
    print(f"  2 アウェイ勝ち: {market[2]:.2f}%")

    print("\n【直近10試合比較】")
    print(
        f"{'指標':<14}"
        f"{str(match['home']):>12}"
        f"{str(match['away']):>12}"
    )

    print(
        f"{'平均勝点':<14}"
        f"{home_10.points_per_match:>12.2f}"
        f"{away_10.points_per_match:>12.2f}"
    )

    print(
        f"{'平均得点':<14}"
        f"{home_10.goals_for:>12.2f}"
        f"{away_10.goals_for:>12.2f}"
    )

    print(
        f"{'平均失点':<14}"
        f"{home_10.goals_against:>12.2f}"
        f"{away_10.goals_against:>12.2f}"
    )

    print(
        f"{'平均SH':<14}"
        f"{home_10.shots_for:>12.2f}"
        f"{away_10.shots_for:>12.2f}"
    )

    print(
        f"{'被SH':<14}"
        f"{home_10.shots_against:>12.2f}"
        f"{away_10.shots_against:>12.2f}"
    )

    if (
        footy_home is not None
        and footy_away is not None
        and bool(footy_home["footystats_available"])
        and bool(footy_away["footystats_available"])
    ):
        print("\n【FootyStats 2025】")

        print(
            f"{'項目':<16}"
            f"{str(match['home']):>12}"
            f"{str(match['away']):>12}"
        )

        print(
            f"{'PPG':<16}"
            f"{float(footy_home['points_per_game_home']):>12.2f}"
            f"{float(footy_away['points_per_game_away']):>12.2f}"
        )

        print(
            f"{'xG':<16}"
            f"{float(footy_home['xg_for_avg_home']):>12.2f}"
            f"{float(footy_away['xg_for_avg_away']):>12.2f}"
        )

        print(
            f"{'xGA':<16}"
            f"{float(footy_home['xg_against_avg_home']):>12.2f}"
            f"{float(footy_away['xg_against_avg_away']):>12.2f}"
        )

        print(
            f"{'BTTS':<16}"
            f"{float(footy_home['btts_percentage_home']):>11.0f}%"
            f"{float(footy_away['btts_percentage_away']):>11.0f}%"
        )

        print(
            f"{'Clean Sheet':<16}"
            f"{float(footy_home['clean_sheet_percentage_home']):>11.0f}%"
            f"{float(footy_away['clean_sheet_percentage_away']):>11.0f}%"
        )

    print("\n【AI総合評価】")
    print(f"  AI Score : {ai.total}/100")
    print(f"  信頼度   : {ai.stars}")
    print(f"  推奨     : {ai.recommendation}")

    print("\n【AI Score内訳】")

    score_limits = {
        "市場差": 20,
        "フォーム": 20,
        "得失点差": 10,
        "SH差": 10,
        "直接対戦": 10,
        "類似投票率": 10,
        "FootyStats": 20,
    }

    for name, score in ai.breakdown.items():
        maximum = score_limits[name]
        print(
            f"  {name:<12}"
            f"{score:>2}/{maximum}"
        )

    print("\n【履歴データ】")
    print(f"  使用可能試合数: {len(historical)}")



    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TOTO LABO Match Report v2"
    )

    parser.add_argument(
        "hold_cnt_id",
        type=int,
        help="toto開催回",
    )

    parser.add_argument(
        "match_no",
        type=int,
        help="試合番号",
    )

    args = parser.parse_args()

    return print_report(
        args.hold_cnt_id,
        args.match_no,
    )


if __name__ == "__main__":
    raise SystemExit(main())
