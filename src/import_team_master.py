import csv
import sqlite3

DB_PATH = "data/toto.db"
CSV_PATH = "data/team_master.csv"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute("""
        INSERT INTO team_master
        (short_name, full_name, league, stadium, capacity, prefecture, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(short_name) DO UPDATE SET
            full_name=excluded.full_name,
            league=excluded.league,
            stadium=excluded.stadium,
            capacity=excluded.capacity,
            prefecture=excluded.prefecture,
            category=excluded.category
        """, (
            row["short_name"],
            row["full_name"],
            row["league"],
            row["stadium"],
            int(row["capacity"]) if row["capacity"] else None,
            row["prefecture"],
            row["category"],
        ))

con.commit()
con.close()

print("team_master.csv をDBに反映しました！")