from pathlib import Path
from bs4 import BeautifulSoup
import csv
import re
import sys

ROOT = Path("data/raw/football_lab/cbp/2026")
OUT = Path(
    "data/analysis/"
    "football_lab_team_cbp_2026_normalized_v01.csv"
)

TEAM_CATEGORIES = {
    "offense": "攻撃",
    "pass": "パス",
    "cross": "クロス",
    "dribble": "ドリブル",
    "shot": "シュート",
    "goal": "ゴール",
    "gain": "奪取",
    "defense": "守備",
    "save": "セーブ",
}

EXPECTED_TEAMS = 20


def clean(x):
    return " ".join(str(x).split())


def num(x):
    x = clean(x).replace(",", "")
    if x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def integer(x):
    v = num(x)
    if v is None:
        return None
    return int(v)


def extract_team_names(cell):
    """
    Football LAB team cell contains long + short names, e.g.
      サンフレッチェ広島 広島
      ＦＣ東京 FC東京

    Prefer anchor text structure if available.
    Keep both full display text and short name.
    """
    texts = []

    for s in cell.stripped_strings:
        s = clean(s)
        if s and s not in texts:
            texts.append(s)

    full_display = clean(cell.get_text(" ", strip=True))

    short_name = texts[-1] if texts else full_display

    # If only one flattened string exists, use it safely as both.
    return full_display, short_name


def rows_from_team_table(path, league, category):
    html = path.read_bytes()
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", id="ls_teamCBP")

    if table is None:
        raise ValueError(
            f"{league}/{category}: "
            "ls_teamCBP not found"
        )

    trs = table.find_all("tr")

    if len(trs) != EXPECTED_TEAMS + 1:
        raise ValueError(
            f"{league}/{category}: "
            f"expected 21 rows incl header, got {len(trs)}"
        )

    out = []

    for tr in trs[1:]:
        cells = tr.find_all(["th", "td"])
        vals = [
            clean(c.get_text(" ", strip=True))
            for c in cells
        ]

        if len(cells) != 10:
            raise ValueError(
                f"{league}/{category}: "
                f"expected 10 cells, got {len(cells)} "
                f"row={vals}"
            )

        rank = integer(vals[0])

        # Audit established:
        # 0 rank
        # 1 blank/icon
        # 2 team
        # 3 category points
        # 4 per-match
        # 5 recent-five
        # 6 league rank
        # 7 points
        # 8 goals for
        # 9 goals against
        team_display, team_short = extract_team_names(
            cells[2]
        )

        row = {
            "league": league.upper(),
            "team_display": team_display,
            "team_short": team_short,
            "category": category,
            "cbp_rank": rank,
            "cbp_total": num(vals[3]),
            "cbp_per_match": num(vals[4]),
            "cbp_recent5": num(vals[5]),
            "league_rank": integer(vals[6]),
            "league_points": integer(vals[7]),
            "goals_for": integer(vals[8]),
            "goals_against": integer(vals[9]),
        }

        if row["cbp_rank"] is None:
            raise ValueError(
                f"{league}/{category}: invalid CBP rank"
            )

        if not row["team_short"]:
            raise ValueError(
                f"{league}/{category}: empty team"
            )

        if row["cbp_total"] is None:
            raise ValueError(
                f"{league}/{category}: "
                f"null cbp_total for {team_display}"
            )

        out.append(row)

    return out


def main():
    long_rows = []
    errors = []

    for league in ["j1", "j2"]:
        for category in TEAM_CATEGORIES:
            path = ROOT / league / f"{category}.html"

            if not path.exists():
                errors.append(
                    f"missing: {path}"
                )
                continue

            try:
                rows = rows_from_team_table(
                    path,
                    league,
                    category,
                )
            except Exception as e:
                errors.append(str(e))
                continue

            print(
                f"PARSED {league.upper():2s} "
                f"{category:8s} "
                f"teams={len(rows)}"
            )

            long_rows.extend(rows)

    if errors:
        print()
        print("=== ERRORS ===")
        for e in errors:
            print("-", e)
        print("NORMALIZE: FAIL")
        sys.exit(1)

    expected_long = (
        2
        * EXPECTED_TEAMS
        * len(TEAM_CATEGORIES)
    )

    if len(long_rows) != expected_long:
        raise SystemExit(
            f"STOP: expected {expected_long} "
            f"long rows, got {len(long_rows)}"
        )

    # Build one row per league/team.
    teams = {}

    for r in long_rows:
        key = (
            r["league"],
            r["team_short"],
        )

        base = teams.setdefault(
            key,
            {
                "league": r["league"],
                "team_short": r["team_short"],
                "team_display": r["team_display"],
            },
        )

        cat = r["category"]

        for field in [
            "cbp_rank",
            "cbp_total",
            "cbp_per_match",
            "cbp_recent5",
        ]:
            base[f"{cat}_{field}"] = r[field]

        # League result columns are duplicated across
        # categories. Preserve once, then cross-check.
        common = {
            "league_rank": r["league_rank"],
            "league_points": r["league_points"],
            "goals_for": r["goals_for"],
            "goals_against": r["goals_against"],
        }

        for field, value in common.items():
            if field in base and base[field] != value:
                raise SystemExit(
                    "STOP: common-field mismatch "
                    f"{key} {field}: "
                    f"{base[field]} vs {value}"
                )

            base[field] = value

    if len(teams) != 40:
        raise SystemExit(
            f"STOP: expected 40 league/team rows, "
            f"got {len(teams)}"
        )

    rows = sorted(
        teams.values(),
        key=lambda r: (
            r["league"],
            r["league_rank"],
            r["team_short"],
        ),
    )

    base_cols = [
        "league",
        "team_short",
        "team_display",
        "league_rank",
        "league_points",
        "goals_for",
        "goals_against",
    ]

    metric_cols = []

    for cat in TEAM_CATEGORIES:
        metric_cols.extend([
            f"{cat}_cbp_rank",
            f"{cat}_cbp_total",
            f"{cat}_cbp_per_match",
            f"{cat}_cbp_recent5",
        ])

    cols = base_cols + metric_cols

    # Strict completeness check:
    # receive is intentionally NOT represented here,
    # because audit proved it has no Team CBP table.
    nulls = []

    for r in rows:
        for c in cols:
            if r.get(c) is None:
                nulls.append(
                    (r["league"], r["team_short"], c)
                )

    if nulls:
        print()
        print("=== NULLS ===")
        for x in nulls[:30]:
            print(x)

        raise SystemExit(
            f"STOP: normalized NULL count={len(nulls)}"
        )

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        w = csv.DictWriter(
            f,
            fieldnames=cols,
        )
        w.writeheader()
        w.writerows(rows)

    print()
    print("=== FOOTBALL LAB TEAM CBP NORMALIZED V01 ===")
    print("TEAM CATEGORIES :", len(TEAM_CATEGORIES))
    print(
        "CATEGORIES      :",
        ", ".join(TEAM_CATEGORIES),
    )
    print("RECEIVE         : EXCLUDED (player-only)")
    print("LONG ROWS       :", len(long_rows))
    print("TEAM ROWS       :", len(rows))
    print(
        "J1 ROWS         :",
        sum(r["league"] == "J1" for r in rows),
    )
    print(
        "J2 ROWS         :",
        sum(r["league"] == "J2" for r in rows),
    )
    print("NORMALIZED NULL :", len(nulls))
    print("SAVED           :", OUT)
    print()
    print("NORMALIZE TEAM CBP: PASS")

    print()
    print("=== SAMPLE ===")

    for r in rows[:5]:
        print(
            r["league"],
            r["team_short"],
            "rank=", r["league_rank"],
            "off=", r["offense_cbp_total"],
            "shot=", r["shot_cbp_total"],
            "gain=", r["gain_cbp_total"],
            "def=", r["defense_cbp_total"],
        )


if __name__ == "__main__":
    main()
