import argparse
import math
import re
import sqlite3
from pathlib import Path

DB_PATH = Path("data/toto.db")

INITIAL_RATING = 1500.0
K_FACTOR = 20.0
HOME_ADVANTAGE = 100.0

# 前年度評価を75%残し、25%を平均値1500へ戻す
SEASON_CARRYOVER = 0.75


def detect_league(competition):
    text = (competition or "").strip().upper()

    if text.startswith("Ｊ１") or text.startswith("J1"):
        return "J1"

    if text.startswith("Ｊ２") or text.startswith("J2"):
        return "J2"

    return None


def parse_date_key(season, match_date):
    match = re.search(
        r"\d{2}/(\d{2})/(\d{2})",
        match_date or "",
    )

    if match is None:
        raise ValueError(
            f"試合日を解析できません: "
            f"season={season}, match_date={match_date!r}"
        )

    month, day = match.groups()

    return f"{season:04d}{month}{day}"


def create_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS match_elo (
            season INTEGER NOT NULL,
            jleague_match_id INTEGER NOT NULL,

            league TEXT NOT NULL,
            match_date TEXT NOT NULL,
            kickoff_time TEXT,

            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,

            home_elo REAL NOT NULL,
            away_elo REAL NOT NULL,
            elo_diff REAL NOT NULL,

            expected_home REAL NOT NULL,
            expected_draw_base REAL NOT NULL,
            expected_away REAL NOT NULL,

            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,
            result TEXT NOT NULL,

            home_elo_after REAL NOT NULL,
            away_elo_after REAL NOT NULL,

            PRIMARY KEY (
                season,
                jleague_match_id
            )
        )
    """)


def load_matches(con, start_season, end_season):
    rows = con.execute("""
        SELECT
            season,
            jleague_match_id,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team,
            home_score,
            away_score
        FROM jleague_matches
        WHERE season BETWEEN ? AND ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY
            season,
            match_date,
            kickoff_time,
            jleague_match_id
    """, (
        start_season,
        end_season,
    )).fetchall()

    matches = []

    for row in rows:
        (
            season,
            match_id,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team,
            home_score,
            away_score,
        ) = row

        league = detect_league(competition)

        if league is None:
            continue

        matches.append({
            "season": season,
            "match_id": match_id,
            "league": league,
            "match_date": match_date,
            "date_key": parse_date_key(
                season,
                match_date,
            ),
            "kickoff_time": kickoff_time or "",
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
        })

    matches.sort(
        key=lambda row: (
            row["season"],
            row["date_key"],
            row["kickoff_time"],
            row["match_id"],
        )
    )

    return matches


def regress_ratings_to_mean(ratings):
    for team in list(ratings):
        ratings[team] = (
            INITIAL_RATING
            + (
                ratings[team] - INITIAL_RATING
            ) * SEASON_CARRYOVER
        )


def expected_home_score(
    home_rating,
    away_rating,
):
    adjusted_home = (
        home_rating
        + HOME_ADVANTAGE
    )

    return 1.0 / (
        1.0
        + math.pow(
            10.0,
            (
                away_rating
                - adjusted_home
            ) / 400.0,
        )
    )


def actual_scores(home_score, away_score):
    if home_score > away_score:
        return "1", 1.0, 0.0

    if home_score < away_score:
        return "2", 0.0, 1.0

    return "0", 0.5, 0.5


def goal_margin_multiplier(
    home_score,
    away_score,
    elo_diff,
):
    margin = abs(
        home_score - away_score
    )

    if margin <= 1:
        return 1.0

    return (
        math.log(margin + 1.0)
        * (
            2.2
            / (
                abs(elo_diff) * 0.001
                + 2.2
            )
        )
    )


def build_rows(matches):
    ratings = {}
    output_rows = []

    current_season = None

    for match in matches:
        season = match["season"]

        if current_season is None:
            current_season = season

        elif season != current_season:
            regress_ratings_to_mean(
                ratings
            )
            current_season = season

        home_team = match["home_team"]
        away_team = match["away_team"]

        home_elo = ratings.get(
            home_team,
            INITIAL_RATING,
        )

        away_elo = ratings.get(
            away_team,
            INITIAL_RATING,
        )

        elo_diff = home_elo - away_elo

        expected_home = expected_home_score(
            home_rating=home_elo,
            away_rating=away_elo,
        )
        expected_away = 1.0 - expected_home

        # 引分専用確率ではなく、互角度を示す補助値
        expected_draw_base = (
            1.0
            - abs(
                expected_home
                - expected_away
            )
        )

        (
            result,
            actual_home,
            actual_away,
        ) = actual_scores(
            match["home_score"],
            match["away_score"],
        )

        multiplier = goal_margin_multiplier(
            home_score=match["home_score"],
            away_score=match["away_score"],
            elo_diff=elo_diff,
        )

        rating_change = (
            K_FACTOR
            * multiplier
            * (
                actual_home
                - expected_home
            )
        )

        home_elo_after = (
            home_elo
            + rating_change
        )

        away_elo_after = (
            away_elo
            - rating_change
        )

        output_rows.append({
            "season": season,
            "jleague_match_id": (
                match["match_id"]
            ),
            "league": match["league"],
            "match_date": (
                match["match_date"]
            ),
            "kickoff_time": (
                match["kickoff_time"]
            ),
            "home_team": home_team,
            "away_team": away_team,

            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_diff": elo_diff,

            "expected_home": expected_home,
            "expected_draw_base": (
                expected_draw_base
            ),
            "expected_away": expected_away,

            "home_score": (
                match["home_score"]
            ),
            "away_score": (
                match["away_score"]
            ),
            "result": result,

            "home_elo_after": (
                home_elo_after
            ),
            "away_elo_after": (
                away_elo_after
            ),
        })

        ratings[home_team] = (
            home_elo_after
        )
        ratings[away_team] = (
            away_elo_after
        )

    return output_rows


def save_rows(
    con,
    start_season,
    end_season,
    rows,
):
    con.execute("""
        DELETE FROM match_elo
        WHERE season BETWEEN ? AND ?
    """, (
        start_season,
        end_season,
    ))

    con.executemany("""
        INSERT INTO match_elo (
            season,
            jleague_match_id,

            league,
            match_date,
            kickoff_time,

            home_team,
            away_team,

            home_elo,
            away_elo,
            elo_diff,

            expected_home,
            expected_draw_base,
            expected_away,

            home_score,
            away_score,
            result,

            home_elo_after,
            away_elo_after
        )
        VALUES (
            :season,
            :jleague_match_id,

            :league,
            :match_date,
            :kickoff_time,

            :home_team,
            :away_team,

            :home_elo,
            :away_elo,
            :elo_diff,

            :expected_home,
            :expected_draw_base,
            :expected_away,

            :home_score,
            :away_score,
            :result,

            :home_elo_after,
            :away_elo_after
        )
    """, rows)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "J1/J2全試合について、"
            "試合前Eloレーティングを生成します。"
        )
    )

    parser.add_argument(
        "start_season",
        type=int,
        help="開始年度。例: 2002",
    )

    parser.add_argument(
        "end_season",
        type=int,
        help="終了年度。例: 2025",
    )

    args = parser.parse_args()

    if args.start_season > args.end_season:
        parser.error(
            "開始年度は終了年度以下にしてください"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        create_table(con)

        matches = load_matches(
            con=con,
            start_season=(
                args.start_season
            ),
            end_season=(
                args.end_season
            ),
        )

        if not matches:
            raise RuntimeError(
                "対象となるJ1/J2試合がありません"
            )

        rows = build_rows(matches)

        save_rows(
            con=con,
            start_season=(
                args.start_season
            ),
            end_season=(
                args.end_season
            ),
            rows=rows,
        )

        con.commit()

        print(
            f"対象年度: "
            f"{args.start_season}"
            f"〜{args.end_season}"
        )
        print(
            f"試合読込: {len(matches)}件"
        )
        print(
            f"Elo保存: {len(rows)}件"
        )
        print(
            "match_elo Version 1 作成完了"
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()