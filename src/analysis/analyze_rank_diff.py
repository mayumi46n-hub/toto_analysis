import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("data/toto.db")
SEASON = 2001


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
            result
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
        ORDER BY round_no, match_no
    """, (start_round, end_round))
    return cur.fetchall()


def load_standings(con):
    cur = con.cursor()
    cur.execute("""
        SELECT
            round_no,
            league,
            team,
            rank
        FROM round_standings
        WHERE season = ?
    """, (SEASON,))

    standings = {}

    for round_no, league, team, rank in cur.fetchall():
        standings[(round_no, league, team)] = rank

    return standings


def find_league_and_ranks(standings, pre_round, home_team, away_team):
    for league in ["J1", "J2"]:
        home_rank = standings.get((pre_round, league, home_team))
        away_rank = standings.get((pre_round, league, away_team))

        if home_rank is not None and away_rank is not None:
            return league, home_rank, away_rank

    return None, None, None


def rank_diff_bucket(diff):
    if diff == 0:
        return "0"
    if 1 <= abs(diff) <= 2:
        return "1-2"
    if 3 <= abs(diff) <= 5:
        return "3-5"
    if 6 <= abs(diff) <= 9:
        return "6-9"
    return "10+"


def add_result(counter, result):
    counter["total"] += 1
    counter[result] += 1


def percent(count, total):
    if total == 0:
        return 0.0
    return count * 100.0 / total


def analyze(matches, standings):
    by_signed_diff = defaultdict(lambda: defaultdict(int))
    by_abs_bucket = defaultdict(lambda: defaultdict(int))
    skipped = []

    for round_no, match_no, home_team, away_team, result in matches:
        pre_round = round_no - 1

        league, home_rank, away_rank = find_league_and_ranks(
            standings,
            pre_round,
            home_team,
            away_team,
        )

        if league is None:
            skipped.append((round_no, match_no, home_team, away_team))
            continue

        # 正の値: ホームの方が上位
        # 負の値: アウェイの方が上位
        diff = away_rank - home_rank

        add_result(by_signed_diff[diff], result)
        add_result(by_abs_bucket[rank_diff_bucket(diff)], result)

    return by_signed_diff, by_abs_bucket, skipped


def print_counter(counter):
    total = counter["total"]
    home = counter["1"]
    draw = counter["0"]
    away = counter["2"]

    print(
        f"{total:3d}試合 | "
        f"1 ホーム勝ち {home:3d} ({percent(home, total):5.1f}%) | "
        f"0 引分 {draw:3d} ({percent(draw, total):5.1f}%) | "
        f"2 アウェイ勝ち {away:3d} ({percent(away, total):5.1f}%)"
    )


def print_report(by_signed_diff, by_abs_bucket, skipped, start_round, end_round):
    print("=" * 80)
    print(f"順位差分析: 第{start_round}回〜第{end_round}回")
    print("※ 試合前順位として、直前toto回終了時点の順位を使用")
    print("※ 順位差 = アウェイ順位 - ホーム順位")
    print("   正の値: ホームの方が上位 / 負の値: アウェイの方が上位")
    print("=" * 80)

    print("\n順位差別")
    for diff in sorted(by_signed_diff.keys(), reverse=True):
        label = f"{diff:+d}"
        print(f"順位差 {label:>4}: ", end="")
        print_counter(by_signed_diff[diff])

    print("\n順位差 絶対値グループ別")
    order = ["0", "1-2", "3-5", "6-9", "10+"]

    for bucket in order:
        if bucket not in by_abs_bucket:
            continue

        print(f"順位差 {bucket:>3}: ", end="")
        print_counter(by_abs_bucket[bucket])

    print("\n未集計")
    print(f"{len(skipped)}試合")

    if skipped:
        for row in skipped[:20]:
            print(row)


def main():
    start_round = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
    end_round = int(sys.argv[2]) if len(sys.argv) >= 3 else 31

    con = connect_db()
    matches = load_matches(con, start_round, end_round)
    standings = load_standings(con)
    con.close()

    by_signed_diff, by_abs_bucket, skipped = analyze(matches, standings)
    print_report(by_signed_diff, by_abs_bucket, skipped, start_round, end_round)


if __name__ == "__main__":
    main()