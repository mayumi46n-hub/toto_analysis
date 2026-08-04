from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


BASE_URL = (
    "https://store.toto-dream.com/dcs/subos/screen/pi09/spin003/"
    "PGSPIN00301InitVoteRate.form"
)

OUTPUT_FILE = Path("current_toto_matches.csv")


def fetch_current_toto(
    hold_cnt_id: int, year: int
) -> list[dict[str, object]]:
    url = f"{BASE_URL}?holdCntId={hold_cnt_id}&year={year}"
    response = requests.get(
        url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="kobetsu-format2")

    if table is None:
        raise ValueError(
            f"第{hold_cnt_id}回の投票結果表が見つかりません。"
        )

    rows: list[dict[str, object]] = []

    for tr in table.find_all("tr"):
        tds = tr.find_all("td")

        if len(tds) < 8:
            continue

        match_no_text = tds[2].get_text(" ", strip=True)

        if not match_no_text.isdigit():
            continue

        month_day = tds[0].get_text(" ", strip=True)

        home = tds[3].get_text(" ", strip=True)

        try:
            match_date = datetime.strptime(
                f"{year}/{month_day}",
                "%Y/%m/%d",
            ).strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"開催日を変換できません: {month_day}"
            )

        away = tds[7].get_text(" ", strip=True)

        vote_values: list[tuple[int, float]] = []

        for index in (4, 5, 6):
            text = tds[index].get_text(" ", strip=True)

            match = re.search(
                r"([\d,]+)（([\d.]+)%）", text
            )

            if match is None:
                break

            votes = int(match.group(1).replace(",", ""))
            rate = float(match.group(2))

            vote_values.append((votes, rate))

        if len(vote_values) != 3:
            continue

        rows.append(
            {
                "hold_cnt_id": hold_cnt_id,
                "match_no": int(match_no_text),
                "match_date": match_date,
                "home": home,
                "away": away,
                "home_rate": vote_values[0][1],
                "draw_rate": vote_values[1][1],
                "away_rate": vote_values[2][1],
            }
        )

    return rows


def save_csv(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "hold_cnt_id",
        "match_no",
        "match_date",
        "home",
        "away",
        "home_rate",
        "draw_rate",
        "away_rate",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "現在回のtoto投票率を取得して"
            "current_toto_matches.csvを作成します。"
        )
    )

    parser.add_argument(
        "hold_cnt_id", type=int, help="toto開催回"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="対象年（デフォルトは現在年）",
    )

    args = parser.parse_args()

    try:
        rows = fetch_current_toto(
            args.hold_cnt_id,
            args.year,
        )
    except (requests.RequestException, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1

    if not rows:
        print(
            "エラー: 対象試合を取得できませんでした。",
            file=sys.stderr,
        )
        return 1

    save_csv(rows)

    print(f"第{args.hold_cnt_id}回")
    print(f"取得件数: {len(rows)}")
    print(f"保存先: {OUTPUT_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
