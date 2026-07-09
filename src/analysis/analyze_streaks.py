import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

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


def result_for_team(team, home_team, away_team, home_score, away_score):
    if team == home_team:
        goals_for = home_score
        goals_against = away_score
    else:
        goals_for = away_score
        goals_against = home_score

    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def build_team_results(matches):
    team_results = defaultdict(list)

    for round_no, match_no, home_team, away_team, home_score, away_score in matches:
        for team in [home_team, away_team]:
            result = result_for_team(
                team,
                home_team,
                away_team,
                home_score,
                away_score,
            )

            team_results[team].append({
                "round_no": round_no,
                "match_no": match_no,
                "opponent": away_team if team == home_team else home_team,
                "venue": "H" if team == home_team else "A",
                "result": result,
                "goals_for": home_score if team == home_team else away_score,
                "goals_against": away_score if team == home_team else home_score,
            })

    return team_results


def max_streak(results, target_result):
    current = 0
    best = 0

    for row in results:
        if row["result"] == target_result:
            current += 1
            best = max(best, current)
        else:
            current = 0

    return best


def current_streak(results):
    if not results:
        return "", 0

    last_result = results[-1]["result"]
    count = 0

    for row in reversed(results):
        if row["result"] == last_result:
            count += 1
        else:
            break

    return last_result, count


def calculate_streaks(team_results):
    rows = []

    for team, results in team_results.items():
        wins = sum(1 for r in results if r["result"] == "W")
        draws = sum(1 for r in results if r["result"] == "D")
        losses = sum(1 for r in results if r["result"] == "L")

        current_result, current_count = current_streak(results)

        rows.append({
            "team": team,
            "matches": len(results),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "max_win_streak": max_streak(results, "W"),
            "max_draw_streak": max_streak(results, "D"),
            "max_loss_streak": max_streak(results, "L"),
            "current_result": current_result,
            "current_count": current_count,
        })

    rows.sort(key=lambda r: (-r["max_win_streak"], -r["wins"], r["team"]))
    return rows


def print_report(rows, start_round, end_round):
    print("=" * 60)
    print(f"連勝・連敗分析: 第{start_round}回〜第{end_round}回")
    print("=" * 60)

    print("\n最大連勝 TOP10")
    for row in rows[:10]:
        print(
            f"{row['team']}: "
            f"最大{row['max_win_streak']}連勝 "
            f"({row['wins']}勝{row['draws']}分{row['losses']}敗)"
        )

    print("\n最大連敗 TOP10")
    loss_rows = sorted(
        rows,
        key=lambda r: (-r["max_loss_streak"], -r["losses"], r["team"])
    )

    for row in loss_rows[:10]:
        print(
            f"{row['team']}: "
            f"最大{row['max_loss_streak']}連敗 "
            f"({row['wins']}勝{row['draws']}分{row['losses']}敗)"
        )

    print("\n現在の継続状態")
    label = {
        "W": "連勝中",
        "D": "引き分け中",
        "L": "連敗中",
    }

    current_rows = sorted(
        rows,
        key=lambda r: (-r["current_count"], r["team"])
    )

    for row in current_rows[:15]:
        print(
            f"{row['team']}: "
            f"{row['current_count']}{label.get(row['current_result'], '')}"
        )


def main():
    start_round = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
    end_round = int(sys.argv[2]) if len(sys.argv) >= 3 else 31

    con = connect_db()
    matches = load_matches(con, start_round, end_round)
    con.close()

    if not matches:
        print("対象データがありません")
        sys.exit(1)

    team_results = build_team_results(matches)
    rows = calculate_streaks(team_results)
    print_report(rows, start_round, end_round)


if __name__ == "__main__":
    main()