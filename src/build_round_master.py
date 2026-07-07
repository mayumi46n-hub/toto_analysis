import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup

OUT = "data/round_master.csv"


def section_text_to_dates(text):
    dates = []

    for month, day in re.findall(r"(\d{1,2})[／/](\d{1,2})", text):
        dates.append(f"2001{int(month):02d}{int(day):02d}")

    for month, day in re.findall(r"(\d{1,2})月(\d{1,2})日", text):
        dates.append(f"2001{int(month):02d}{int(day):02d}")

    return list(dict.fromkeys(dates))


def extract_section_number(text):
    m = re.search(r"第\s*(\d{1,2})\s*節", text)
    if not m:
        return None
    return int(m.group(1))


def extract_round_info(html_path, round_no, table_index):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find_all("table")[table_index]

    info = {
        "round_no": round_no,
        "j1_section": None,
        "j2_section": None,
        "j1_dates": [],
        "j2_dates": [],
    }

    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if not cells:
            continue

        text = cells[0]

        if text.startswith("J1") and "第" in text and "節" in text:
            info["j1_section"] = extract_section_number(text)
            info["j1_dates"] = section_text_to_dates(text)

        if text.startswith("J2") and "第" in text and "節" in text:
            info["j2_section"] = extract_section_number(text)
            info["j2_dates"] = section_text_to_dates(text)

    return info


rows = []

for html_path in sorted(Path("data").glob("toto_club_2001_yosou*_utf8.html")):
    m = re.search(r"yosou(\d+)_utf8", html_path.name)
    if not m:
        continue

    yosou_no = int(m.group(1))

    # yosou1 -> 第3回/第4回, yosou2 -> 第5回/第6回 ...
    odd_round = yosou_no * 2 + 1
    even_round = yosou_no * 2 + 2

    targets = [
        (odd_round, 1, 2),   # anchor #1, table 2
        (even_round, 2, 1),  # anchor #2, table 1
    ]

    for round_no, anchor, table_index in targets:
        info = extract_round_info(html_path, round_no, table_index)

        dates = info["j1_dates"] or info["j2_dates"]
        if not dates:
            print(f"skip: 第{round_no}回 日付なし")
            continue

        if info["j1_section"] is None or info["j2_section"] is None:
            print(f"skip: 第{round_no}回 J1/J2節なし")
            continue

        date_key = dates[0]
        date1 = dates[0]
        date2 = dates[1] if len(dates) >= 2 else ""

        j1_section_id = 1120 + info["j1_section"]
        j2_section_id = 1152 + info["j2_section"]

        rows.append({
            "round_no": round_no,
            "yosou_no": yosou_no,
            "anchor": anchor,
            "date_key": date_key,
            "date1": date1,
            "date2": date2,
            "j1_section_id": j1_section_id,
            "j2_section_id": j2_section_id,
        })

rows.sort(key=lambda r: r["round_no"])

with open(OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "round_no",
            "yosou_no",
            "anchor",
            "date_key",
            "date1",
            "date2",
            "j1_section_id",
            "j2_section_id",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"{OUT} を作成しました")
print(f"{len(rows)}件")
for row in rows:
    print(row)