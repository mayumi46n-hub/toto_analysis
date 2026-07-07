import sys
import subprocess
import sqlite3
from pathlib import Path

DB_PATH = "data/toto.db"

if len(sys.argv) < 3:
    print("使い方: python3 src/process_round.py ROUND_NO YYYYMMDD")
    print("例: python3 src/process_round.py 13 20010526")
    sys.exit(1)

round_no = int(sys.argv[1])
date = sys.argv[2]


def run(command):
    print("\n実行:", " ".join(command))
    result = subprocess.run(command)

    if result.returncode != 0:
        print("エラーで停止しました")
        sys.exit(result.returncode)


def convert_toto_html_if_needed(round_no):
    if round_no <= 2:
        base_name = "toto_club_2001"
    else:
        yosou_no = (round_no - 1) // 2
        base_name = f"toto_club_2001_yosou{yosou_no}"

    src = Path(f"data/{base_name}.html")
    dst = Path(f"data/{base_name}_utf8.html")

    if not src.exists():
        print(f"\n警告: 元HTMLがありません: {src}")
        return

    print(f"\nUTF-8変換: {src} -> {dst}")

    with open(dst, "w", encoding="utf-8") as out:
        result = subprocess.run(
            ["iconv", "-f", "SHIFT_JIS", "-t", "UTF-8", str(src)],
            stdout=out,
        )

    if result.returncode != 0:
        print("UTF-8変換に失敗しました")
        sys.exit(result.returncode)


convert_toto_html_if_needed(round_no)

run(["python3", "src/import_jleague_matches.py", date])
run(["python3", "src/parse_toto_club.py", str(round_no)])

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute("""
SELECT
    COUNT(*),
    SUM(CASE WHEN home_score IS NOT NULL AND away_score IS NOT NULL THEN 1 ELSE 0 END)
FROM toto_matches
WHERE round_no = ?
""", (round_no,))

total, matched = cur.fetchone()
con.close()

print("\n確認結果")
print(f"第{round_no}回: {matched} / {total}")

if total == 13 and matched == 13:
    print("OK: 13/13 照合完了")
else:
    print("注意: 未照合があります")