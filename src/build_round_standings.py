import csv
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB = "data/toto.db"
ROUND_MASTER = Path("data/round_master.csv")
SEASON = 2001


def empty_stats():
    return {
        "played": 0,
        "win": 0,
        "draw": 0,
        "lose": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_diff": 0,
        "points": 0,
    }


def parse_match_date(s):
    # 例: 01/11/17(土) -> 20011117
    m = re.search(r"(\d{2})/(\d{2})/(\d{2})", s or "")
    if not m:
        return ""
    yy, mm, dd = m.groups()
    return f"20{yy}{mm}{dd}"


def apply_match(stats, team, gf, ga):
    stats[team]["played"] += 1
    stats[team]["goals_for"] += gf
    stats[team]["goals_against"] += ga
    stats[team]["goal_diff"] = stats[team]["goals_for"] - stats[team]["goals_against"]

    if gf > ga:
        stats[team]["win"] += 1
        stats[team]["points"] += 3
    elif gf < ga:
        stats[team]["lose"] += 1
    else:
        stats[team]["draw"] += 1
        stats[team]["points"] += 1


def calculate_ranking(stats):
    rows = [{"team": team, **s} for team, s in stats.items()]
    rows.sort(key=lambda r: (-r["points"], -r["goal_diff"], -r["goals_for"], r["team"]))

    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    return rows


def load_round_master():
    rows = []
    with ROUND_MASTER.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["year"]) == SEASON:
                rows.append(row)

    rows.sort(key=lambda r: int(r["round_no"]))
    return rows


def j1_competition_name(row):
    comp_id = int(row["j1_competition_id"])
    if comp_id == 129:
        return "Ｊ１ １ｓｔ"
    if comp_id == 130:
        return "Ｊ１ ２ｎｄ"
    raise ValueError(f"unknown J1 competition_id: {comp_id}")


def cutoff_date(row):
    dates = [row.get("date_key", ""), row.get("date1", ""), row.get("date2", "")]
    dates = [d for d in dates if d]
    return max(dates)


def load_jleague_matches(cur):
    cur.execute("""
        SELECT
            competition,
            match_date,
            home_team,
            away_team,
            home_score,
            away_score
        FROM jleague_matches
        WHERE season = ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY match_date, kickoff_time
    """, (SEASON,))

    rows = []
    for competition, match_date, home, away, hs, aw in cur.fetchall():
        rows.append({
            "competition": competition,
            "date": parse_match_date(match_date),
            "home_team": home,
            "away_team": away,
            "home_score": hs,
            "away_score": aw,
        })

    return rows


def build_stats(matches, competition_name, cutoff):
    stats = defaultdict(empty_stats)

    for m in matches:
        if m["competition"] != competition_name:
            continue
        if not m["date"] or m["date"] > cutoff:
            continue

        apply_match(stats, m["home_team"], m["home_score"], m["away_score"])
        apply_match(stats, m["away_team"], m["away_score"], m["home_score"])

    return calculate_ranking(stats)


def save_standings(cur, round_no, league, ranking_rows):
    for row in ranking_rows:
        cur.execute("""
            INSERT OR REPLACE INTO round_standings (
                season,
                round_no,
                league,
                team,
                rank,
                played,
                win,
                draw,
                lose,
                goals_for,
                goals_against,
                goal_diff,
                points
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            SEASON,
            round_no,
            league,
            row["team"],
            row["rank"],
            row["played"],
            row["win"],
            row["draw"],
            row["lose"],
            row["goals_for"],
            row["goals_against"],
            row["goal_diff"],
            row["points"],
        ))


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        DELETE FROM round_standings
        WHERE season = ?
    """, (SEASON,))

    round_rows = load_round_master()
    matches = load_jleague_matches(cur)

    for row in round_rows:
        round_no = int(row["round_no"])
        cutoff = cutoff_date(row)

        j1_comp = j1_competition_name(row)

        j1_ranking = build_stats(matches, j1_comp, cutoff)
        j2_ranking = build_stats(matches, "Ｊ２", cutoff)

        save_standings(cur, round_no, "J1", j1_ranking)
        save_standings(cur, round_no, "J2", j2_ranking)

        print(
            f"第{round_no}回 cutoff={cutoff}: "
            f"J1 {len(j1_ranking)}チーム / J2 {len(j2_ranking)}チーム"
        )

    con.commit()
    con.close()

    print("J1/J2別 round_standings 作成完了")


if __name__ == "__main__":
    main()