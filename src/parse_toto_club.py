import re
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name

HTML = "data/toto_club_2001_utf8.html"

with open(HTML, encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

tables = soup.find_all("table")

match_rows = []

for tr in tables[2].find_all("tr"):
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

print(f"第1回 試合数: {len(match_rows)}")

for i, (home, away, result) in enumerate(match_rows, start=1):
    print(i, home, away, result)