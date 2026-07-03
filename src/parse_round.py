import sys
import sqlite3
from bs4 import BeautifulSoup

if len(sys.argv) >= 2:
    ROUND_NO = int(sys.argv[1])
else:
    ROUND_NO = 1636

HTML_PATH = f"data/toto_round_{ROUND_NO}.html"
DB_PATH = "data/toto.db"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

target_td = soup.find("td", string=lambda s: s and f"第{ROUND_NO}回 toto" in s)

if target_td is None:
    if "ご指定のくじ結果は表示できません" in html:
        print(f"SKIP: 第{ROUND_NO}回は表示できない開催回です")
        exit(2)

    if "システムでエラーが発生しました" in html:
        print(f"SKIP: 第{ROUND_NO}回はシステムエラーページです")
        exit(2)

    print(f"SKIP: 第{ROUND_NO}回はtoto本体がありません")
    exit(2)

match_table = target_td.find_parent("table").find_next("table", class_="kobetsu-format2")

if match_table is None:
    print(f"SKIP: 第{ROUND_NO}回は試合テーブルが見つかりません")
    exit(2)

rows = match_table.find_all("tr")

matches = []

for row in rows:
    cells = [c.get_text(strip=True) for c in row.find_all("td")]

    if len(cells) != 7:
        continue

    date, stadium, match_no, home_team, score, away_team, result = cells

    if "-" in score:
        home_score, away_score = score.split("-")
        home_score = int(home_score)
        away_score = int(away_score)
    else:
        home_score = None
        away_score = None

    matches.append((
        ROUND_NO,
        int(match_no),
        home_team,
        away_team,
        result,
        home_score,
        away_score,
    ))

if len(matches) == 0:
    print(f"SKIP: 第{ROUND_NO}回はtoto本体の試合データがありません")
    exit(2)

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
INSERT OR REPLACE INTO toto_rounds
(round_no, result_date, sales_amount)
VALUES (?, ?, ?)
""", (ROUND_NO, None, None))

cur.execute("""
DELETE FROM toto_matches
WHERE round_no = ?
""", (ROUND_NO,))

for match in matches:
    cur.execute("""
    INSERT INTO toto_matches
    (round_no, match_no, home_team, away_team, result, home_score, away_score)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, match)

con.commit()
con.close()

print(f"第{ROUND_NO}回の{len(matches)}試合をDBに保存しました")