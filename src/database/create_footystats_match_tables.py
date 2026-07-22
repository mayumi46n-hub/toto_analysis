import sqlite3

DB = "data/toto.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# -----------------------------
# Match Page
# -----------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS footystats_match_pages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    page_title TEXT,
    league TEXT,
    season INTEGER,

    source_file TEXT,
    json_file TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

# -----------------------------
# Tables
# -----------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS footystats_match_tables (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    page_id INTEGER,

    table_index INTEGER,

    section_title TEXT,
    table_title TEXT,

    FOREIGN KEY(page_id)
        REFERENCES footystats_match_pages(id)

)
""")

# -----------------------------
# Metrics
# -----------------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS footystats_match_metrics (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    table_id INTEGER,

    metric_name TEXT,

    value1 TEXT,
    value2 TEXT,
    value3 TEXT,

    FOREIGN KEY(table_id)
        REFERENCES footystats_match_tables(id)

)
""")

conn.commit()
conn.close()

print("FootyStats tables created.")
