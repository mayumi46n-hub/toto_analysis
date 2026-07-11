import sqlite3
from pathlib import Path

from analysis.form import build_team_histories, get_form_points

DB_PATH = Path("data/toto.db")

SEASON = 2001
START_ROUND = 1
END_ROUND = 31
FEATURE_VERSION = 3
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


def load_form_matches(con):
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


def load_standings(con):
    rows = con.execute("""
        SELECT
            round_no,
            league,
            team,
            rank,
            points,
            goal_diff
        FROM round_standings
        WHERE season = ?
          AND league IN ('J1', 'J2')
    """, (SEASON,)).fetchall()

    return {
        (round_no, league, team): {
            "rank": rank,
            "points": points,
            "goal_diff": goal_diff,
        }
        for (
            round_no,
            league,
            team,
            rank,
            points,
            goal_diff,
        ) in rows
    }


def find_team_features(
    standings,
    pre_round,
    home_team,
    away_team,
):
    for league in ("J1", "J2"):
        home = standings.get(
            (pre_round, league, home_team)
        )
        away = standings.get(
            (pre_round, league, away_team)
        )

        if home is not None and away is not None:
            return league, home, away

    return None


def build_features(matches, standings, histories):
    feature_rows = []
    skipped = []

    for (
        round_no,
        match_no,
        home_team,
        away_team,
        result,
    ) in matches:
        pre_round = round_no - 1

        found = find_team_features(
            standings=standings,
            pre_round=pre_round,
            home_team=home_team,
            away_team=away_team,
        )

        if found is None:
            skipped.append((
                round_no,
                match_no,
                home_team,
                away_team,
            ))
            continue

        league, home, away = found

        home_form_points = get_form_points(
            histories=histories,
            team=home_team,
            before_round=round_no,
            window=FORM_WINDOW,
        )

        away_form_points = get_form_points(
            histories=histories,
            team=away_team,
            before_round=round_no,
            window=FORM_WINDOW,
        )

        home_home_form_points = get_form_points(
            histories=histories,
            team=home_team,
            before_round=round_no,
            window=FORM_WINDOW,
            venue="H",
        )

        away_away_form_points = get_form_points(
            histories=histories,
            team=away_team,
            before_round=round_no,
            window=FORM_WINDOW,
            venue="A",
        )

        feature_rows.append((
            FEATURE_VERSION,
            SEASON,
            round_no,
            match_no,
            league,
            home_team,
            away_team,

            home["rank"],
            away["rank"],
            away["rank"] - home["rank"],

            home["points"],
            away["points"],
            home["points"] - away["points"],

            home["goal_diff"],
            away["goal_diff"],
            home["goal_diff"] - away["goal_diff"],

            home_form_points,
            away_form_points,
            home_form_points - away_form_points,

            home_home_form_points,
            away_away_form_points,
            home_home_form_points - away_away_form_points,

            result,
        ))

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

            result
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?
        )
    """, rows)


def main():
    con = connect_db()

    try:
        create_table(con)

        matches = load_matches(con)
        standings = load_standings(con)
        form_matches = load_form_matches(con)

        histories = build_team_histories(form_matches)

        rows, skipped = build_features(
            matches=matches,
            standings=standings,
            histories=histories,
        )

        insert_features(con, rows)
        con.commit()

        print(f"試合データ読込: {len(matches)}件")
        print(f"フォーム計算対象: {len(form_matches)}件")
        print(f"特徴量作成: {len(rows)}件")
        print(f"未作成: {len(skipped)}件")

        if skipped:
            print("\n未作成試合（先頭10件）")
            for item in skipped[:10]:
                print(item)

        print("\nFeature Builder Version 3 完了")

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    main()