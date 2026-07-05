import sys
import re
import sqlite3
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name

HTML = "data/toto_club_2001_utf8.html"
DB_PATH = "data/toto.db"
if len(sys.argv) >= 2:
    ROUND_NO = int(sys.argv[1])
else:
    ROUND_NO = 1

with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tables = soup.find_all("table")

match_rows = []
matches = []

TABLE_INDEX = {
    1: 2,
    2: 1,
}

table_index = TABLE_INDEX[ROUND_NO]

for tr in tables[table_index].find_all("tr"):
    cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]

    if len(cells) >= 9 and cells[3] == "勝":
        home_team = cells[1]
        away_team = cells[2]
        result_text = cells[-1]
    elif len(cells) >= 8 and cells[2] == "勝":
        home_team = cells[0]
        away_team = cells[1]
        result_text = cells[-1]
    else:
        continue

    m = re.search(r"\[(\d)\]", result_text)
    if not m:
        continue

    result = m.group(1)

    match_rows.append((
        normalize_team_name(home_team),
        normalize_team_name(away_team),
        result
    ))

print(f"第{ROUND_NO}回 試合数: {len(match_rows)}")

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

matched = 0

for i, (home, away, result) in enumerate(match_rows, start=1):
    cur.execute("""
    SELECT home_score, away_score, stadium, attendance
    FROM jleague_matches
    WHERE home_team = ?
      AND away_team = ?
    """, (home, away))

    row = cur.fetchone()

    if row:
        matched += 1
        home_score, away_score, stadium, attendance = row
    else:
        home_score = None
        away_score = None
        stadium = None
        attendance = None

    matches.append({
        "round_no": ROUND_NO,
        "match_no": i,
        "home_team": home,
        "away_team": away,
        "result": result,
        "home_score": home_score,
        "away_score": away_score,
        "stadium": stadium,
        "attendance": attendance,
    })

save_con = sqlite3.connect(DB_PATH)
save_cur = save_con.cursor()

# 第1回を入れ直せるように一旦削除
save_cur.execute(
    "DELETE FROM toto_matches WHERE round_no = ?",
    (ROUND_NO,)
)

for match in matches:

    save_cur.execute("""
    INSERT INTO toto_matches
    (
        round_no,
        match_no,
        home_team,
        away_team,
        result,
        home_score,
        away_score
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        match["round_no"],
        match["match_no"],
        match["home_team"],
        match["away_team"],
        match["result"],
        match["home_score"],
        match["away_score"],
    ))

save_con.commit()
save_con.close()

print(f"\nDBへ {len(matches)} 試合保存しました")
con.close()

print(f"照合成功: {matched} / {len(match_rows)}")

print("\n作成したデータ")
for match in matches:
    print(match)