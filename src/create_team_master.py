import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS team_master (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_name TEXT UNIQUE,
    full_name TEXT,
    league TEXT,
    stadium TEXT,
    capacity INTEGER,
    prefecture TEXT,
    category TEXT
)
""")

# 既存テーブルに列を追加。すでにあれば無視する。
columns = [
    ("capacity", "INTEGER"),
    ("prefecture", "TEXT"),
    ("category", "TEXT"),
]

for col_name, col_type in columns:
    try:
        cur.execute(f"ALTER TABLE team_master ADD COLUMN {col_name} {col_type}")
    except sqlite3.OperationalError:
        pass

con.commit()
con.close()

print("team_master テーブルを作成・拡張しました！")