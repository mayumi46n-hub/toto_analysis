import sqlite3
from pathlib import Path

DB_PATH = Path("data/db/footystats.db")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ------------------------
# matches テーブル
# ------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS matches (

    id INTEGER PRIMARY KEY,

    page_title TEXT,

    league TEXT,

    season INTEGER,

    source_file TEXT,

    json_file TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
""")

# ------------------------
# match_tables テーブル
# ------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS match_tables (

    id INTEGER PRIMARY KEY,

    match_id INTEGER,

    table_index INTEGER,

    section_title TEXT,

    table_title TEXT,

    FOREIGN KEY(match_id) REFERENCES matches(id)

);
""")

# ------------------------
# match_metrics テーブル
# ------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS match_metrics (

    id INTEGER PRIMARY KEY,

    table_id INTEGER,

    metric_name TEXT,

    col1 TEXT,

    col2 TEXT,

    col3 TEXT,

    FOREIGN KEY(table_id) REFERENCES match_tables(id)

);
""")

conn.commit()
conn.close()

print("Database created.")