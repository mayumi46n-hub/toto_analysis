import sys
import sqlite3
from round_config import get_round_config
from toto_parser import (
    extract_toto_rows,
    competition_condition,
    yyyymmdd_to_db_like,
)

DB_PATH = "data/toto.db"

if len(sys.argv) >= 2:
    ROUND_NO = int(sys.argv[1])
else:
    ROUND_NO = 1

config = get_round_config(ROUND_NO)

HTML = config["html"]
table_index = config["table"]

section_dates, match_rows = extract_toto_rows(
    HTML,
    table_index,
    ROUND_NO,
)

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