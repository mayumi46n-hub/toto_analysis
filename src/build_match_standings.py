import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path("data/toto.db")


def empty_stats():
    return {
        "played": 0,
        "win": 0,
        "draw": 0,
        "lose": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_diff": 0,
        "points": 0,
    }


def parse_match_date(value):
    match = re.search(
        r"(\d{2})/(\d{2})/(\d{2})",
        value or "",
    )

    if match is None:
        raise ValueError(
            f"試合日を解析できません: {value!r}"
        )

    year, month, day = match.groups()

    return f"20{year}{month}{day}"


def detect_league(competition):
    text = (competition or "").strip().upper()

    if text.startswith("Ｊ１") or text.startswith("J1"):
        return "J1"

    if text.startswith("Ｊ２") or text.startswith("J2"):
        return "J2"

    return None


def create_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS match_pre_standings (
            season INTEGER NOT NULL,
            jleague_match_id INTEGER NOT NULL,
            league TEXT NOT NULL,
            match_date TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,

            home_rank INTEGER NOT NULL,
            away_rank INTEGER NOT NULL,
            rank_diff INTEGER NOT NULL,

            home_played INTEGER NOT NULL,
            away_played INTEGER NOT NULL,

            home_points INTEGER NOT NULL,
            away_points INTEGER NOT NULL,
            points_diff INTEGER NOT NULL,

            home_goal_diff INTEGER NOT NULL,
            away_goal_diff INTEGER NOT NULL,
            goal_diff_diff INTEGER NOT NULL,

            PRIMARY KEY (
                season,
                jleague_match_id
            )
        )
    """)


def load_matches(con, season):
    rows = con.execute("""
        SELECT
            jleague_match_id,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team,
            home_score,
            away_score
        FROM jleague_matches
        WHERE season = ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY
            match_date,
            kickoff_time,
            jleague_match_id
    """, (season,)).fetchall()

    matches = []

    for (
        match_id,
        competition,
        match_date,
        kickoff_time,
        home_team,
        away_team,
        home_score,
        away_score,
    ) in rows:
        league = detect_league(competition)

        if league is None:
            continue

        matches.append({
            "match_id": match_id,
            "league": league,
            "match_date": match_date,
            "date_key": parse_match_date(match_date),
            "kickoff_time": kickoff_time or "",
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
        })

    return matches


def collect_teams(matches):
    teams = defaultdict(set)

    for match in matches:
        league = match["league"]
        teams[league].add(match["home_team"])
        teams[league].add(match["away_team"])

    return teams


def initialize_stats(teams):
    stats = {}

    for league, league_teams in teams.items():
        stats[league] = {
            team: empty_stats()
            for team in sorted(league_teams)
        }

    return stats


def calculate_ranks(league_stats):
    ordered = sorted(
        league_stats.items(),
        key=lambda item: (
            -item[1]["points"],
            -item[1]["goal_diff"],
            -item[1]["goals_for"],
            item[0],
        ),
    )

    ranks = {}
    previous_key = None
    current_rank = 1

    for index, (team, stats) in enumerate(
        ordered,
        start=1,
    ):
        rank_key = (
            stats["points"],
            stats["goal_diff"],
            stats["goals_for"],
        )

        if previous_key is not None and rank_key != previous_key:
            current_rank = index

        ranks[team] = current_rank
        previous_key = rank_key

    return ranks


def apply_result(team_stats, goals_for, goals_against):
    team_stats["played"] += 1
    team_stats["goals_for"] += goals_for
    team_stats["goals_against"] += goals_against
    team_stats["goal_diff"] = (
        team_stats["goals_for"]
        - team_stats["goals_against"]
    )

    if goals_for > goals_against:
        team_stats["win"] += 1
        team_stats["points"] += 3
    elif goals_for < goals_against:
        team_stats["lose"] += 1
    else:
        team_stats["draw"] += 1
        team_stats["points"] += 1


def build_rows(season, matches):
    teams = collect_teams(matches)
    stats = initialize_stats(teams)

    matches_by_date = defaultdict(list)

    for match in matches:
        matches_by_date[match["date_key"]].append(match)

    output_rows = []

    for date_key in sorted(matches_by_date):
        day_matches = matches_by_date[date_key]

        ranks_by_league = {
            league: calculate_ranks(league_stats)
            for league, league_stats in stats.items()
        }

        # 同日開催試合は、すべてその日の試合前状態を使用する
        for match in day_matches:
            league = match["league"]
            home_team = match["home_team"]
            away_team = match["away_team"]

            home = stats[league][home_team]
            away = stats[league][away_team]
            ranks = ranks_by_league[league]

            home_rank = ranks[home_team]
            away_rank = ranks[away_team]

            output_rows.append({
                "season": season,
                "jleague_match_id": match["match_id"],
                "league": league,
                "match_date": match["match_date"],
                "home_team": home_team,
                "away_team": away_team,

                "home_rank": home_rank,
                "away_rank": away_rank,
                "rank_diff": away_rank - home_rank,

                "home_played": home["played"],
                "away_played": away["played"],

                "home_points": home["points"],
                "away_points": away["points"],
                "points_diff": (
                    home["points"] - away["points"]
                ),

                "home_goal_diff": home["goal_diff"],
                "away_goal_diff": away["goal_diff"],
                "goal_diff_diff": (
                    home["goal_diff"]
                    - away["goal_diff"]
                ),
            })

        # スナップショット保存後に同日の結果を反映
        for match in day_matches:
            league = match["league"]
            home_team = match["home_team"]
            away_team = match["away_team"]
            home_score = match["home_score"]
            away_score = match["away_score"]

            apply_result(
                stats[league][home_team],
                home_score,
                away_score,
            )
            apply_result(
                stats[league][away_team],
                away_score,
                home_score,
            )

    return output_rows


def save_rows(con, season, rows):
    con.execute(
        """
        DELETE FROM match_pre_standings
        WHERE season = ?
        """,
        (season,),
    )

    con.executemany("""
        INSERT INTO match_pre_standings (
            season,
            jleague_match_id,
            league,
            match_date,
            home_team,
            away_team,

            home_rank,
            away_rank,
            rank_diff,

            home_played,
            away_played,

            home_points,
            away_points,
            points_diff,

            home_goal_diff,
            away_goal_diff,
            goal_diff_diff
        )
        VALUES (
            :season,
            :jleague_match_id,
            :league,
            :match_date,
            :home_team,
            :away_team,

            :home_rank,
            :away_rank,
            :rank_diff,

            :home_played,
            :away_played,

            :home_points,
            :away_points,
            :points_diff,

            :home_goal_diff,
            :away_goal_diff,
            :goal_diff_diff
        )
    """, rows)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Jリーグ各試合の直前順位・勝点・"
            "得失点差を生成します。"
        )
    )
    parser.add_argument(
        "season",
        type=int,
        help="対象年度。例: 2002",
    )

    args = parser.parse_args()
    season = args.season

    con = sqlite3.connect(DB_PATH)

    try:
        create_table(con)

        matches = load_matches(
            con=con,
            season=season,
        )

        if not matches:
            raise RuntimeError(
                f"{season}年のJ1/J2試合がありません"
            )

        rows = build_rows(
            season=season,
            matches=matches,
        )

        save_rows(
            con=con,
            season=season,
            rows=rows,
        )

        con.commit()

        league_counts = defaultdict(int)

        for row in rows:
            league_counts[row["league"]] += 1

        print(f"対象年度: {season}")
        print(f"試合読込: {len(matches)}件")
        print(f"順位特徴量保存: {len(rows)}件")

        for league in sorted(league_counts):
            print(
                f"{league}: "
                f"{league_counts[league]}件"
            )

        print("match_pre_standings 作成完了")

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    main()
