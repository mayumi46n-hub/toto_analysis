import argparse
import re
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path

DB_PATH = Path("data/toto.db")

DEFAULT_REST_DAYS = 30
MAX_REST_DAYS = 30


def detect_league(competition):
    text = (competition or "").strip().upper()

    if text.startswith("Ｊ１") or text.startswith("J1"):
        return "J1"

    if text.startswith("Ｊ２") or text.startswith("J2"):
        return "J2"

    return None


def parse_match_date(season, value):
    match = re.search(
        r"\d{2}/(\d{2})/(\d{2})",
        value or "",
    )

    if match is None:
        raise ValueError(
            f"試合日を解析できません: "
            f"season={season}, match_date={value!r}"
        )

    month_text, day_text = match.groups()

    return date(
        int(season),
        int(month_text),
        int(day_text),
    )


def create_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS match_rest (
            season INTEGER NOT NULL,
            jleague_match_id INTEGER NOT NULL,

            league TEXT NOT NULL,
            match_date TEXT NOT NULL,
            kickoff_time TEXT,

            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,

            home_rest_days INTEGER NOT NULL,
            away_rest_days INTEGER NOT NULL,
            rest_diff INTEGER NOT NULL,

            home_first_match INTEGER NOT NULL,
            away_first_match INTEGER NOT NULL,

            PRIMARY KEY (
                season,
                jleague_match_id
            )
        )
    """)


def load_matches(
    con,
    start_season,
    end_season,
):
    rows = con.execute("""
        SELECT
            season,
            jleague_match_id,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team
        FROM jleague_matches
        WHERE season BETWEEN ? AND ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY
            season,
            match_date,
            kickoff_time,
            jleague_match_id
    """, (
        start_season,
        end_season,
    )).fetchall()

    matches = []

    for row in rows:
        (
            season,
            match_id,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team,
        ) = row

        league = detect_league(competition)

        if league is None:
            continue

        parsed_date = parse_match_date(
            season,
            match_date,
        )

        matches.append({
            "season": season,
            "jleague_match_id": match_id,
            "league": league,
            "match_date": match_date,
            "date_value": parsed_date,
            "kickoff_time": kickoff_time or "",
            "home_team": home_team,
            "away_team": away_team,
        })

    matches.sort(
        key=lambda match: (
            match["date_value"],
            match["kickoff_time"],
            match["jleague_match_id"],
        )
    )

    return matches


def calculate_rest_days(
    last_match_dates,
    team,
    current_date,
):
    previous_date = last_match_dates.get(team)

    if previous_date is None:
        return DEFAULT_REST_DAYS, 1

    days = (
        current_date - previous_date
    ).days

    if days < 0:
        raise RuntimeError(
            f"試合日の順序が不正です: "
            f"team={team}, "
            f"previous={previous_date}, "
            f"current={current_date}"
        )

    capped_days = min(
        days,
        MAX_REST_DAYS,
    )

    return capped_days, 0


def build_rows(matches):
    matches_by_date = defaultdict(list)

    for match in matches:
        matches_by_date[
            match["date_value"]
        ].append(match)

    last_match_dates = {}
    output_rows = []

    for current_date in sorted(
        matches_by_date
    ):
        day_matches = matches_by_date[
            current_date
        ]

        # 同日開催の全試合について、
        # 当日の結果を反映する前に特徴量を作る
        for match in day_matches:
            home_team = match["home_team"]
            away_team = match["away_team"]

            (
                home_rest_days,
                home_first_match,
            ) = calculate_rest_days(
                last_match_dates=last_match_dates,
                team=home_team,
                current_date=current_date,
            )

            (
                away_rest_days,
                away_first_match,
            ) = calculate_rest_days(
                last_match_dates=last_match_dates,
                team=away_team,
                current_date=current_date,
            )

            output_rows.append({
                "season": match["season"],
                "jleague_match_id": (
                    match["jleague_match_id"]
                ),

                "league": match["league"],
                "match_date": (
                    match["match_date"]
                ),
                "kickoff_time": (
                    match["kickoff_time"]
                ),

                "home_team": home_team,
                "away_team": away_team,

                "home_rest_days": (
                    home_rest_days
                ),
                "away_rest_days": (
                    away_rest_days
                ),
                "rest_diff": (
                    home_rest_days
                    - away_rest_days
                ),

                "home_first_match": (
                    home_first_match
                ),
                "away_first_match": (
                    away_first_match
                ),
            })

        # 同日全試合の特徴量生成後に
        # 最終試合日を更新する
        for match in day_matches:
            last_match_dates[
                match["home_team"]
            ] = current_date

            last_match_dates[
                match["away_team"]
            ] = current_date

    return output_rows


def save_rows(
    con,
    start_season,
    end_season,
    rows,
):
    con.execute("""
        DELETE FROM match_rest
        WHERE season BETWEEN ? AND ?
    """, (
        start_season,
        end_season,
    ))

    con.executemany("""
        INSERT INTO match_rest (
            season,
            jleague_match_id,

            league,
            match_date,
            kickoff_time,

            home_team,
            away_team,

            home_rest_days,
            away_rest_days,
            rest_diff,

            home_first_match,
            away_first_match
        )
        VALUES (
            :season,
            :jleague_match_id,

            :league,
            :match_date,
            :kickoff_time,

            :home_team,
            :away_team,

            :home_rest_days,
            :away_rest_days,
            :rest_diff,

            :home_first_match,
            :away_first_match
        )
    """, rows)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "J1/J2全試合について、"
            "試合前の休養日数特徴量を生成します。"
        )
    )

    parser.add_argument(
        "start_season",
        type=int,
        help="開始年度。例: 2002",
    )

    parser.add_argument(
        "end_season",
        type=int,
        help="終了年度。例: 2025",
    )

    args = parser.parse_args()

    if args.start_season > args.end_season:
        parser.error(
            "開始年度は終了年度以下にしてください"
        )

    con = sqlite3.connect(DB_PATH)

    try:
        create_table(con)

        matches = load_matches(
            con=con,
            start_season=args.start_season,
            end_season=args.end_season,
        )

        if not matches:
            raise RuntimeError(
                "対象となるJ1/J2試合がありません"
            )

        rows = build_rows(matches)

        save_rows(
            con=con,
            start_season=args.start_season,
            end_season=args.end_season,
            rows=rows,
        )

        con.commit()

        print(
            f"対象年度: "
            f"{args.start_season}"
            f"〜{args.end_season}"
        )
        print(
            f"試合読込: {len(matches)}件"
        )
        print(
            f"休養日数保存: {len(rows)}件"
        )
        print(
            f"休養日数上限: {MAX_REST_DAYS}日"
        )
        print(
            "match_rest Version 1 作成完了"
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()