import re
from bs4 import BeautifulSoup
from normalize_team import normalize_team_name


def section_text_to_dates(section_text, round_no):
    year = 2001 if round_no >= 3 else 2000
    dates = []

    for month_text, day_text in re.findall(r"(\d{1,2})[／/](\d{1,2})", section_text):
        date_text = f"{year}{int(month_text):02d}{int(day_text):02d}"
        if date_text not in dates:
            dates.append(date_text)

    for month_text, day_text in re.findall(r"(\d{1,2})月(\d{1,2})日", section_text):
        date_text = f"{year}{int(month_text):02d}{int(day_text):02d}"
        if date_text not in dates:
            dates.append(date_text)

    return dates


def yyyymmdd_to_db_like(date_text):
    return f"{date_text[2:4]}/{date_text[4:6]}/{date_text[6:8]}%"


def competition_condition(league):
    if league == "J1":
        return "competition LIKE 'Ｊ１%'"
    if league == "J2":
        return "competition = 'Ｊ２'"
    return "1 = 1"


def extract_toto_rows(html_path, table_index, round_no):
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    target_table = soup.find_all("table")[table_index]

    section_dates = {}
    match_rows = []

    current_league = None
    current_dates = []

    for tr in target_table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]

        if not cells:
            continue

        section_text = cells[0]

        if section_text.startswith("J1") and ("／" in section_text or "/" in section_text or "月" in section_text):
            current_league = "J1"
            current_dates = section_text_to_dates(section_text, round_no)
            section_dates["J1"] = current_dates
            print("開催日候補:", section_text, "→", ",".join(current_dates))

        elif section_text.startswith("J2") and ("／" in section_text or "/" in section_text or "月" in section_text):
            current_league = "J2"
            current_dates = section_text_to_dates(section_text, round_no)
            section_dates["J2"] = current_dates
            print("開催日候補:", section_text, "→", ",".join(current_dates))

        if len(cells) >= 9 and cells[3] == "勝":
            home_team = cells[1]
            away_team = cells[2]
            result_text = cells[-1]
        elif len(cells) >= 8 and cells[2] == "勝":
            home_team = cells[0]
            away_team = cells[1]
            result_text = cells[-1]
        else:
            continue

        m = re.search(r"\[(\d)\]", result_text)
        if not m:
            continue

        match_rows.append((
            normalize_team_name(home_team),
            normalize_team_name(away_team),
            m.group(1),
            current_league,
            list(current_dates),
        ))

    if "J1" in section_dates and "J2" not in section_dates and len(match_rows) > 8:
        section_dates["J2"] = section_dates["J1"]
        # toto Club側の日付誤記対策
    # 例: 第15回 J2 が 06月07日/06月08日 と書かれているが、
    # 実際は J1 と同じ 07月07日/07月08日
    if "J1" in section_dates and "J2" in section_dates:
        if section_dates["J1"] and section_dates["J2"]:
            j1_month = section_dates["J1"][0][4:6]
            j2_month = section_dates["J2"][0][4:6]

            if j1_month != j2_month:
                corrected_dates = []
                for date_text in section_dates["J2"]:
                    corrected_dates.append(
                        date_text[:4] + j1_month + date_text[6:8]
                    )

                section_dates["J2"] = corrected_dates

                match_rows = [
                    (
                        home,
                        away,
                        result,
                        league,
                        corrected_dates if league == "J2" else dates,
                    )
                    for home, away, result, league, dates in match_rows
                ]    

    return section_dates, match_rows