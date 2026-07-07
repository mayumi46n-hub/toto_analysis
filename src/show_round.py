import csv
import sys

MASTER_PATH = "data/round_master.csv"

if len(sys.argv) < 2:
    print("使い方: python3 src/show_round.py ROUND_NO")
    print("例: python3 src/show_round.py 13")
    sys.exit(1)

round_no = sys.argv[1]

with open(MASTER_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

target = None

for row in rows:
    if row["round_no"] == round_no:
        target = row
        break

if target is None:
    print(f"第{round_no}回は round_master.csv にありません")
    sys.exit(1)

year = 2001
yosou_no = target["yosou_no"]
anchor = target["anchor"]
j1_section_id = target["j1_section_id"]
j2_section_id = target["j2_section_id"]

toto_url = f"https://www.toto-club.net/yosou/{year}/yosou{yosou_no}.htm#{anchor}"

j1_url = (
    f"https://data.j-league.or.jp/SFMS01/search?"
    f"competition_years={year}&"
    f"competition_frame_ids=1&"
    f"competition_ids=129&"
    f"competition_section_ids={j1_section_id}&"
    f"tv_relay_station_name="
)

j2_url = (
    f"https://data.j-league.or.jp/SFMS01/search?"
    f"competition_years={year}&"
    f"competition_frame_ids=2&"
    f"competition_ids=132&"
    f"competition_section_ids={j2_section_id}&"
    f"tv_relay_station_name="
)

print(f"第{round_no}回")
print(f"date_key: {target['date_key']}")
print()
print("toto Club")
print(toto_url)
print()
print("J1")
print(j1_url)
print()
print("J2")
print(j2_url)