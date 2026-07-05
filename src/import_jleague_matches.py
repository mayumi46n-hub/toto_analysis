import sys
import sqlite3
from normalize_team import normalize_team_name
from bs4 import BeautifulSoup

if len(sys.argv) >= 2:
    DATE = sys.argv[1]
else:
    DATE = "20001108"

HTML = f"data/jleague_{DATE}.html"
DB_PATH = "data/toto.db"

with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

table = soup.find_all("table")[0]
rows = table.find_all("tr")

matches = []

for row in rows[1:]:
    cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]

    if len(cells) < 10:
        continue

    season = int(cells[0])
    competition = cells[1]
    section = cells[2]
    match_date = cells[3]
    kickoff_time = cells[4]
    home_team = normalize_team_name(cells[5])
    score = cells[6]
    away_team = normalize_team_name(cells[7])
    stadium = cells[8]
    attendance = int(cells[9].replace(",", "")) if cells[9] else None

    if "-" not in score:
        continue

    home_score, away_score = score.split("-")
    home_score = int(home_score)
    away_score = int(away_score)

    matches.append((
        season,
        competition,
        section,
        match_date,
        kickoff_time,
        home_team,
        away_team,
        home_score,
        away_score,
        stadium,
        attendance,
        None,
    ))

print(f"見つけた試合数: {len(matches)}")

for m in matches:

    print(m)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
DELETE FROM jleague_matches
WHERE season = ?
  AND match_date = ?
""", (2000, "00/11/08(水)"))

for match in matches:
    cur.execute("""
    INSERT INTO jleague_matches
    (
        season,
        competition,
        section,
        match_date,
        kickoff_time,
        home_team,
        away_team,
        home_score,
        away_score,
        stadium,
        attendance,
        match_url
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, match)

con.commit()
con.close()

print(f"Jリーグ公式データ {len(matches)}試合をDBに保存しました")