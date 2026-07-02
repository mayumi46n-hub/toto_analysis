import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS toto_rounds (
    round_no INTEGER PRIMARY KEY,
    result_date TEXT,
    sales_amount INTEGER,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS toto_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_no INTEGER,
    match_no INTEGER,
    home_team TEXT,
    away_team TEXT,
    result TEXT,
    home_score INTEGER,
    away_score INTEGER
)
""")

con.commit()
con.close()

print("toto用の表を作成しました")