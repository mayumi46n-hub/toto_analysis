import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

# team_masterを全部取得
teams = cur.execute("""
SELECT team_id, stadium
FROM team_master
WHERE stadium IS NOT NULL
""").fetchall()

count = 0

for team_id, stadium_name in teams:

    row = cur.execute("""
    SELECT stadium_id
    FROM stadium_master
    WHERE stadium_name = ?
    """, (stadium_name,)).fetchone()

    if row is None:
        continue

    stadium_id = row[0]

    cur.execute("""
    UPDATE team_master
    SET stadium_id = ?
    WHERE team_id = ?
    """, (stadium_id, team_id))

    count += 1

con.commit()
con.close()

print(f"{count}チームをスタジアムへリンクしました！")