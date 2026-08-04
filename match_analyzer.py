from __future__ import annotations

import argparse
import math
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


MASTER_FILE = Path("jleague_toto_analysis_master.csv")
CURRENT_FILE = Path("current_toto_matches.csv")


TEAM_ALIASES = {
    "F東京": "FC東京",
    "FC東京": "FC東京",
    "Ｆ東京": "FC東京",

    "川崎": "川崎Ｆ",
    "川崎F": "川崎Ｆ",
    "川崎Ｆ": "川崎Ｆ",

    "横浜M": "横浜FM",
    "横浜Ｍ": "横浜FM",
    "横浜FM": "横浜FM",

    "横浜C": "横浜FC",
    "横浜Ｃ": "横浜FC",
    "横浜FC": "横浜FC",

    "東京V": "東京Ｖ",
    "東京Ｖ": "東京Ｖ",

    "G大阪": "Ｇ大阪",
    "Ｇ大阪": "Ｇ大阪",

    "C大阪": "Ｃ大阪",
    "Ｃ大阪": "Ｃ大阪",

    "栃木": "栃木SC",
    "栃木SC": "栃木SC",
    "栃木ＳＣ": "栃木SC",

    "草津": "群馬",
    "群馬": "群馬",
}


@dataclass
class TeamSummary:
    matches: int
    wins: int
    draws: int
    losses: int
    points_per_match: float
    goals_for: float
    goals_against: float
    shots_for: float
    shots_against: float
    corners_for: float
    corners_against: float
    fouls_for: float
    fouls_against: float
    form: str


def normalize_team(value: object) -> str:
    if pd.isna(value):
        return ""

    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"\s+", "", text.strip())

    return TEAM_ALIASES.get(text, text)


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_mean(series: pd.Series) -> float:
    value = numeric(series).mean()
    return 0.0 if pd.isna(value) else float(value)


def format_number(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def form_symbol(goals_for: float, goals_against: float) -> str:
    if goals_for > goals_against:
        return "○"
    if goals_for < goals_against:
        return "●"
    return "△"


def load_master() -> pd.DataFrame:
    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"{MASTER_FILE} が見つかりません。"
        )

    df = pd.read_csv(
        MASTER_FILE,
        low_memory=False,
        dtype={
            "match_card_id": "string",
            "hold_cnt_id": "Int64",
            "match_no": "Int64",
        },
    )

    required = {
        "date_jleague",
        "home",
        "away",
        "home_score_jleague",
        "away_score_jleague",
        "home_SH",
        "away_SH",
        "home_CK",
        "away_CK",
        "home_FK",
        "away_FK",
        "home_rate",
        "draw_rate",
        "away_rate",
        "result",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "マスターCSVに必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    df["match_date"] = pd.to_datetime(
        df["date_jleague"],
        errors="coerce",
    )

    df["home_norm"] = df["home"].map(normalize_team)
    df["away_norm"] = df["away"].map(normalize_team)

    numeric_columns = [
        "home_score_jleague",
        "away_score_jleague",
        "home_SH",
        "away_SH",
        "home_CK",
        "away_CK",
        "home_FK",
        "away_FK",
        "home_rate",
        "draw_rate",
        "away_rate",
        "result",
    ]

    for column in numeric_columns:
        df[column] = numeric(df[column])

    return df.sort_values("match_date")


def load_current_match(
    hold_cnt_id: int,
    match_no: int,
) -> pd.Series:
    if not CURRENT_FILE.exists():
        raise FileNotFoundError(
            f"{CURRENT_FILE} が見つかりません。"
        )

    current = pd.read_csv(
        CURRENT_FILE,
        dtype={
            "hold_cnt_id": "Int64",
            "match_no": "Int64",
        },
    )

    required = {
        "hold_cnt_id",
        "match_no",
        "match_date",
        "home",
        "away",
        "home_rate",
        "draw_rate",
        "away_rate",
    }

    missing = required - set(current.columns)

    if missing:
        raise ValueError(
            "現在回CSVに必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    target = current[
        (current["hold_cnt_id"] == hold_cnt_id)
        & (current["match_no"] == match_no)
    ]

    if target.empty:
        raise ValueError(
            f"第{hold_cnt_id}回 第{match_no}試合が"
            f"{CURRENT_FILE}にありません。"
        )

    if len(target) > 1:
        raise ValueError(
            "現在回CSVに同じ開催回・試合番号が複数あります。"
        )

    row = target.iloc[0].copy()

    row["home_norm"] = normalize_team(row["home"])
    row["away_norm"] = normalize_team(row["away"])

    return row


def filter_before_date(
    df: pd.DataFrame,
    match_date: object,
) -> pd.DataFrame:

    if pd.isna(match_date):
        return df.copy()

    text = str(match_date).strip()

    if not text:
        return df.copy()

    # YYYY-MM-DD形式のみを正式対応とする
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        text,
    ):
        raise ValueError(
            "match_dateはYYYY-MM-DD形式が必要です。"
            f"現在値: {text!r}"
        )

    cutoff = pd.to_datetime(
        text,
        format="%Y-%m-%d",
        errors="raise",
    )

    historical = df[
        df["match_date"] < cutoff
    ].copy()

    return historical


def team_side_matches(
    df: pd.DataFrame,
    team: str,
    venue: str,
) -> pd.DataFrame:
    if venue == "home":
        selected = df[df["home_norm"] == team].copy()

        selected["team_gf"] = selected["home_score_jleague"]
        selected["team_ga"] = selected["away_score_jleague"]
        selected["team_sh"] = selected["home_SH"]
        selected["opp_sh"] = selected["away_SH"]
        selected["team_ck"] = selected["home_CK"]
        selected["opp_ck"] = selected["away_CK"]
        selected["team_fk"] = selected["home_FK"]
        selected["opp_fk"] = selected["away_FK"]

    elif venue == "away":
        selected = df[df["away_norm"] == team].copy()

        selected["team_gf"] = selected["away_score_jleague"]
        selected["team_ga"] = selected["home_score_jleague"]
        selected["team_sh"] = selected["away_SH"]
        selected["opp_sh"] = selected["home_SH"]
        selected["team_ck"] = selected["away_CK"]
        selected["opp_ck"] = selected["home_CK"]
        selected["team_fk"] = selected["away_FK"]
        selected["opp_fk"] = selected["home_FK"]

    else:
        raise ValueError("venueはhomeまたはawayです。")

    return selected.sort_values(
        "match_date",
        ascending=False,
    )


def summarize_team(
    matches: pd.DataFrame,
    limit: int,
) -> TeamSummary:
    sample = matches.head(limit).copy()

    if sample.empty:
        return TeamSummary(
            matches=0,
            wins=0,
            draws=0,
            losses=0,
            points_per_match=0.0,
            goals_for=0.0,
            goals_against=0.0,
            shots_for=0.0,
            shots_against=0.0,
            corners_for=0.0,
            corners_against=0.0,
            fouls_for=0.0,
            fouls_against=0.0,
            form="-",
        )

    wins = int((sample["team_gf"] > sample["team_ga"]).sum())
    draws = int((sample["team_gf"] == sample["team_ga"]).sum())
    losses = int((sample["team_gf"] < sample["team_ga"]).sum())

    points = wins * 3 + draws

    symbols = [
        form_symbol(gf, ga)
        for gf, ga in zip(
            sample["team_gf"],
            sample["team_ga"],
        )
    ]

    return TeamSummary(
        matches=len(sample),
        wins=wins,
        draws=draws,
        losses=losses,
        points_per_match=points / len(sample),
        goals_for=safe_mean(sample["team_gf"]),
        goals_against=safe_mean(sample["team_ga"]),
        shots_for=safe_mean(sample["team_sh"]),
        shots_against=safe_mean(sample["opp_sh"]),
        corners_for=safe_mean(sample["team_ck"]),
        corners_against=safe_mean(sample["opp_ck"]),
        fouls_for=safe_mean(sample["team_fk"]),
        fouls_against=safe_mean(sample["opp_fk"]),
        form="".join(symbols),
    )


def h2h_matches(
    df: pd.DataFrame,
    home_team: str,
    away_team: str,
    limit: int = 5,
) -> pd.DataFrame:
    direct = df[
        (
            (df["home_norm"] == home_team)
            & (df["away_norm"] == away_team)
        )
        |
        (
            (df["home_norm"] == away_team)
            & (df["away_norm"] == home_team)
        )
    ].copy()

    return direct.sort_values(
        "match_date",
        ascending=False,
    ).head(limit)


def similar_market_results(
    df: pd.DataFrame,
    home_rate: float,
    draw_rate: float,
    away_rate: float,
    tolerance: float = 4.0,
) -> dict[str, float]:
    similar = df[
        (abs(df["home_rate"] - home_rate) <= tolerance)
        & (abs(df["draw_rate"] - draw_rate) <= tolerance)
        & (abs(df["away_rate"] - away_rate) <= tolerance)
    ].copy()

    valid = similar["result"].dropna()

    if valid.empty:
        return {
            "matches": 0,
            "home": 0.0,
            "draw": 0.0,
            "away": 0.0,
        }

    total = len(valid)

    return {
        "matches": total,
        "home": float((valid == 1).sum() / total * 100),
        "draw": float((valid == 0).sum() / total * 100),
        "away": float((valid == 2).sum() / total * 100),
    }


def softmax(values: list[float]) -> list[float]:
    maximum = max(values)
    exp_values = [
        math.exp(value - maximum)
        for value in values
    ]
    total = sum(exp_values)

    return [
        value / total * 100
        for value in exp_values
    ]


def provisional_probabilities(
    market: tuple[float, float, float],
    home_stats: TeamSummary,
    away_stats: TeamSummary,
    similar: dict[str, float],
) -> tuple[float, float, float]:
    """
    v1の説明可能な暫定推定。
    機械学習モデルではありません。
    """

    market_home, market_draw, market_away = market

    home_form = home_stats.points_per_match
    away_form = away_stats.points_per_match

    home_goal_diff = (
        home_stats.goals_for
        - home_stats.goals_against
    )

    away_goal_diff = (
        away_stats.goals_for
        - away_stats.goals_against
    )

    home_shot_diff = (
        home_stats.shots_for
        - home_stats.shots_against
    )

    away_shot_diff = (
        away_stats.shots_for
        - away_stats.shots_against
    )

    home_score = (
        math.log(max(market_home, 0.1))
        + 0.32 * home_form
        + 0.20 * home_goal_diff
        + 0.025 * home_shot_diff
        + 0.15
    )

    away_score = (
        math.log(max(market_away, 0.1))
        + 0.32 * away_form
        + 0.20 * away_goal_diff
        + 0.025 * away_shot_diff
    )

    draw_balance = -abs(
        (
            home_form
            + home_goal_diff
        )
        -
        (
            away_form
            + away_goal_diff
        )
    )

    draw_score = (
        math.log(max(market_draw, 0.1))
        + 0.18 * draw_balance
    )

    if similar["matches"] >= 20:
        home_score += 0.006 * similar["home"]
        draw_score += 0.006 * similar["draw"]
        away_score += 0.006 * similar["away"]

    probabilities = softmax(
        [home_score, draw_score, away_score]
    )

    return tuple(probabilities)


def print_team_summary(
    label: str,
    summary: TeamSummary,
) -> None:
    print(label)

    if summary.matches == 0:
        print("  対象データなし")
        return

    print(f"  対象試合: {summary.matches}")
    print(
        f"  成績: {summary.wins}勝 "
        f"{summary.draws}分 "
        f"{summary.losses}敗"
    )
    print(f"  フォーム: {summary.form}")
    print(
        "  平均勝点: "
        f"{format_number(summary.points_per_match)}"
    )
    print(
        "  平均得点・失点: "
        f"{format_number(summary.goals_for)} - "
        f"{format_number(summary.goals_against)}"
    )
    print(
        "  平均SH: "
        f"{format_number(summary.shots_for)} "
        f"（被SH {format_number(summary.shots_against)}）"
    )
    print(
        "  平均CK: "
        f"{format_number(summary.corners_for)} "
        f"（被CK {format_number(summary.corners_against)}）"
    )
    print(
        "  平均FK: "
        f"{format_number(summary.fouls_for)} "
        f"（相手FK {format_number(summary.fouls_against)}）"
    )


def print_h2h(
    h2h: pd.DataFrame,
    first_team: str,
) -> None:
    print("\n【直接対戦・直近5試合】")

    if h2h.empty:
        print("  対戦データなし")
        return

    first_wins = 0
    draws = 0
    second_wins = 0

    for _, row in h2h.iterrows():
        date_text = (
            row["match_date"].strftime("%Y-%m-%d")
            if not pd.isna(row["match_date"])
            else "日付不明"
        )

        home = row["home_norm"]
        away = row["away_norm"]
        hs = int(row["home_score_jleague"])
        aws = int(row["away_score_jleague"])

        print(
            f"  {date_text} "
            f"{home} {hs}-{aws} {away}"
        )

        if hs == aws:
            draws += 1
        else:
            winner = home if hs > aws else away

            if winner == first_team:
                first_wins += 1
            else:
                second_wins += 1

    print(
        f"  集計: {first_wins}勝 "
        f"{draws}分 {second_wins}敗"
        f"（先に表示したホーム側視点）"
    )


def recommendation_labels(
    probabilities: tuple[float, float, float],
) -> tuple[str, str, str]:
    labels = ["1", "0", "2"]

    ranked = sorted(
        zip(labels, probabilities),
        key=lambda x: x[1],
        reverse=True,
    )

    return (
        ranked[0][0],
        ranked[1][0],
        ranked[2][0],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TOTO LABO Match Analyzer v1"
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

    try:
        master = load_master()

        match = load_current_match(
            args.hold_cnt_id,
            args.match_no,
        )

    except (
        FileNotFoundError,
        ValueError,
        pd.errors.ParserError,
    ) as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    historical = filter_before_date(
        master,
        match["match_date"],
    )

    home_team = match["home_norm"]
    away_team = match["away_norm"]

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

    home_5 = summarize_team(home_matches, 5)
    home_10 = summarize_team(home_matches, 10)
    away_5 = summarize_team(away_matches, 5)
    away_10 = summarize_team(away_matches, 10)

    h2h = h2h_matches(
        historical,
        home_team,
        away_team,
    )

    market = (
        float(match["home_rate"]),
        float(match["draw_rate"]),
        float(match["away_rate"]),
    )

    similar = similar_market_results(
        historical,
        *market,
    )

    probabilities = provisional_probabilities(
        market,
        home_10,
        away_10,
        similar,
    )

    main_pick, second_pick, third_pick = (
        recommendation_labels(probabilities)
    )

    print("=" * 62)
    print("TOTO LABO Match Analyzer v1")
    print("=" * 62)
    print(
        f"第{args.hold_cnt_id}回 "
        f"第{args.match_no}試合"
    )
    print(f"{match['home']} vs {match['away']}")

    if (
        not pd.isna(match["match_date"])
        and str(match["match_date"]).strip()
    ):
        print(f"開催日: {match['match_date']}")

    print("\n【市場・toto投票率】")
    print(f"  1 ホーム勝ち : {market[0]:.2f}%")
    print(f"  0 引き分け   : {market[1]:.2f}%")
    print(f"  2 アウェイ勝ち: {market[2]:.2f}%")

    print("\n【ホームチーム】")
    print_team_summary(
        f"{match['home']}・直近5ホーム戦",
        home_5,
    )
    print()
    print_team_summary(
        f"{match['home']}・直近10ホーム戦",
        home_10,
    )

    print("\n【アウェイチーム】")
    print_team_summary(
        f"{match['away']}・直近5アウェイ戦",
        away_5,
    )
    print()
    print_team_summary(
        f"{match['away']}・直近10アウェイ戦",
        away_10,
    )

    print_h2h(
        h2h,
        home_team,
    )

    print("\n【類似投票率の過去実績】")
    print(
        "  条件: 各投票率が今回の±4ポイント以内"
    )
    print(f"  対象試合: {similar['matches']}")

    if similar["matches"]:
        print(f"  1: {similar['home']:.2f}%")
        print(f"  0: {similar['draw']:.2f}%")
        print(f"  2: {similar['away']:.2f}%")

    print("\n【FootyStats】")
    print("  v1では未連携")
    print("  v2でxG・xGA・BTTS・CSを追加予定")

    print("\n【TOTO LABO暫定確率】")
    print("  ※市場・フォーム・得失点・SH差による")
    print("  ※まだ機械学習モデルではありません")
    print(f"  1: {probabilities[0]:.2f}%")
    print(f"  0: {probabilities[1]:.2f}%")
    print(f"  2: {probabilities[2]:.2f}%")

    print("\n【市場との差】")
    print(
        f"  1: {probabilities[0] - market[0]:+.2f}pt"
    )
    print(
        f"  0: {probabilities[1] - market[1]:+.2f}pt"
    )
    print(
        f"  2: {probabilities[2] - market[2]:+.2f}pt"
    )

    print("\n【暫定判定】")
    print(f"  本命: {main_pick}")
    print(f"  対抗: {second_pick}")
    print(f"  穴  : {third_pick}")
    print(
        f"  ダブル候補: {main_pick}・{second_pick}"
    )

    print("\n注意:")
    print(
        "  v1は過去データによる説明可能な分析器です。"
    )
    print(
        "  最新メンバー、負傷、FootyStatsは未反映です。"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
