import sys
import sqlite3
from pathlib import Path
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name

DB_PATH = "data/toto.db"

if len(sys.argv) >= 2:
    DATE = sys.argv[1]
else:
    DATE = "20001108"


def html_files_for_date(date):
    split_files = [
        f"data/jleague_{date}_j1.html",
        f"data/jleague_{date}_j2.html",
    ]

    existing_split_files = [path for path in split_files if Path(path).exists()]

    if existing_split_files:
        return existing_split_files

    legacy_file = f"data/jleague_{date}.html"

    if Path(legacy_file).exists():
        return [legacy_file]

    return []


def parse_html(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    tables = soup.find_all("table")

    if not tables:
        print(f"警告: tableが見つかりません: {html_path}")
        return []

    table = tables[0]
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

    return matches


html_files = html_files_for_date(DATE)

if not html_files:
    raise FileNotFoundError(f"JリーグHTMLが見つかりません: data/jleague_{DATE}*.html")

all_matches = []

for html_file in html_files:
    matches = parse_html(html_file)
    print(f"{html_file}: {len(matches)}試合")
    all_matches.extend(matches)

print(f"見つけた試合数: {len(all_matches)}")

for m in all_matches:
    print(m)

if not all_matches:
    print("保存する試合がありません")
    sys.exit()

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

delete_keys = sorted(set((match[0], match[3], match[1]) for match in all_matches))

for season, match_date, competition in delete_keys:
    cur.execute("""
    DELETE FROM jleague_matches
    WHERE season = ?
      AND match_date = ?
      AND competition = ?
    """, (season, match_date, competition))

for match in all_matches:
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

print(f"Jリーグ公式データ {len(all_matches)}試合をDBに保存しました")