import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS team_alias (
    alias_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias_name TEXT UNIQUE,
    team_id INTEGER
)
""")

con.commit()
con.close()

print("team_alias テーブルを作成しました！")