import sqlite3

DB_PATH = "data/toto.db"
ROUND_NO = 1636

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print(f"========== 第{ROUND_NO}回 結果集計 ==========")

cur.execute("""
SELECT result, COUNT(*)
FROM toto_matches
WHERE round_no = ?
GROUP BY result
ORDER BY result
""", (ROUND_NO,))

for result, count in cur.fetchall():
    if result == "1":
        label = "ホーム勝ち"
    elif result == "0":
        label = "引き分け"
    elif result == "2":
        label = "アウェイ勝ち"
    else:
        label = "不明"

    print(f"{label}: {count}試合")

con.close()