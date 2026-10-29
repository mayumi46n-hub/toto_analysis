import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

JST = timezone(timedelta(hours=9))
BASE = "https://store.toto-dream.com/dcs/subos/screen/pi01/spin000/PGSPIN00001DisptotoLotInfo.form"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    args = ap.parse_args()
    rnd = args.round
    response = requests.get(BASE, params={"holdCntId": rnd}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text(" ", strip=True)
    print(f"第{rnd}回：公式ページ取得OK")
    def get_date(label):
        m = re.search(label + r"\s*(\d{4})年(\d{1,2})月(\d{1,2})日", text)
        if not m:
            raise ValueError("日付取得失敗: " + label)
        return f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}"
    start_date = get_date("販売開始日")
    end_date = get_date("販売終了日")
    result_date = get_date("結果発表日")
    start_part = text.split("販売開始日", 1)[1].split("販売終了日", 1)[0]
    end_part = text.split("販売終了日", 1)[1].split("結果発表日", 1)[0]
    st = re.search(r"(\d{1,2})[：:](\d{2})", start_part)
    nt = re.search(r"ネット決済\)\s*(\d{1,2})[：:](\d{2})", end_part)
    if not st or not nt:
        raise ValueError("販売時刻の取得に失敗しました")
    sales_start = start_date + " " + st[1].zfill(2) + ":" + st[2]
    net_deadline = end_date + " " + nt[1].zfill(2) + ":" + nt[2]
    print("販売開始:", sales_start)
    print("ネット決済締切:", net_deadline)
    print("結果発表日:", result_date)
    matches = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
            if len(cells) in (7, 8) and cells[0].isdigit():
                rows.append(cells)
        if len(rows) == 13 and [int(r[0]) for r in rows] == list(range(1, 14)):
            matches = rows
            break
    if len(matches) != 13:
        raise ValueError("toto対象13試合を特定できません")
    print("対象試合:", len(matches))
    print("第1試合:", matches[0][4], "vs", matches[0][6])
    print("第13試合:", matches[-1][4], "vs", matches[-1][6])
    records = []
    for r in matches:
        records.append({
            "round": rnd, "match_no": int(r[0]),
            "match_month_day": r[1], "kickoff_time": r[2],
            "stadium": r[3], "home_team": r[4], "away_team": r[6]
        })
    out = Path("data/analysis")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"toto{rnd}_official_matches_v01.csv"
    pd.DataFrame(records).to_csv(path, index=False, encoding="utf-8-sig")
    print("13試合・会場情報CSV保存:", path)

    info_path = out / f"toto{rnd}_official_round_info_v01.csv"
    pd.DataFrame([{
        "round": rnd,
        "sales_start": sales_start,
        "net_deadline": net_deadline,
        "result_date": result_date,
        "retrieved_at_jst": datetime.now(JST).isoformat(timespec="seconds"),
        "official_url": response.url,
    }]).to_csv(info_path, index=False, encoding="utf-8-sig")
    print("開催情報CSV保存:", info_path)

if __name__ == "__main__":
    main()
