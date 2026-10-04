#!/usr/bin/env python3

from pathlib import Path
from bs4 import BeautifulSoup
import argparse
import csv
import hashlib
import json
import re


def load_round_manifest(path, round_no):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"STOP: missing manifest {path}")

    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rr = int(r["round_no"])
            if rr != round_no:
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



CATEGORY_PATTERNS = {
    "RESULT_FORM": [
        r"勝率", r"勝利", r"引き分け", r"敗北",
        r"フォーム", r"平均勝点", r"PPG",
    ],
    "ATTACK": [
        r"得点", r"Scored", r"攻撃",
    ],
    "DEFENSE": [
        r"失点", r"Conceded", r"クリーンシート",
        r"Clean Sheet",
    ],
    "XG": [
        r"\bxG\b", r"xGA", r"Expected Goals",
    ],
    "SHOTS": [
        r"シュート", r"Shots", r"オンターゲット",
        r"オフターゲット", r"決定率",
    ],
    "GOALS_TOTALS": [
        r"オーバー", r"アンダー", r"BTTS",
        r"両チーム得点", r"合計ゴール",
    ],
    "HALF": [
        r"前半", r"後半", r"ハーフ",
        r"1st Half", r"2nd Half",
    ],
    "TIMING": [
        r"\d+\s*分", r"10分", r"15分",
    ],
    "CORNERS": [
        r"コーナー", r"Corner",
    ],
    "CARDS": [
        r"カード", r"Card", r"イエロー", r"レッド",
    ],
    "TERRITORY": [
        r"支配率", r"Possession", r"オフサイド",
        r"Offside",
    ],
    "SETPLAY_OTHER": [
        r"フリーキック", r"ゴールキック", r"スローイン",
        r"ファール", r"Free.Kick", r"Goal.Kick",
        r"Throw.in", r"Foul",
    ],
    "H2H": [
        r"H2H", r"直接対決", r"対戦成績",
    ],
    "PLAYERS": [
        r"選手", r"Player", r"得点ランキング",
        r"カードランキング",
    ],
    "ODDS": [
        r"オッズ", r"Odds", r"マーケット",
    ],
}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def table_rows(soup):
    result = []

    for idx, table in enumerate(soup.find_all("table"), 1):
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

        result.append({
            "table_index": idx,
            "title": rows[0][0] if rows[0] else None,
            "rows": rows,
        })

    return result


def headings(soup):
    out = []

    for tag in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6"]
    ):
        txt = clean(tag.get_text(" ", strip=True))
        if txt:
            out.append({
                "tag": tag.name,
                "text": txt,
            })

    return out


def category_lines(text):
    # Break large visible text into manageable semantic chunks.
    chunks = [
        clean(x)
        for x in re.split(
            r"(?<=[。.!?])\s+|\n+",
            text
        )
        if clean(x)
    ]

    out = {}

    for cat, patterns in CATEGORY_PATTERNS.items():
        hits = []
        seen = set()

        for chunk in chunks:
            if any(
                re.search(p, chunk, re.I)
                for p in patterns
            ):
                if chunk not in seen:
                    seen.add(chunk)
                    hits.append(chunk)

        out[cat] = hits

    return out


def parse_page(path, page_type):
    raw = path.read_bytes()

    soup = BeautifulSoup(
        raw.decode("utf-8", errors="replace"),
        "html.parser"
    )

    title = (
        clean(soup.title.get_text(" ", strip=True))
        if soup.title else None
    )

    text = clean(soup.get_text(" ", strip=True))

    scripts = []

    for script in soup.find_all("script"):
        txt = script.get_text(" ", strip=True)

        if not txt:
            continue

        # Keep metadata only; avoid enormous duplicate script bodies.
        scripts.append({
            "type": script.get("type"),
            "id": script.get("id"),
            "chars": len(txt),
            "preview": clean(txt[:500]),
        })

    return {
        "page_type": page_type,
        "file": str(path),
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "title": title,
        "headings": headings(soup),
        "tables": table_rows(soup),
        "scripts": scripts,
        "categories": category_lines(text),
        "visible_text": text,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument(
        "--input-root",
        default="data/raw/footystats/round_html"
    )
    ap.add_argument(
        "--output-root",
        default="data/parsed/footystats"
    )
    args = ap.parse_args()

    root = Path(args.input_root) / str(args.round)
    out_root = (
        Path(args.output_root)
        / f"toto{args.round}_full_v02"
    )

    out_root.mkdir(
        parents=True,
        exist_ok=True
    )

    round_matches = load_round_manifest(
        args.manifest,
        args.round
    )

    manifest = []

    for no, home, away in round_matches:
        pages = {}

        for kind in ["home", "h2h", "away"]:
            path = root / (
                f"{args.round}_{no:02d}_{kind}.html"
            )

            if not path.exists():
                raise SystemExit(
                    f"STOP: missing {path}"
                )

            pages[kind] = parse_page(
                path,
                kind
            )

        obj = {
            "round": args.round,
            "match_no": no,
            "home_team": home,
            "away_team": away,
            "pages": pages,
        }

        out = (
            out_root
            / f"toto{args.round}_{no:02d}_full_v02.json"
        )

        out.write_text(
            json.dumps(
                obj,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        page_stats = {}

        for kind, page in pages.items():
            page_stats[kind] = {
                "bytes": page["bytes"],
                "tables": len(page["tables"]),
                "headings": len(page["headings"]),
                "categories": {
                    k: len(v)
                    for k, v
                    in page["categories"].items()
                },
            }

        manifest.append({
            "match_no": no,
            "home_team": home,
            "away_team": away,
            "output": str(out),
            "pages": page_stats,
        })

        print(
            f"No{no:02d} "
            f"{home} vs {away} "
            f"HOME tables={len(pages['home']['tables'])} "
            f"H2H tables={len(pages['h2h']['tables'])} "
            f"AWAY tables={len(pages['away']['tables'])}"
        )

    manifest_path = (
        out_root
        / f"toto{args.round}_manifest_v02.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("MATCHES:", len(manifest))
    print("JSON COUNT:", len(list(out_root.glob("*_full_v02.json"))))
    print("MANIFEST:", manifest_path)
    print("SAVED ROOT:", out_root)


if __name__ == "__main__":
    main()
