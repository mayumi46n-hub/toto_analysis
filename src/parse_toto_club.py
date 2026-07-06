import re
import sys
import sqlite3
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name

HTML = "data/toto_club_2001_utf8.html"
DB_PATH = "data/toto.db"

if len(sys.argv) >= 2:
    ROUND_NO = int(sys.argv[1])
else:
    ROUND_NO = 1

TABLE_INDEX = {
    1: 2,
    2: 1,
}

table_index = TABLE_INDEX[ROUND_NO]


def section_text_to_date(section_text):
    m = re.search(r"(\d{1,2})／(\d{1,2})", section_text)
    if not m:
        return None

    month = int(m.group(1))
    day = int(m.group(2))
    year = 2000

    return f"{year}{month:02d}{day:02d}"


def db_date_to_yyyymmdd(match_date):
    m = re.search(r"(\d{2})/(\d{2})/(\d{2})", match_date)
    if not m:
        return None

    year = 2000 + int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))

    return f"{year}{month:02d}{day:02d}"


with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tables = soup.find_all("table")
target_table = tables[table_index]

section_dates = {}

for tr in target_table.find_all("tr"):
    cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]

    if not cells:
        continue

    section_text = cells[0]

    if section_text.startswith("J1") and "／" in section_text:
        section_dates["J1"] = section_text_to_date(section_text)
        print("開催日候補:", section_text, "→", section_dates["J1"])

    if section_text.startswith("J2") and "／" in section_text:
        section_dates["J2"] = section_text_to_date(section_text)
        print("開催日候補:", section_text, "→", section_dates["J2"])

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print("\nJリーグDB登録状況")

for league, target_date in section_dates.items():
    cur.execute("""
        SELECT match_date
        FROM jleague_matches
    """)

    count = 0

    for (match_date,) in cur.fetchall():
        if db_date_to_yyyymmdd(match_date) == target_date:
            count += 1

    print(f"{league}: {target_date} -> {count}試合")

match_rows = []
matches = []

for tr in target_table.find_all("tr"):
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

print(f"\n第{ROUND_NO}回 試合数: {len(match_rows)}")

matched = 0

for i, (home, away, result) in enumerate(match_rows, start=1):
    cur.execute("""
    SELECT home_score, away_score
    FROM jleague_matches
    WHERE home_team = ?
      AND away_team = ?
    """, (home, away))

    row = cur.fetchone()

    if row:
        matched += 1
        home_score, away_score = row
    else:
        home_score = None
        away_score = None

    matches.append({
        "round_no": ROUND_NO,
        "match_no": i,
        "home_team": home,
        "away_team": away,
        "result": result,
        "home_score": home_score,
        "away_score": away_score,
    })

cur.execute(
    "DELETE FROM toto_matches WHERE round_no = ?",
    (ROUND_NO,)
)

for match in matches:
    cur.execute("""
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

con.commit()
con.close()

print(f"\nDBへ {len(matches)} 試合保存しました")
print(f"照合成功: {matched} / {len(match_rows)}")

print("\n作成したデータ")
for match in matches:
    print(match)