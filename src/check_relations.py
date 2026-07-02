import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print("========== チーム・スタジアム連携 ==========")

for row in cur.execute("""
SELECT
    t.short_name,
    t.full_name,
    s.stadium_name,
    s.capacity,
    s.prefecture
FROM team_master t
JOIN stadium_master s
    ON t.stadium_id = s.stadium_id
ORDER BY t.short_name
"""):
    short_name, full_name, stadium_name, capacity, prefecture = row
    print(f"{short_name}: {full_name} / {stadium_name} / {capacity}人 / {prefecture}")

con.close()