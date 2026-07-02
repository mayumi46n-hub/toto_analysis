import sqlite3

DB_PATH = "data/toto.db"
ROUND_NO = 1636

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print(f"========== 第{ROUND_NO}回 toto試合情報 ==========")

for row in cur.execute("""
SELECT round_no, match_no, home_team, away_team, result, home_score, away_score
FROM toto_matches
WHERE round_no = ?
ORDER BY match_no
""", (ROUND_NO,)):

    round_no, match_no, home_team, away_team, result, home_score, away_score = row

    if result == "1":
        result_text = "ホーム勝ち"
    elif result == "0":
        result_text = "引き分け"
    elif result == "2":
        result_text = "アウェイ勝ち"
    else:
        result_text = "不明"

    print(f"{match_no}試合目: {home_team} vs {away_team} / 結果: {result}（{result_text}） / スコア: {home_score}-{away_score}")

con.close()