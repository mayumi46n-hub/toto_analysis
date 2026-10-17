#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import re
import time
import argparse
import sqlite3

import pandas as pd
import requests
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser()
parser.add_argument("--round", type=int, required=True)
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--delay", type=float, default=2.0)
parser.add_argument("--out-dir", type=Path, default=None)
args = parser.parse_args()
ROUND_NO = args.round
ROUND = Path(f"data/config/toto_rounds/{ROUND_NO}_card_official.csv")
if not ROUND.exists():
    legacy_round = Path(f"data/config/toto_rounds/{ROUND_NO}.csv")
    if legacy_round.exists():
        ROUND = legacy_round

SLUGS = Path(
    "data/analysis/"
    "football_lab_team_slug_map_2026_v02.csv"
)

STAMP = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

OUT = args.out_dir if args.out_dir is not None else Path(
    "data/raw/football_lab/"
    f"toto{ROUND_NO}_previews_{STAMP}_v01"
)

MANIFEST = (
    OUT / "manifest.csv"
)


def stop(msg):
    print("STOP:", msg)
    raise SystemExit(2)


if not ROUND.exists():
    stop(f"missing {ROUND}")

if not SLUGS.exists():
    stop(f"missing {SLUGS}")


rnd = pd.read_csv(
    ROUND,
    low_memory=False,
)

sm = pd.read_csv(
    SLUGS,
    low_memory=False,
)

con = sqlite3.connect("data/toto.db")
aliases = pd.read_sql_query("SELECT alias_name, team_id FROM team_alias_v2", con)
master = pd.read_sql_query("SELECT team_id, short_name, full_name FROM team_master", con)



names = pd.concat([aliases.rename(columns={"alias_name": "name"}), master[["team_id", "short_name"]].rename(columns={"short_name": "name"}), master[["team_id", "full_name"]].rename(columns={"full_name": "name"})]).dropna().drop_duplicates()
name_to_team_id = dict(zip(names["name"].astype(str), names["team_id"]))
team_id_to_slug = {}
for _, sr in sm.iterrows():
    tid = name_to_team_id.get(str(sr["team_short"]), name_to_team_id.get(str(sr["team_display"])))
    if tid is not None:
        if tid in team_id_to_slug and team_id_to_slug[tid] != str(sr["slug"]):
            stop(f"ambiguous Football LAB slug team_id={tid}")
        team_id_to_slug[tid] = str(sr["slug"])


if len(rnd) != 13:
    stop(
        f"round rows={len(rnd)}"
    )


resolved = []
for _, rr in rnd.sort_values("match_no").iterrows():
    no = int(rr["match_no"])
    home = str(rr["home_team"])
    away = str(rr["away_team"])
    hid = name_to_team_id.get(home)
    aid = name_to_team_id.get(away)
    slug = team_id_to_slug.get(hid) if hid is not None else None
    if hid is None or aid is None or not slug:
        stop(f"No{no:02d} identity/slug unresolved: {home}-{away}")
    resolved.append((no, home, away, hid, aid, slug))
if len(resolved) != 13:
    stop(f"resolved matches={len(resolved)}")
if args.dry_run:
    [print(f"No{x[0]:02d} {x[1]}-{x[2]} home_id={x[3]} away_id={x[4]} slug={x[5]}") for x in resolved]
    print("DRY_RUN_QA PASS 13/13")
    raise SystemExit(0)

session = requests.Session()

session.headers.update({
    "User-Agent":
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140 Safari/537.36",
    "Accept":
        "text/html,application/xhtml+xml",
})


OUT.mkdir(
    parents=True,
    exist_ok=args.out_dir is not None,
)


rows = []


print("STATE-18c2b")
print("OUT", OUT)


for _, r in rnd.sort_values(
    "match_no"
).iterrows():

    no = int(
        r["match_no"]
    )

    home = str(
        r["home_team"]
    )

    away = str(
        r["away_team"]
    )

    home_team_id = name_to_team_id.get(home)
    if home_team_id is None:
        stop(f"No{no:02d} unresolved team identity: {home}")
    slug = team_id_to_slug.get(home_team_id)

    if not slug:
        stop(
            f"No{no:02d} missing slug: {home}"
        )

    url = (
        f"https://www.football-lab.jp/"
        f"{slug}/preview"
    )

    path = OUT / f"{ROUND_NO}_{no:02d}_{slug}_preview.html"

    reused = False
    if path.exists() and path.stat().st_size >= 10000:
        candidate = path.read_bytes()
        candidate_text = candidate.decode("utf-8", errors="replace")
        reused = "Football LAB" in candidate_text and "プレビュー" in candidate_text
    if reused:
        content = candidate
        html_text = candidate_text
        http_status = 200
        size = len(content)
        print(f"No{no:02d} REUSE {path}")
    else:
        resp = session.get(url, timeout=30)
        http_status = resp.status_code
        content = resp.content
        html_text = resp.text
        size = len(content)
        if http_status != 200:
            stop(f"No{no:02d} HTTP {http_status}")
        if size < 10000:
            stop(f"No{no:02d} HTML too small {size}")
        path.write_bytes(content)

    soup = BeautifulSoup(
        html_text,
        "html.parser",
    )

    text = soup.get_text(
        " ",
        strip=True,
    )

    formation_pending = (
        "予想フォーメーションは後日更新予定"
        in text
    )

    has_absence_section = (
        "欠場選手情報"
        in text
    )

    suspension_mentions = len(
        re.findall(
            "出場停止",
            text,
        )
    )

    absence_mentions = len(
        re.findall(
            "欠場情報",
            text,
        )
    )

    # Extract page update date if visible.
    m = re.search(
        r"(\d{4}\.\d{1,2}\.\d{1,2})"
        r"\s*update",
        text,
    )

    page_update = (
        m.group(1)
        if m
        else pd.NA
    )

    rows.append({
        "round_no":
            ROUND_NO,
        "match_no":
            no,
        "home_team":
            home,
        "away_team":
            away,
        "home_slug":
            slug,
        "preview_url":
            url,
        "http_status":
            http_status,
        "bytes":
            size,
        "page_update":
            page_update,
        "formation_pending":
            formation_pending,
        "absence_section":
            has_absence_section,
        "absence_mentions":
            absence_mentions,
        "suspension_mentions":
            suspension_mentions,
        "raw_path":
            str(path),
    })

    print(
        f"No{no:02d} "
        f"{home}-{away} "
        f"bytes={size} "
        f"formation_pending="
        f"{int(formation_pending)} "
        f"absence="
        f"{int(has_absence_section)}"
    )

    if not reused:
        time.sleep(args.delay)


d = pd.DataFrame(rows)


if len(d) != 13:
    stop(
        f"manifest rows={len(d)}"
    )


if not d[
    "http_status"
].eq(200).all():
    stop(
        "non-200 page exists"
    )


d.to_csv(
    MANIFEST,
    index=False,
)


print()
print("PREVIEW_PAGES", len(d))
print(
    "FORMATION_PENDING",
    int(
        d["formation_pending"]
        .sum()
    ),
)
print(
    "ABSENCE_SECTION",
    int(
        d["absence_section"]
        .sum()
    ),
)
print(
    "TOTAL_ABSENCE_MENTIONS",
    int(
        d["absence_mentions"]
        .sum()
    ),
)

print("MANIFEST", MANIFEST)
print("PASS")
