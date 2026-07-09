import csv
import sys
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

MASTER_PATH = "data/round_master.csv"


def load_round(round_no):
    with open(MASTER_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["round_no"] == str(round_no):
                return row
    return None


def build_jleague_url(year, frame_id, competition_id, section_id):
    return (
        "https://data.j-league.or.jp/SFMS01/search?"
        f"competition_years={year}&"
        f"competition_frame_ids={frame_id}&"
        f"competition_ids={competition_id}&"
        f"competition_section_ids={section_id}&"
        "tv_relay_station_name="
    )


def download(url, output_path):
    print("download:", url)
    print("save to :", output_path)

    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    context = ssl._create_unverified_context()

    with urlopen(req, context=context) as response:
        body = response.read()

    output_path.write_bytes(body)


if len(sys.argv) < 2:
    print("使い方: python3 src/fetch_jleague_html.py ROUND_NO")
    print("例: python3 src/fetch_jleague_html.py 18")
    sys.exit(1)

round_no = int(sys.argv[1])
row = load_round(round_no)

if row is None:
    print(f"第{round_no}回は round_master.csv にありません")
    sys.exit(1)

year = row.get("year", "2001")
date_key = row["date_key"]

j1_url = build_jleague_url(
    year,
    1,
    row["j1_competition_id"],
    row["j1_section_id"],
)

j2_url = build_jleague_url(
    year,
    2,
    row["j2_competition_id"],
    row["j2_section_id"],
)

j1_path = Path(f"data/jleague_{date_key}_j1.html")
j2_path = Path(f"data/jleague_{date_key}_j2.html")

download(j1_url, j1_path)
download(j2_url, j2_path)

print("JリーグHTML取得完了")