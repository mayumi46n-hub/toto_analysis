import re
import sqlite3
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from normalize_team import normalize_team_name

DB_PATH = Path("data/toto.db")
INPUT_ROOT = Path("data/jleague_seasons")


def parse_attendance(text):
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else None


def parse_html(html_path, expected_year):
    html = html_path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    soup = BeautifulSoup(html, "html.parser")

    matches = []

    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [
                cell.get_text(" ", strip=True)
                for cell in tr.find_all(["td", "th"])
            ]

            if len(cells) < 10:
                continue

            if not cells[0].isdigit():
                continue

            season = int(cells[0])

            if season != expected_year:
                continue

            score_match = re.fullmatch(
                r"\s*(\d+)\s*-\s*(\d+)\s*",
                cells[6],
            )

            if score_match is None:
                continue

            home_score = int(score_match.group(1))
            away_score = int(score_match.group(2))

            matches.append((
                season,
                cells[1],
                cells[2],
                cells[3],
                cells[4],
                normalize_team_name(cells[5]),
                normalize_team_name(cells[7]),
                home_score,
                away_score,
                cells[8],
                parse_attendance(cells[9]),
                None,
            ))

    return matches


def load_season_matches(year):
    season_dir = INPUT_ROOT / str(year)

    html_files = [
        season_dir / "j1.html",
        season_dir / "j2.html",
    ]

    missing = [
        str(path)
        for path in html_files
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "HTMLがありません:\n" + "\n".join(missing)
        )

    all_matches = []

    for html_path in html_files:
        matches = parse_html(html_path, year)
        print(f"{html_path}: {len(matches)}試合")
        all_matches.extend(matches)

    return all_matches


def save_matches(year, matches):
    con = sqlite3.connect(DB_PATH)

    try:
        cur = con.cursor()

        cur.execute(
            "DELETE FROM jleague_matches WHERE season = ?",
            (year,),
        )

        cur.executemany("""
            INSERT INTO jleague_matches (
                season,
                competition,
                section,
                match_date,
                kickoff_time,
                home_team,
                away_team,
                home_score,
                away_score,
                stadium,
                attendance,
                match_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, matches)

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 src/import_season.py YEAR")
        print("例: python3 src/import_season.py 2002")
        sys.exit(1)

    year = int(sys.argv[1])
    matches = load_season_matches(year)

    if not matches:
        raise RuntimeError(
            f"{year}年の試合をHTMLから取得できませんでした"
        )

    save_matches(year, matches)

    print(f"{year}年 Jリーグ公式データ {len(matches)}試合を保存しました")


if __name__ == "__main__":
    main()