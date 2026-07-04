import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS jleague_matches (
    jleague_match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season INTEGER,
    competition TEXT,
    match_date TEXT,
    kickoff_time TEXT,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    stadium TEXT,
    attendance INTEGER
)
""")

con.commit()
con.close()

print("jleague_matches テーブルを作成しました！")