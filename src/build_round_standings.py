import sqlite3
from collections import defaultdict

DB = "data/toto.db"
SEASON = 2001
START_ROUND = 1
END_ROUND = 31
LEAGUE = "ALL"


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


def apply_match(stats, team, goals_for, goals_against):
    stats[team]["played"] += 1
    stats[team]["goals_for"] += goals_for
    stats[team]["goals_against"] += goals_against
    stats[team]["goal_diff"] = stats[team]["goals_for"] - stats[team]["goals_against"]

    if goals_for > goals_against:
        stats[team]["win"] += 1
        stats[team]["points"] += 3
    elif goals_for < goals_against:
        stats[team]["lose"] += 1
    else:
        stats[team]["draw"] += 1
        stats[team]["points"] += 1


def calculate_ranking(stats):
    rows = []

    for team, s in stats.items():
        rows.append({
            "team": team,
            **s,
        })

    rows.sort(
        key=lambda r: (
            -r["points"],
            -r["goal_diff"],
            -r["goals_for"],
            r["team"],
        )
    )

    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    return rows


def load_round_matches(cur, round_no):
    cur.execute("""
        SELECT
            home_team,
            away_team,
            home_score,
            away_score
        FROM toto_matches
        WHERE round_no = ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY match_no
    """, (round_no,))
    return cur.fetchall()


def save_standings(cur, round_no, ranking_rows):
    for row in ranking_rows:
        cur.execute("""
            INSERT OR REPLACE INTO round_standings (
                season,
                round_no,
                league,
                team,
                rank,
                played,
                win,
                draw,
                lose,
                goals_for,
                goals_against,
                goal_diff,
                points
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            SEASON,
            round_no,
            LEAGUE,
            row["team"],
            row["rank"],
            row["played"],
            row["win"],
            row["draw"],
            row["lose"],
            row["goals_for"],
            row["goals_against"],
            row["goal_diff"],
            row["points"],
        ))


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        DELETE FROM round_standings
        WHERE season = ?
          AND round_no BETWEEN ? AND ?
          AND league = ?
    """, (SEASON, START_ROUND, END_ROUND, LEAGUE))

    stats = defaultdict(empty_stats)

    for round_no in range(START_ROUND, END_ROUND + 1):
        matches = load_round_matches(cur, round_no)

        for home_team, away_team, home_score, away_score in matches:
            apply_match(stats, home_team, home_score, away_score)
            apply_match(stats, away_team, away_score, home_score)

        ranking_rows = calculate_ranking(stats)
        save_standings(cur, round_no, ranking_rows)

        print(f"第{round_no}回: {len(ranking_rows)}チーム順位を保存")

    con.commit()
    con.close()

    print("round_standings 作成完了")


if __name__ == "__main__":
    main()