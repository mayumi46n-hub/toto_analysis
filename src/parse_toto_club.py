import re
import sys
import sqlite3
from round_config import get_round_config
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name

DB_PATH = "data/toto.db"

if len(sys.argv) >= 2:
    ROUND_NO = int(sys.argv[1])
else:
    ROUND_NO = 1

config = get_round_config(ROUND_NO)

HTML = config["html"]
table_index = config["table"]


def section_text_to_dates(section_text):
    year = 2001 if ROUND_NO >= 3 else 2000

    dates = []

    # 例: 3/10, 11／8
    slash_matches = re.findall(r"(\d{1,2})[／/](\d{1,2})", section_text)
    for month_text, day_text in slash_matches:
        month = int(month_text)
        day = int(day_text)
        dates.append(f"{year}{month:02d}{day:02d}")

    # 例: 04月14日
    japanese_matches = re.findall(r"(\d{1,2})月(\d{1,2})日", section_text)
    for month_text, day_text in japanese_matches:
        month = int(month_text)
        day = int(day_text)
        date_text = f"{year}{month:02d}{day:02d}"
        if date_text not in dates:
            dates.append(date_text)

    return dates


def yyyymmdd_to_db_like(date_text):
    year = date_text[2:4]
    month = date_text[4:6]
    day = date_text[6:8]
    return f"{year}/{month}/{day}%"


def db_date_to_yyyymmdd(match_date):
    m = re.search(r"(\d{2})/(\d{2})/(\d{2})", match_date)
    if not m:
        return None

    year = 2000 + int(m.group(1))
    month = int(m.group(2))
    day = int(m.group(3))

    return f"{year}{month:02d}{day:02d}"


def competition_condition(league):
    if league == "J1":
        return "competition LIKE 'Ｊ１%'"
    if league == "J2":
        return "competition = 'Ｊ２'"
    return "1 = 1"


with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tables = soup.find_all("table")
target_table = tables[table_index]

section_dates = {}
match_rows = []

current_league = None
current_dates = []

for tr in target_table.find_all("tr"):
    cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]

    if not cells:
        continue

    section_text = cells[0]

    if section_text.startswith("J1") and ("／" in section_text or "/" in section_text or "月" in section_text):
        current_league = "J1"
        current_dates = section_text_to_dates(section_text)
        section_dates["J1"] = current_dates
        print("開催日候補:", section_text, "→", ",".join(current_dates))

    elif section_text.startswith("J2") and ("／" in section_text or "/" in section_text or "月" in section_text):
        current_league = "J2"
        current_dates = section_text_to_dates(section_text)
        section_dates["J2"] = current_dates
        print("開催日候補:", section_text, "→", ",".join(current_dates))

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
        result,
        current_league,
        list(current_dates),
    ))

if "J1" in section_dates and "J2" not in section_dates and len(match_rows) > 8:
    section_dates["J2"] = section_dates["J1"]

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print("\nJリーグDB登録状況")

for league, dates in section_dates.items():
    total = 0

    for date_text in dates:
        cur.execute(f"""
            SELECT COUNT(*)
            FROM jleague_matches
            WHERE {competition_condition(league)}
              AND match_date LIKE ?
        """, (yyyymmdd_to_db_like(date_text),))

        total += cur.fetchone()[0]

    print(f"{league}: {','.join(dates)} -> {total}試合")

print(f"\n第{ROUND_NO}回 試合数: {len(match_rows)}")

matches = []
matched = 0

for i, (home, away, result, league, target_dates) in enumerate(match_rows, start=1):
    if not target_dates:
        target_dates = []
        for dates in section_dates.values():
            target_dates.extend(dates)

    date_conditions = " OR ".join(["match_date LIKE ?"] * len(target_dates))

    params = [home, away]
    params.extend(yyyymmdd_to_db_like(date_text) for date_text in target_dates)

    if date_conditions:
        sql = f"""
        SELECT home_score, away_score
        FROM jleague_matches
        WHERE home_team = ?
          AND away_team = ?
          AND ({date_conditions})
        """
        cur.execute(sql, params)
        row = cur.fetchone()
    else:
        row = None

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