#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import argparse
import csv
import csv
import re

def load_round_manifest(path, round_no):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"STOP: missing manifest {path}")

    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if int(r["round_no"]) != round_no:
                continue
            rows.append((
                int(r["match_no"]),
                r["home_team"],
                r["away_team"],
            ))

    rows.sort(key=lambda x: x[0])

    if len(rows) != 13:
        raise SystemExit(
            f"STOP: round {round_no} manifest rows={len(rows)}"
        )

    return rows


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def parse_value(s):
    s = clean(s)
    if s == "":
        return None
    if s.endswith("%"):
        try:
            return float(s[:-1].strip())
        except Exception:
            return s
    s2 = s.replace(",", "")
    try:
        return float(s2)
    except Exception:
        return s

def soup(path):
    return BeautifulSoup(
        path.read_text(encoding="utf-8", errors="replace"),
        "html.parser"
    )

def visible_text(sp):
    return sp.get_text(" ", strip=True)

def first(pattern, text, group=1):
    m = re.search(pattern, text, re.I | re.S)
    if not m:
        return None
    return parse_value(m.group(group))

def tables_to_rows(sp):
    """
    table title -> list of rows
    row = list[str]
    """
    out = {}
    for table in sp.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [
                clean(x.get_text(" ", strip=True))
                for x in tr.find_all(["th", "td"])
            ]
            if cells:
                rows.append(cells)
        if not rows:
            continue
        title = rows[0][0] if rows[0] else ""
        if title:
            out.setdefault(title, []).append(rows)
    return out

def get_team_compare(tables, table_title, row_label, side):
    blocks = tables.get(table_title, [])
    for rows in blocks:
        for row in rows[1:]:
            if not row:
                continue
            if clean(row[0]) == row_label:
                if side == "home":
                    return parse_value(row[1]) if len(row) > 1 else None
                if side == "away":
                    return parse_value(row[2]) if len(row) > 2 else None
                if side == "avg":
                    return parse_value(row[3]) if len(row) > 3 else None
    return None

def get_market(tables):
    """
    MARKET table:
      マーケット | オッズ | データ
    """
    out = {}
    blocks = tables.get("マーケット", [])
    for rows in blocks:
        for row in rows[1:]:
            if len(row) >= 2:
                out[clean(row[0])] = {
                    "odds": parse_value(row[1]),
                    "data": parse_value(row[2]) if len(row) >= 3 else None,
                }
    return out

def market_find(market, predicate):
    for label, rec in market.items():
        if predicate(label):
            return rec["odds"]
    return None

def _team_stats_table(sp):
    """
    FootyStats team page の Stats table を構造的に読む。

    想定構造:
        Stats | Overall | At Home | At Away
        xG For / Match      1.27  1.39  1.20
        xG Against / Match  1.58  1.55  1.61
        Scored / Match      ...
        Conceded / Match    ...

    J1/J2や表示言語差に備えて複数ラベルを許容する。
    """
    candidates = []

    for table in sp.find_all("table"):
        rows = []

        for tr in table.find_all("tr"):
            cells = [
                clean(x.get_text(" ", strip=True))
                for x in tr.find_all(["th", "td"])
            ]
            if cells:
                rows.append(cells)

        if not rows:
            continue

        flat = " ".join(" ".join(r) for r in rows)

        score = 0
        for token in [
            "xG For",
            "xG Against",
            "Scored / Match",
            "Conceded / Match",
            "Overall",
            "At Home",
            "At Away",
        ]:
            if token.lower() in flat.lower():
                score += 1

        if score >= 4:
            candidates.append((score, rows))

    if not candidates:
        return {}

    candidates.sort(key=lambda x: x[0], reverse=True)
    rows = candidates[0][1]

    out = {}

    for row in rows:
        if len(row) < 2:
            continue

        label = clean(row[0]).casefold()

        vals = [
            parse_value(x)
            for x in row[1:4]
        ]

        while len(vals) < 3:
            vals.append(None)

        out[label] = {
            "all": vals[0],
            "home": vals[1],
            "away": vals[2],
        }

    return out


def _stats_lookup(stats, labels, split):
    for label in labels:
        rec = stats.get(label.casefold())
        if rec:
            return rec.get(split)
    return None


def extract_team_page(sp, text, prefix):
    """
    team page をまずHTML tableで読む。
    tableで取れない場合だけ旧regexをfallbackとして使う。
    """

    stats = _team_stats_table(sp)

    row = {
        f"{prefix}_gf_all": _stats_lookup(
            stats,
            ["Scored / Match", "Goals Scored / Match", "得点 / 試合"],
            "all",
        ),
        f"{prefix}_ga_all": _stats_lookup(
            stats,
            ["Conceded / Match", "Goals Conceded / Match", "失点 / 試合"],
            "all",
        ),

        f"{prefix}_xg_all": _stats_lookup(
            stats,
            ["xG For / Match", "xG For"],
            "all",
        ),
        f"{prefix}_xg_home": _stats_lookup(
            stats,
            ["xG For / Match", "xG For"],
            "home",
        ),
        f"{prefix}_xg_away": _stats_lookup(
            stats,
            ["xG For / Match", "xG For"],
            "away",
        ),

        f"{prefix}_xga_all": _stats_lookup(
            stats,
            ["xG Against / Match", "xG Against"],
            "all",
        ),
        f"{prefix}_xga_home": _stats_lookup(
            stats,
            ["xG Against / Match", "xG Against"],
            "home",
        ),
        f"{prefix}_xga_away": _stats_lookup(
            stats,
            ["xG Against / Match", "xG Against"],
            "away",
        ),
    }

    # Japanese-page fallback from v0.3.
    fallbacks = {
        f"{prefix}_gf_all":
            first(r"得点\s*-\s*[^0-9]*([0-9.]+)\s*平均得点", text),

        f"{prefix}_ga_all":
            first(r"失点\s*-\s*[^0-9]*([0-9.]+)\s*平均失点", text),

        f"{prefix}_xg_all":
            first(r"xG\s*\([^)]*\)\s*全試合\s*([0-9.]+)", text),

        f"{prefix}_xg_home":
            first(
                r"xG\s*\([^)]*\)\s*全試合\s*[0-9.]+\s*ホーム\s*([0-9.]+)",
                text,
            ),

        f"{prefix}_xg_away":
            first(
                r"xG\s*\([^)]*\)\s*全試合\s*[0-9.]+\s*ホーム\s*[0-9.]+\s*アウェイ\s*([0-9.]+)",
                text,
            ),

        f"{prefix}_xga_all":
            first(r"xG\s*\(相手チーム\)\s*全試合\s*([0-9.]+)", text),

        f"{prefix}_xga_home":
            first(
                r"xG\s*\(相手チーム\)\s*全試合\s*[0-9.]+\s*ホーム\s*([0-9.]+)",
                text,
            ),

        f"{prefix}_xga_away":
            first(
                r"xG\s*\(相手チーム\)\s*全試合\s*[0-9.]+\s*ホーム\s*[0-9.]+\s*アウェイ\s*([0-9.]+)",
                text,
            ),
    }

    for k, v in fallbacks.items():
        if row.get(k) is None:
            row[k] = v

    return row

def extract_match(no, home_team, away_team, root, round_no):
    base = f"{round_no}_{no:02d}"

    hp = root / f"{base}_home.html"
    xp = root / f"{base}_h2h.html"
    ap = root / f"{base}_away.html"

    for p in [hp, xp, ap]:
        if not p.exists():
            raise FileNotFoundError(p)

    hs = soup(hp)
    xs = soup(xp)
    a_s = soup(ap)

    ht = visible_text(hs)
    xt = visible_text(xs)
    at = visible_text(a_s)

    tables = tables_to_rows(xs)
    market = get_market(tables)

    row = {
        "round": round_no,
        "match_no": no,
        "home_team": home_team,
        "away_team": away_team,
    }

    row.update(extract_team_page(hs, ht, "home"))
    row.update(extract_team_page(a_s, at, "away"))

    # use correct venue-specific splits
    row["home_xg_venue"] = row.get("home_xg_home")
    row["home_xga_venue"] = row.get("home_xga_home")
    row["away_xg_venue"] = row.get("away_xg_away")
    row["away_xga_venue"] = row.get("away_xga_away")

    # SHOTS
    row.update({
        "shots_home":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数", "home"),
        "shots_away":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数", "away"),

        "sot_home":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数(オンターゲット)", "home"),
        "sot_away":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数(オンターゲット)", "away"),

        "off_target_home":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数(オフターゲット)", "home"),
        "off_target_away":
            get_team_compare(tables, "チームシュート平均/確率", "シュート数(オフターゲット)", "away"),

        "shot_conversion_home":
            get_team_compare(tables, "チームシュート平均/確率", "シュート決定率", "home"),
        "shot_conversion_away":
            get_team_compare(tables, "チームシュート平均/確率", "シュート決定率", "away"),

        "shots_per_goal_home":
            get_team_compare(tables, "チームシュート平均/確率", "ゴールあたりのシュート数", "home"),
        "shots_per_goal_away":
            get_team_compare(tables, "チームシュート平均/確率", "ゴールあたりのシュート数", "away"),
    })

    # TERRITORY / OTHER
    row.update({
        "offsides_home":
            get_team_compare(tables, "オフサイド数", "1試合平均オフサイド", "home"),
        "offsides_away":
            get_team_compare(tables, "オフサイド数", "1試合平均オフサイド", "away"),

        "fouls_home":
            get_team_compare(tables, "その他統計", "ファール数/試合", "home"),
        "fouls_away":
            get_team_compare(tables, "その他統計", "ファール数/試合", "away"),

        "fouled_home":
            get_team_compare(tables, "その他統計", "被ファール数/試合", "home"),
        "fouled_away":
            get_team_compare(tables, "その他統計", "被ファール数/試合", "away"),

        "possession_home":
            get_team_compare(tables, "その他統計", "支配率(平均)", "home"),
        "possession_away":
            get_team_compare(tables, "その他統計", "支配率(平均)", "away"),
    })

    # HALF
    row.update({
        "first_half_lead_home":
            get_team_compare(tables, "前後半チーム調子", "前半得点リード数", "home"),
        "first_half_lead_away":
            get_team_compare(tables, "前後半チーム調子", "前半得点リード数", "away"),

        "second_half_lead_home":
            get_team_compare(tables, "前後半チーム調子", "後半得点リード数", "home"),
        "second_half_lead_away":
            get_team_compare(tables, "前後半チーム調子", "後半得点リード数", "away"),

        "first_half_draw_home":
            get_team_compare(tables, "前後半チーム調子", "前半引き分け数", "home"),
        "first_half_draw_away":
            get_team_compare(tables, "前後半チーム調子", "前半引き分け数", "away"),

        "second_half_draw_home":
            get_team_compare(tables, "前後半チーム調子", "後半引き分け数", "home"),
        "second_half_draw_away":
            get_team_compare(tables, "前後半チーム調子", "後半引き分け数", "away"),
    })

    # SET PLAY / OTHER
    row.update({
        "free_kicks_home":
            get_team_compare(tables, "フリーキック", "1試合平均フリーキック数", "home"),
        "free_kicks_away":
            get_team_compare(tables, "フリーキック", "1試合平均フリーキック数", "away"),

        "goal_kicks_home":
            get_team_compare(tables, "ゴールキック数", "1試合平均ゴールキック", "home"),
        "goal_kicks_away":
            get_team_compare(tables, "ゴールキック数", "1試合平均ゴールキック", "away"),

        "throw_ins_home":
            get_team_compare(tables, "スローイン数", "1試合平均スローイン数", "home"),
        "throw_ins_away":
            get_team_compare(tables, "スローイン数", "1試合平均スローイン数", "away"),
    })

    # H2H / total-goal historical
    row.update({
        "h2h_over15":
            first(r"([0-9]+)%\s*オーバー1\.5", xt),

        "h2h_over25":
            first(r"([0-9]+)%\s*オーバー2\.5", xt),

        "h2h_over35":
            first(r"([0-9]+)%\s*オーバー3\.5", xt),

        "h2h_btts":
            first(r"([0-9]+)%\s*両チーム得点", xt),
    })

    # MARKET: dedicated parser
    # FootyStats H2H market table:
    #   first 勝利 row  = home
    #   second 勝利 row = away
    win_rows = [
        (label, rec["odds"])
        for label, rec in market.items()
        if "勝利" in label and rec.get("odds") is not None
    ]

    row["odds_home"] = win_rows[0][1] if len(win_rows) >= 1 else None
    row["odds_away"] = win_rows[1][1] if len(win_rows) >= 2 else None
    row["odds_draw"] = market.get("引き分け", {}).get("odds")
    row["odds_over25"] = market.get("オーバー2.5", {}).get("odds")
    row["odds_btts"] = market.get("両チーム得点", {}).get("odds")

    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument(
        "--input-root",
        default="data/raw/footystats/round_html"
    )
    ap.add_argument(
        "--output",
        default=None
    )
    args = ap.parse_args()

    root = Path(args.input_root) / str(args.round)

    output = (
        Path(args.output)
        if args.output
        else Path(
            f"data/analysis/footystats_toto{args.round}_normalized_v05.csv"
        )
    )

    round_matches = load_round_manifest(
        args.manifest,
        args.round
    )

    rows = []

    for no, home, away in round_matches:
        row = extract_match(no, home, away, root, args.round)
        rows.append(row)

        nonnull = sum(
            1 for k, v in row.items()
            if k not in {"round", "match_no", "home_team", "away_team"}
            and v is not None
        )

        print(
            f"No{no:02d} {home:6s} vs {away:6s} "
            f"nonnull={nonnull}"
        )

    # union of keys preserving first-seen order
    fieldnames = []
    seen = set()
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print("\nROWS:", len(rows))
    print("COLS:", len(fieldnames))
    print("SAVED:", output)

if __name__ == "__main__":
    main()
