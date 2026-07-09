import sqlite3
import sys
from pathlib import Path
from collections import defaultdict, deque

DB_PATH = Path("data/toto.db")


def connect_db():
    return sqlite3.connect(DB_PATH)


def load_matches(con, start_round, end_round):
    cur = con.cursor()
    cur.execute("""
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
    """, (start_round, end_round))

    return cur.fetchall()


def team_match_result(team, home_team, away_team, home_score, away_score):
    if team == home_team:
        goals_for = home_score
        goals_against = away_score
        venue = "H"
    else:
        goals_for = away_score
        goals_against = home_score
        venue = "A"

    if goals_for > goals_against:
        result = "W"
        points = 3
    elif goals_for < goals_against:
        result = "L"
        points = 0
    else:
        result = "D"
        points = 1

    return {
        "venue": venue,
        "result": result,
        "points": points,
        "goals_for": goals_for,
        "goals_against": goals_against,
    }


def build_team_histories(matches):
    histories = defaultdict(list)

    for round_no, match_no, home_team, away_team, home_score, away_score in matches:
        for team in [home_team, away_team]:
            row = team_match_result(
                team,
                home_team,
                away_team,
                home_score,
                away_score,
            )
            row["round_no"] = round_no
            row["match_no"] = match_no
            row["opponent"] = away_team if team == home_team else home_team

            histories[team].append(row)

    return histories


def calculate_recent_form(results, window):
    recent = results[-window:]

    if not recent:
        return {
            "matches": 0,
            "points": 0,
            "max_points": 0,
            "form_rate": 0,
            "avg_goals_for": 0,
            "avg_goals_against": 0,
            "goal_diff": 0,
            "sequence": "",
        }

    points = sum(r["points"] for r in recent)
    goals_for = sum(r["goals_for"] for r in recent)
    goals_against = sum(r["goals_against"] for r in recent)
    matches = len(recent)
    max_points = matches * 3

    return {
        "matches": matches,
        "points": points,
        "max_points": max_points,
        "form_rate": points * 100.0 / max_points if max_points else 0,
        "avg_goals_for": goals_for / matches,
        "avg_goals_against": goals_against / matches,
        "goal_diff": goals_for - goals_against,
        "sequence": "".join(r["result"] for r in recent),
    }


def calculate_team_forms(histories, window):
    rows = []

    for team, results in histories.items():
        form = calculate_recent_form(results, window)

        rows.append({
            "team": team,
            **form,
        })

    rows.sort(
        key=lambda r: (
            -r["form_rate"],
            -r["points"],
            -r["goal_diff"],
            r["team"],
        )
    )

    return rows


def print_report(rows, start_round, end_round, window):
    print("=" * 70)
    print(f"フォーム分析: 第{start_round}回〜第{end_round}回 / 直近{window}試合")
    print("=" * 70)

    print("\n好調チーム TOP10")
    for row in rows[:10]:
        print(
            f"{row['team']}: "
            f"{row['points']}/{row['max_points']}点 "
            f"({row['form_rate']:.1f}%) "
            f"得点{row['avg_goals_for']:.2f} "
            f"失点{row['avg_goals_against']:.2f} "
            f"得失点差{row['goal_diff']} "
            f"[{row['sequence']}]"
        )

    print("\n不調チーム TOP10")
    bad_rows = sorted(
        rows,
        key=lambda r: (
            r["form_rate"],
            r["points"],
            r["goal_diff"],
            r["team"],
        )
    )

    for row in bad_rows[:10]:
        print(
            f"{row['team']}: "
            f"{row['points']}/{row['max_points']}点 "
            f"({row['form_rate']:.1f}%) "
            f"得点{row['avg_goals_for']:.2f} "
            f"失点{row['avg_goals_against']:.2f} "
            f"得失点差{row['goal_diff']} "
            f"[{row['sequence']}]"
        )


def main():
    start_round = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
    end_round = int(sys.argv[2]) if len(sys.argv) >= 3 else 31
    window = int(sys.argv[3]) if len(sys.argv) >= 4 else 5

    con = connect_db()
    matches = load_matches(con, start_round, end_round)
    con.close()

    if not matches:
        print("対象データがありません")
        sys.exit(1)

    histories = build_team_histories(matches)
    rows = calculate_team_forms(histories, window)
    print_report(rows, start_round, end_round, window)


if __name__ == "__main__":
    main()