import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path("data/toto.db")

FEATURE_VERSION = 1
FORM_WINDOW = 5


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


def result_and_points(home_score, away_score):
    if home_score > away_score:
        return "1", 3, 0

    if home_score < away_score:
        return "2", 0, 3

    return "0", 1, 1


def create_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS match_features_season (
            feature_version INTEGER NOT NULL,
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

            home_form_matches INTEGER NOT NULL,
            away_form_matches INTEGER NOT NULL,
            home_form_points INTEGER NOT NULL,
            away_form_points INTEGER NOT NULL,
            form_diff INTEGER NOT NULL,

            home_home_form_matches INTEGER NOT NULL,
            away_away_form_matches INTEGER NOT NULL,
            home_home_form_points INTEGER NOT NULL,
            away_away_form_points INTEGER NOT NULL,
            venue_form_diff INTEGER NOT NULL,

            h2h_last5_matches INTEGER NOT NULL,
            h2h_last5_home_points INTEGER NOT NULL,
            h2h_last5_away_points INTEGER NOT NULL,
            h2h_last5_diff INTEGER NOT NULL,

            h2h_last10_matches INTEGER NOT NULL,
            h2h_last10_home_points INTEGER NOT NULL,
            h2h_last10_away_points INTEGER NOT NULL,
            h2h_last10_diff INTEGER NOT NULL,

            h2h_all_matches INTEGER NOT NULL,
            h2h_all_home_points INTEGER NOT NULL,
            h2h_all_away_points INTEGER NOT NULL,
            h2h_all_diff INTEGER NOT NULL,

            h2h_same_venue_last5_matches INTEGER NOT NULL,
            h2h_same_venue_last5_home_points INTEGER NOT NULL,
            h2h_same_venue_last5_away_points INTEGER NOT NULL,
            h2h_same_venue_last5_diff INTEGER NOT NULL,

            result TEXT NOT NULL,
            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,

            PRIMARY KEY (
                feature_version,
                season,
                jleague_match_id
            )
        )
    """)


def load_matches(con, season):
    rows = con.execute("""
        SELECT
            jm.jleague_match_id,
            jm.match_date,
            jm.kickoff_time,
            jm.home_team,
            jm.away_team,
            jm.home_score,
            jm.away_score,

            ps.league,
            ps.home_rank,
            ps.away_rank,
            ps.rank_diff,

            ps.home_played,
            ps.away_played,

            ps.home_points,
            ps.away_points,
            ps.points_diff,

            ps.home_goal_diff,
            ps.away_goal_diff,
            ps.goal_diff_diff
        FROM jleague_matches AS jm
        INNER JOIN match_pre_standings AS ps
            ON ps.season = jm.season
           AND ps.jleague_match_id = jm.jleague_match_id
        WHERE jm.season = ?
          AND jm.home_score IS NOT NULL
          AND jm.away_score IS NOT NULL
        ORDER BY
            jm.match_date,
            jm.kickoff_time,
            jm.jleague_match_id
    """, (season,)).fetchall()

    matches = []

    for row in rows:
        (
            match_id,
            match_date,
            kickoff_time,
            home_team,
            away_team,
            home_score,
            away_score,
            league,
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
            goal_diff_diff,
        ) = row

        matches.append({
            "match_id": match_id,
            "match_date": match_date,
            "date_key": parse_match_date(match_date),
            "kickoff_time": kickoff_time or "",
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "league": league,

            "home_rank": home_rank,
            "away_rank": away_rank,
            "rank_diff": rank_diff,

            "home_played": home_played,
            "away_played": away_played,

            "home_points": home_points,
            "away_points": away_points,
            "points_diff": points_diff,

            "home_goal_diff": home_goal_diff,
            "away_goal_diff": away_goal_diff,
            "goal_diff_diff": goal_diff_diff,
        })

    return matches


def summarize_team_form(
    history,
    window,
    venue=None,
):
    eligible = [
        match
        for match in history
        if venue is None or match["venue"] == venue
    ]

    recent = eligible[-window:]

    return {
        "matches": len(recent),
        "points": sum(
            match["points"]
            for match in recent
        ),
    }


def team_points_in_h2h(match, team):
    if team == match["home_team"]:
        return match["home_points"]

    return match["away_points"]


def summarize_h2h(
    matches,
    home_team,
    away_team,
):
    home_points = sum(
        team_points_in_h2h(match, home_team)
        for match in matches
    )

    away_points = sum(
        team_points_in_h2h(match, away_team)
        for match in matches
    )

    return {
        "matches": len(matches),
        "home_points": home_points,
        "away_points": away_points,
        "diff": home_points - away_points,
    }


def get_h2h_features(
    pair_history,
    home_team,
    away_team,
):
    pair_key = tuple(sorted((
        home_team,
        away_team,
    )))

    history = pair_history.get(pair_key, [])

    same_venue = [
        match
        for match in history
        if match["home_team"] == home_team
        and match["away_team"] == away_team
    ]

    last5 = summarize_h2h(
        history[-5:],
        home_team,
        away_team,
    )

    last10 = summarize_h2h(
        history[-10:],
        home_team,
        away_team,
    )

    all_matches = summarize_h2h(
        history,
        home_team,
        away_team,
    )

    same_venue_last5 = summarize_h2h(
        same_venue[-5:],
        home_team,
        away_team,
    )

    return {
        "h2h_last5_matches": last5["matches"],
        "h2h_last5_home_points": last5["home_points"],
        "h2h_last5_away_points": last5["away_points"],
        "h2h_last5_diff": last5["diff"],

        "h2h_last10_matches": last10["matches"],
        "h2h_last10_home_points": last10["home_points"],
        "h2h_last10_away_points": last10["away_points"],
        "h2h_last10_diff": last10["diff"],

        "h2h_all_matches": all_matches["matches"],
        "h2h_all_home_points": all_matches["home_points"],
        "h2h_all_away_points": all_matches["away_points"],
        "h2h_all_diff": all_matches["diff"],

        "h2h_same_venue_last5_matches": (
            same_venue_last5["matches"]
        ),
        "h2h_same_venue_last5_home_points": (
            same_venue_last5["home_points"]
        ),
        "h2h_same_venue_last5_away_points": (
            same_venue_last5["away_points"]
        ),
        "h2h_same_venue_last5_diff": (
            same_venue_last5["diff"]
        ),
    }


def build_feature_rows(season, matches):
    team_history = defaultdict(list)
    pair_history = defaultdict(list)
    matches_by_date = defaultdict(list)

    for match in matches:
        matches_by_date[match["date_key"]].append(
            match
        )

    feature_rows = []

    for date_key in sorted(matches_by_date):
        day_matches = matches_by_date[date_key]

        # 同日の全試合について、結果反映前に特徴量を生成
        for match in day_matches:
            home_team = match["home_team"]
            away_team = match["away_team"]

            home_form = summarize_team_form(
                team_history[home_team],
                window=FORM_WINDOW,
            )

            away_form = summarize_team_form(
                team_history[away_team],
                window=FORM_WINDOW,
            )

            home_venue_form = summarize_team_form(
                team_history[home_team],
                window=FORM_WINDOW,
                venue="H",
            )

            away_venue_form = summarize_team_form(
                team_history[away_team],
                window=FORM_WINDOW,
                venue="A",
            )

            h2h = get_h2h_features(
                pair_history=pair_history,
                home_team=home_team,
                away_team=away_team,
            )

            result, _, _ = result_and_points(
                match["home_score"],
                match["away_score"],
            )

            feature_rows.append({
                "feature_version": FEATURE_VERSION,
                "season": season,
                "jleague_match_id": match["match_id"],

                "league": match["league"],
                "match_date": match["match_date"],
                "home_team": home_team,
                "away_team": away_team,

                "home_rank": match["home_rank"],
                "away_rank": match["away_rank"],
                "rank_diff": match["rank_diff"],

                "home_played": match["home_played"],
                "away_played": match["away_played"],

                "home_points": match["home_points"],
                "away_points": match["away_points"],
                "points_diff": match["points_diff"],

                "home_goal_diff": (
                    match["home_goal_diff"]
                ),
                "away_goal_diff": (
                    match["away_goal_diff"]
                ),
                "goal_diff_diff": (
                    match["goal_diff_diff"]
                ),

                "home_form_matches": (
                    home_form["matches"]
                ),
                "away_form_matches": (
                    away_form["matches"]
                ),
                "home_form_points": (
                    home_form["points"]
                ),
                "away_form_points": (
                    away_form["points"]
                ),
                "form_diff": (
                    home_form["points"]
                    - away_form["points"]
                ),

                "home_home_form_matches": (
                    home_venue_form["matches"]
                ),
                "away_away_form_matches": (
                    away_venue_form["matches"]
                ),
                "home_home_form_points": (
                    home_venue_form["points"]
                ),
                "away_away_form_points": (
                    away_venue_form["points"]
                ),
                "venue_form_diff": (
                    home_venue_form["points"]
                    - away_venue_form["points"]
                ),

                **h2h,

                "result": result,
                "home_score": match["home_score"],
                "away_score": match["away_score"],
            })

        # 同日全試合の特徴量生成後に結果を履歴へ反映
        for match in day_matches:
            home_team = match["home_team"]
            away_team = match["away_team"]

            _, home_points, away_points = (
                result_and_points(
                    match["home_score"],
                    match["away_score"],
                )
            )

            team_history[home_team].append({
                "date_key": date_key,
                "venue": "H",
                "points": home_points,
            })

            team_history[away_team].append({
                "date_key": date_key,
                "venue": "A",
                "points": away_points,
            })

            pair_key = tuple(sorted((
                home_team,
                away_team,
            )))

            pair_history[pair_key].append({
                "date_key": date_key,
                "home_team": home_team,
                "away_team": away_team,
                "home_points": home_points,
                "away_points": away_points,
            })

    return feature_rows


def save_rows(con, season, rows):
    con.execute("""
        DELETE FROM match_features_season
        WHERE feature_version = ?
          AND season = ?
    """, (
        FEATURE_VERSION,
        season,
    ))

    con.executemany("""
        INSERT INTO match_features_season (
            feature_version,
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
            goal_diff_diff,

            home_form_matches,
            away_form_matches,
            home_form_points,
            away_form_points,
            form_diff,

            home_home_form_matches,
            away_away_form_matches,
            home_home_form_points,
            away_away_form_points,
            venue_form_diff,

            h2h_last5_matches,
            h2h_last5_home_points,
            h2h_last5_away_points,
            h2h_last5_diff,

            h2h_last10_matches,
            h2h_last10_home_points,
            h2h_last10_away_points,
            h2h_last10_diff,

            h2h_all_matches,
            h2h_all_home_points,
            h2h_all_away_points,
            h2h_all_diff,

            h2h_same_venue_last5_matches,
            h2h_same_venue_last5_home_points,
            h2h_same_venue_last5_away_points,
            h2h_same_venue_last5_diff,

            result,
            home_score,
            away_score
        )
        VALUES (
            :feature_version,
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
            :goal_diff_diff,

            :home_form_matches,
            :away_form_matches,
            :home_form_points,
            :away_form_points,
            :form_diff,

            :home_home_form_matches,
            :away_away_form_matches,
            :home_home_form_points,
            :away_away_form_points,
            :venue_form_diff,

            :h2h_last5_matches,
            :h2h_last5_home_points,
            :h2h_last5_away_points,
            :h2h_last5_diff,

            :h2h_last10_matches,
            :h2h_last10_home_points,
            :h2h_last10_away_points,
            :h2h_last10_diff,

            :h2h_all_matches,
            :h2h_all_home_points,
            :h2h_all_away_points,
            :h2h_all_diff,

            :h2h_same_venue_last5_matches,
            :h2h_same_venue_last5_home_points,
            :h2h_same_venue_last5_away_points,
            :h2h_same_venue_last5_diff,

            :result,
            :home_score,
            :away_score
        )
    """, rows)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Jリーグ全試合向けの試合前特徴量を"
            "生成します。"
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
                f"{season}年の対象試合がありません。"
                "先にbuild_match_standings.pyを実行してください。"
            )

        rows = build_feature_rows(
            season=season,
            matches=matches,
        )

        save_rows(
            con=con,
            season=season,
            rows=rows,
        )

        con.commit()

        print(f"対象年度: {season}")
        print(f"試合読込: {len(matches)}件")
        print(f"特徴量保存: {len(rows)}件")
        print(
            "match_features_season "
            "Version 1 作成完了"
        )

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    main()