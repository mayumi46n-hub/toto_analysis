import sqlite3
import sys
from pathlib import Path

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
            away_score,
            result
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY round_no, match_no
    """, (start_round, end_round))

    return cur.fetchall()


def calculate_stats(matches):
    total_matches = len(matches)

    home_goals = [row[4] for row in matches]
    away_goals = [row[5] for row in matches]
    total_goals = [row[4] + row[5] for row in matches]

    score_counts = {}
    total_goal_counts = {}

    for row in matches:
        home_score = row[4]
        away_score = row[5]

        score_key = f"{home_score}-{away_score}"
        score_counts[score_key] = score_counts.get(score_key, 0) + 1

        goal_sum = home_score + away_score
        total_goal_counts[goal_sum] = total_goal_counts.get(goal_sum, 0) + 1

    return {
        "total_matches": total_matches,
        "home_avg": sum(home_goals) / total_matches,
        "away_avg": sum(away_goals) / total_matches,
        "total_avg": sum(total_goals) / total_matches,
        "home_zero_rate": home_goals.count(0) * 100.0 / total_matches,
        "away_zero_rate": away_goals.count(0) * 100.0 / total_matches,
        "home_max": max(home_goals),
        "away_max": max(away_goals),
        "score_counts": score_counts,
        "total_goal_counts": total_goal_counts,
    }


def print_report(stats, start_round, end_round):
    print("=" * 40)
    print(f"得点分析: 第{start_round}回〜第{end_round}回")
    print("=" * 40)

    print(f"総試合数          : {stats['total_matches']}")
    print(f"ホーム平均得点    : {stats['home_avg']:.2f}")
    print(f"アウェイ平均得点  : {stats['away_avg']:.2f}")
    print(f"平均総得点        : {stats['total_avg']:.2f}")
    print(f"ホーム無得点率    : {stats['home_zero_rate']:.2f}%")
    print(f"アウェイ無得点率  : {stats['away_zero_rate']:.2f}%")
    print(f"ホーム最多得点    : {stats['home_max']}")
    print(f"アウェイ最多得点  : {stats['away_max']}")

    print("\n総得点分布")
    for goals in sorted(stats["total_goal_counts"]):
        print(f"{goals}点: {stats['total_goal_counts'][goals]}試合")

    print("\nスコア出現 TOP15")
    sorted_scores = sorted(
        stats["score_counts"].items(),
        key=lambda x: (-x[1], x[0])
    )

    for score, count in sorted_scores[:15]:
        print(f"{score}: {count}試合")


def main():
    start_round = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
    end_round = int(sys.argv[2]) if len(sys.argv) >= 3 else 31

    con = connect_db()
    matches = load_matches(con, start_round, end_round)
    con.close()

    if not matches:
        print("対象データがありません")
        sys.exit(1)

    stats = calculate_stats(matches)
    print_report(stats, start_round, end_round)


if __name__ == "__main__":
    main()