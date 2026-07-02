import sys
import sqlite3

DB_PATH = "data/toto.db"

if len(sys.argv) >= 2:
    round_no = int(sys.argv[1])
else:
    print("使い方: python3 src/delete_round.py 1600")
    exit()

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

cur.execute(
    "DELETE FROM toto_matches WHERE round_no = ?",
    (round_no,)
)

deleted_matches = cur.rowcount

cur.execute(
    "DELETE FROM toto_rounds WHERE round_no = ?",
    (round_no,)
)

con.commit()
con.close()

print(f"第{round_no}回を削除しました")
print(f"削除した試合数: {deleted_matches}")