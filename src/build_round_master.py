import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup

OUT = "data/round_master.csv"

YEAR = 2001

J1_1ST_COMPETITION_ID = 129
J1_2ND_COMPETITION_ID = 130
J2_COMPETITION_ID = 132

J1_1ST_SECTION_BASE = 1120
J1_2ND_SECTION_BASE = 1135
J2_SECTION_BASE = 1152


def section_text_to_dates(text):
    dates = []

    for month, day in re.findall(r"(\d{1,2})[／/](\d{1,2})", text):
        dates.append(f"{YEAR}{int(month):02d}{int(day):02d}")

    for month, day in re.findall(r"(\d{1,2})月(\d{1,2})日", text):
        dates.append(f"{YEAR}{int(month):02d}{int(day):02d}")

    return list(dict.fromkeys(dates))


def extract_section_number(text):
    m = re.search(r"第\s*(\d{1,2})\s*節", text)
    if not m:
        return None
    return int(m.group(1))


def extract_round_info(html_path, table_index):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    tables = soup.find_all("table")

    if table_index >= len(tables):
        return None

    table = tables[table_index]

    info = {
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

        elif text.startswith("J2") and "第" in text and "節" in text:
            info["j2_section"] = extract_section_number(text)
            info["j2_dates"] = section_text_to_dates(text)

    if info["j1_section"] is not None and info["j2_section"] is None:
        info["j2_section"] = info["j1_section"]

    if info["j1_dates"] and not info["j2_dates"]:
        info["j2_dates"] = info["j1_dates"]

    return info


def j1_competition_and_section(round_no, j1_section):
    if round_no <= 17:
        return J1_1ST_COMPETITION_ID, J1_1ST_SECTION_BASE + j1_section

    return J1_2ND_COMPETITION_ID, J1_2ND_SECTION_BASE + j1_section


def build_rows():
    rows = []

    for html_path in sorted(Path("data").glob("toto_club_2001_yosou*_utf8.html")):
        m = re.search(r"yosou(\d+)_utf8", html_path.name)
        if not m:
            continue

        yosou_no = int(m.group(1))

        odd_round = yosou_no * 2 + 1
        even_round = yosou_no * 2 + 2

        if yosou_no == 15:
            targets = [
                (31, 1, 1),
            ]
        else:
            targets = [
                (odd_round, 1, 2),
                (even_round, 2, 1),
            ]

        for round_no, anchor, table_index in targets:
            info = extract_round_info(html_path, table_index)

            if info is None:
                print(f"skip: 第{round_no}回 tableなし")
                continue

            dates = info["j1_dates"] or info["j2_dates"]

            if not dates:
                print(f"skip: 第{round_no}回 日付なし")
                continue

            if info["j1_section"] is None or info["j2_section"] is None:
                print(f"skip: 第{round_no}回 J1/J2節なし")
                continue

            j1_competition_id, j1_section_id = j1_competition_and_section(
                round_no,
                info["j1_section"],
            )

            rows.append({
                "round_no": round_no,
                "year": YEAR,
                "yosou_no": yosou_no,
                "anchor": anchor,
                "date_key": dates[0],
                "date1": dates[0],
                "date2": dates[1] if len(dates) >= 2 else "",
                "j1_competition_id": j1_competition_id,
                "j1_section_id": j1_section_id,
                "j2_competition_id": J2_COMPETITION_ID,
                "j2_section_id": J2_SECTION_BASE + info["j2_section"],
            })

    rows.sort(key=lambda r: r["round_no"])
    return rows


rows = build_rows()

with open(OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "round_no",
            "year",
            "yosou_no",
            "anchor",
            "date_key",
            "date1",
            "date2",
            "j1_competition_id",
            "j1_section_id",
            "j2_competition_id",
            "j2_section_id",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"{OUT} を作成しました")
print(f"{len(rows)}件")

for row in rows:
    print(row)