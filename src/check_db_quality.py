import sqlite3
import sys

DB_PATH = "data/toto.db"
START_ROUND = 1
END_ROUND = 31
EXPECTED_MATCHES_PER_ROUND = 13
EXPECTED_TOTAL = (END_ROUND - START_ROUND + 1) * EXPECTED_MATCHES_PER_ROUND


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print("DB品質チェック")
    print(f"対象: 第{START_ROUND}回〜第{END_ROUND}回")
    print()

    cur.execute("""
        SELECT COUNT(*)
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
    """, (START_ROUND, END_ROUND))
    total = cur.fetchone()[0]

    print(f"総試合数: {total} / 期待値 {EXPECTED_TOTAL}")

    cur.execute("""
        SELECT COUNT(*)
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
    """, (START_ROUND, END_ROUND))
    matched = cur.fetchone()[0]

    print(f"照合済み: {matched} / {total}")

    print("\n各回の試合数")
    cur.execute("""
        SELECT round_no, COUNT(*) AS cnt
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
        GROUP BY round_no
        ORDER BY round_no
    """, (START_ROUND, END_ROUND))

    bad_rounds = []
    for round_no, cnt in cur.fetchall():
        status = "OK" if cnt == EXPECTED_MATCHES_PER_ROUND else "NG"
        print(f"第{round_no}回: {cnt}試合 {status}")
        if cnt != EXPECTED_MATCHES_PER_ROUND:
            bad_rounds.append(round_no)

    print("\n未照合試合")
    cur.execute("""
        SELECT round_no, match_no, home_team, away_team
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
          AND (home_score IS NULL OR away_score IS NULL)
        ORDER BY round_no, match_no
    """, (START_ROUND, END_ROUND))

    unmatched = cur.fetchall()
    if unmatched:
        for row in unmatched:
            print(row)
    else:
        print("なし")

    print("\n重複チェック")
    cur.execute("""
        SELECT round_no, match_no, COUNT(*) AS cnt
        FROM toto_matches
        WHERE round_no BETWEEN ? AND ?
        GROUP BY round_no, match_no
        HAVING COUNT(*) > 1
        ORDER BY round_no, match_no
    """, (START_ROUND, END_ROUND))

    duplicates = cur.fetchall()
    if duplicates:
        for row in duplicates:
            print(row)
    else:
        print("なし")

    con.close()

    print("\n判定")
    if total == EXPECTED_TOTAL and matched == EXPECTED_TOTAL and not bad_rounds and not unmatched and not duplicates:
        print("OK: 2001年データ品質チェック合格")
        sys.exit(0)

    print("NG: 要確認")
    sys.exit(1)


if __name__ == "__main__":
    main()