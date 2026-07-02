import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stadium_master (

    stadium_id INTEGER PRIMARY KEY AUTOINCREMENT,

    stadium_name TEXT UNIQUE,

    capacity INTEGER,

    prefecture TEXT,

    roof_type TEXT,

    latitude REAL,

    longitude REAL

)
""")

con.commit()
con.close()

print("stadium_master テーブルを作成しました！")