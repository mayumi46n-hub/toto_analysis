import sqlite3
from pathlib import Path

from features.form import (
    build_team_histories,
    get_form_points,
)
from features.h2h import (
    build_h2h_histories,
    get_h2h_features,
)
from features.standings import (
    get_standing_features,
    load_standings,
)

DB_PATH = Path("data/toto.db")

SEASON = 2001
START_ROUND = 1
END_ROUND = 31
FEATURE_VERSION = 4
FORM_WINDOW = 5


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_table(con):
    con.execute("DROP TABLE IF EXISTS match_features")

    con.execute("""
        CREATE TABLE match_features (
            feature_version INTEGER NOT NULL,
            season INTEGER NOT NULL,
            round_no INTEGER NOT NULL,
            match_no INTEGER NOT NULL,
            league TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,

            home_rank INTEGER NOT NULL,
            away_rank INTEGER NOT NULL,
            rank_diff INTEGER NOT NULL,

            home_points INTEGER NOT NULL,
            away_points INTEGER NOT NULL,
            points_diff INTEGER NOT NULL,

            home_goal_diff INTEGER NOT NULL,
            away_goal_diff INTEGER NOT NULL,
            goal_diff_diff INTEGER NOT NULL,

            home_form_points INTEGER NOT NULL,
            away_form_points INTEGER NOT NULL,
            form_diff INTEGER NOT NULL,

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

            PRIMARY KEY (
                feature_version,
                season,
                round_no,
                match_no
            )
        )
    """)


def load_matches(con):
    return con.execute("""
        SELECT
            round_no,
            match_no,
            home_team,
            away_team,
            result
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
          AND result IN ('1', '0', '2')
        ORDER BY round_no, match_no
    """, (START_ROUND, END_ROUND)).fetchall()


def load_result_matches(con):
    return con.execute("""
        SELECT
            round_no,
            match_no,
            home_team,
            away_team,
            home_score,
            away_score
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY round_no, match_no
    """, (START_ROUND, END_ROUND)).fetchall()


def build_features(
    matches,
    standings,
    form_histories,
    h2h_histories,
):
    feature_rows = []
    skipped = []

    for (
        round_no,
        match_no,
        home_team,
        away_team,
        result,
    ) in matches:
        standing = get_standing_features(
            standings=standings,
            pre_round=round_no - 1,
            home_team=home_team,
            away_team=away_team,
        )

        if standing is None:
            skipped.append((
                round_no,
                match_no,
                home_team,
                away_team,
            ))
            continue

        home_form_points = get_form_points(
            histories=form_histories,
            team=home_team,
            before_round=round_no,
            window=FORM_WINDOW,
        )

        away_form_points = get_form_points(
            histories=form_histories,
            team=away_team,
            before_round=round_no,
            window=FORM_WINDOW,
        )

        home_home_form_points = get_form_points(
            histories=form_histories,
            team=home_team,
            before_round=round_no,
            window=FORM_WINDOW,
            venue="H",
        )

        away_away_form_points = get_form_points(
            histories=form_histories,
            team=away_team,
            before_round=round_no,
            window=FORM_WINDOW,
            venue="A",
        )

        h2h = get_h2h_features(
            histories=h2h_histories,
            home_team=home_team,
            away_team=away_team,
            before_round=round_no,
        )

        feature_rows.append({
            "feature_version": FEATURE_VERSION,
            "season": SEASON,
            "round_no": round_no,
            "match_no": match_no,
            "league": standing["league"],
            "home_team": home_team,
            "away_team": away_team,

            "home_rank": standing["home_rank"],
            "away_rank": standing["away_rank"],
            "rank_diff": standing["rank_diff"],

            "home_points": standing["home_points"],
            "away_points": standing["away_points"],
            "points_diff": standing["points_diff"],

            "home_goal_diff": standing["home_goal_diff"],
            "away_goal_diff": standing["away_goal_diff"],
            "goal_diff_diff": standing["goal_diff_diff"],

            "home_form_points": home_form_points,
            "away_form_points": away_form_points,
            "form_diff": (
                home_form_points - away_form_points
            ),

            "home_home_form_points": (
                home_home_form_points
            ),
            "away_away_form_points": (
                away_away_form_points
            ),
            "venue_form_diff": (
                home_home_form_points
                - away_away_form_points
            ),

            **h2h,

            "result": result,
        })

    return feature_rows, skipped


def insert_features(con, rows):
    con.executemany("""
        INSERT INTO match_features (
            feature_version,
            season,
            round_no,
            match_no,
            league,
            home_team,
            away_team,

            home_rank,
            away_rank,
            rank_diff,

            home_points,
            away_points,
            points_diff,

            home_goal_diff,
            away_goal_diff,
            goal_diff_diff,

            home_form_points,
            away_form_points,
            form_diff,

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

            result
        )
        VALUES (
            :feature_version,
            :season,
            :round_no,
            :match_no,
            :league,
            :home_team,
            :away_team,

            :home_rank,
            :away_rank,
            :rank_diff,

            :home_points,
            :away_points,
            :points_diff,

            :home_goal_diff,
            :away_goal_diff,
            :goal_diff_diff,

            :home_form_points,
            :away_form_points,
            :form_diff,

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

            :result
        )
    """, rows)


def main():
    con = connect_db()

    try:
        create_table(con)

        matches = load_matches(con)
        result_matches = load_result_matches(con)

        standings = load_standings(
            con=con,
            season=SEASON,
        )

        form_histories = build_team_histories(
            result_matches
        )

        h2h_histories = build_h2h_histories(
            result_matches
        )

        rows, skipped = build_features(
            matches=matches,
            standings=standings,
            form_histories=form_histories,
            h2h_histories=h2h_histories,
        )

        insert_features(con, rows)
        con.commit()

        print(f"試合データ読込: {len(matches)}件")
        print(f"履歴計算対象: {len(result_matches)}件")
        print(f"特徴量作成: {len(rows)}件")
        print(f"未作成: {len(skipped)}件")

        if skipped:
            print("\n未作成試合（先頭10件）")
            for item in skipped[:10]:
                print(item)

        print("\nFeature Builder Version 4 完了")

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    main()