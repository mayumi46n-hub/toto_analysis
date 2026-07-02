import csv
import sqlite3

DB_PATH = "data/toto.db"
CSV_PATH = "data/stadium_master.csv"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute("""
        INSERT INTO stadium_master
        (stadium_name, capacity, prefecture, roof_type)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(stadium_name) DO UPDATE SET
            capacity=excluded.capacity,
            prefecture=excluded.prefecture,
            roof_type=excluded.roof_type
        """, (
            row["stadium_name"],
            int(row["capacity"]) if row["capacity"] else None,
            row["prefecture"],
            row["roof_type"],
        ))

con.commit()
con.close()

print("stadium_master.csv をDBに反映しました！")