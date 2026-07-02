import sqlite3

DB_PATH = "data/toto.db"

round_no = 1600

matches = [
    (1, "鹿島", "浦和", "1", 2, 1),
    (2, "横浜FM", "川崎F", "0", 1, 1),
    (3, "神戸", "FC東京", "1", 3, 1),
    (4, "広島", "G大阪", "2", 0, 1),
    (5, "C大阪", "名古屋", "1", 2, 0),
    (6, "柏", "札幌", "1", 1, 0),
    (7, "新潟", "磐田", "0", 2, 2),
    (8, "京都", "湘南", "2", 0, 2),
    (9, "町田", "東京V", "1", 2, 1),
    (10, "福岡", "鳥栖", "0", 0, 0),
    (11, "仙台", "清水", "2", 1, 3),
    (12, "千葉", "大分", "1", 2, 1),
    (13, "長崎", "熊本", "0", 1, 1),
]

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
INSERT OR REPLACE INTO toto_rounds
(round_no, result_date, sales_amount)
VALUES (?, ?, ?)
""", (round_no, "2026-07-02", None))

# 同じ開催回の古い試合データを一度消す
cur.execute("""
DELETE FROM toto_matches
WHERE round_no = ?
""", (round_no,))

for match in matches:
    match_no, home_team, away_team, result, home_score, away_score = match

    cur.execute("""
    INSERT INTO toto_matches
    (round_no, match_no, home_team, away_team, result, home_score, away_score)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        round_no,
        match_no,
        home_team,
        away_team,
        result,
        home_score,
        away_score,
    ))

con.commit()
con.close()

print("13試合のサンプルデータを書き込みました")