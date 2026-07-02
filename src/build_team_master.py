import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

teams = set()

for row in cur.execute("""
SELECT home_team
FROM toto_matches
"""):
    teams.add(row[0])

for row in cur.execute("""
SELECT away_team
FROM toto_matches
"""):
    teams.add(row[0])

for team in sorted(teams):

    cur.execute("""
    INSERT OR IGNORE INTO team_master
    (short_name)
    VALUES (?)
    """, (team,))

con.commit()

print(f"{len(teams)}チーム登録しました")

con.close()