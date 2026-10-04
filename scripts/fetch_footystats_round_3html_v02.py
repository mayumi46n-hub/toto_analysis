#!/usr/bin/env python3
from pathlib import Path
import argparse
import csv
import hashlib
import random
import requests
import sqlite3
import time

BLOCK_MARKERS = [
    "captcha",
    "verify you are human",
    "checking your browser",
    "attention required",
    "access denied",
    "cloudflare ray id",
]

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36 toto-analysis-snapshot/1.0"
)

ROUND1653 = [
    (1, 46189, "水戸", "川崎Ｆ"),
    (2, 46190, "清水", "福岡"),
    (3, 46192, "Ｇ大阪", "FC東京"),
    (4, 46191, "町田", "横浜FM"),
    (5, 46194, "長崎", "名古屋"),
    (6, 46193, "広島", "Ｃ大阪"),
    (7, 46197, "東京Ｖ", "千葉"),
    (8, 46198, "浦和", "岡山"),
    (9, 46565, "今治", "鳥栖"),
    (10, 46560, "いわき", "横浜FC"),
    (11, 46561, "八戸", "湘南"),
    (12, 46564, "甲府", "磐田"),
    (13, 46559, "秋田", "徳島"),
]

def get_team_url(con, short_name):
    row = con.execute("""
        SELECT tsm.source_url
        FROM team_source_map tsm
        JOIN team_master tm ON tm.team_id = tsm.team_id
        WHERE tsm.source_name='footystats'
          AND tm.short_name=?
          AND tsm.is_primary=1
        LIMIT 1
    """, (short_name,)).fetchone()

    return row["source_url"] if row else None

def get_h2h_url(con, match_id):
    row = con.execute("""
        SELECT source_url
        FROM web_snapshot_targets
        WHERE jleague_match_id=?
          AND source_name='footystats'
          AND is_active=1
        ORDER BY snapshot_target_id DESC
        LIMIT 1
    """, (match_id,)).fetchone()

    if row:
        return row["source_url"]

    row = con.execute("""
        SELECT source_url
        FROM footystats_match_urls
        WHERE jleague_match_id=?
        ORDER BY footystats_match_url_id DESC
        LIMIT 1
    """, (match_id,)).fetchone()

    return row["source_url"] if row else None

def validate(kind, r):
    if r.status_code != 200:
        raise RuntimeError(f"HTTP_ERROR {kind}: {r.status_code}")

    ctype = r.headers.get("Content-Type", "")
    if "html" not in ctype.lower():
        raise RuntimeError(f"NON_HTML {kind}: {ctype}")

    if len(r.content) < 10000:
        raise RuntimeError(f"HTML_TOO_SMALL {kind}: {len(r.content)}")

    low = r.text.casefold()

    hits = [m for m in BLOCK_MARKERS if m in low]
    if hits:
        raise RuntimeError(f"BOT_CHALLENGE {kind}: {hits[0]}")

    if "footystats" not in low:
        raise RuntimeError(f"FOOTYSTATS_MARKER_MISSING {kind}")

def fetch_one(session, url, out):
    r = session.get(url, timeout=30, allow_redirects=True)
    validate(out.stem, r)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(r.content)

    return {
        "status": r.status_code,
        "bytes": len(r.content),
        "final_url": r.url,
        "sha256": hashlib.sha256(r.content).hexdigest(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out-root", default="data/raw/footystats/round_html")
    ap.add_argument("--page-delay-min", type=int, default=50)
    ap.add_argument("--page-delay-max", type=int, default=90)
    ap.add_argument("--match-delay-min", type=int, default=120)
    ap.add_argument("--match-delay-max", type=int, default=240)
    ap.add_argument("--limit", type=int, default=13)
    ap.add_argument("--session-max-requests", type=int, default=2)
    args = ap.parse_args()

    with open(args.manifest,encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))

    rows=[r for r in rows if int(r["round_no"])==args.round][:args.limit]
    if not rows:
        raise SystemExit("NO_MANIFEST_ROWS")

    out_root=Path(args.out_root)/str(args.round)

    def new_session():
        sess=requests.Session()
        sess.headers.update({
            "User-Agent":UA,
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language":"ja,en-US;q=0.8,en;q=0.6",
            "DNT":"1",
        })
        return sess

    sess=new_session()
    request_count=0

    try:
        for idx,r in enumerate(rows):
            no=int(r["match_no"]); home=r["home_team"]; away=r["away_team"]
            print("\n"+"="*88)
            print(f"No{no:02d} {home} vs {away}")
            print("="*88)

            pages=[("home",r["home_url"]),("h2h",r["h2h_url"]),("away",r["away_url"])]
            if any(not u for _,u in pages):
                raise RuntimeError(f"MISSING_URL No{no:02d}")

            for pidx,(kind,url) in enumerate(pages):
                out=out_root/f"{args.round}_{no:02d}_{kind}.html"

                if out.exists() and out.stat().st_size>=10000:
                    print(f"SKIP {kind}: existing {out.stat().st_size} bytes")
                    continue

                print(f"GET  {kind}: {url}")
                if request_count and request_count%args.session_max_requests==0:
                    sess.close(); sess=new_session()
                    print("SESSION RESET")

                try:
                    meta=fetch_one(sess,url,out)
                    request_count+=1
                except Exception as exc:
                    print(f"STOP No{no:02d} {kind}: {exc}")
                    raise

                print(f"SAVED {kind}: bytes={meta['bytes']} sha={meta['sha256'][:12]} final={meta['final_url']}")

                if pidx<2:
                    wait=random.randint(args.page_delay_min,args.page_delay_max)
                    print(f"WAIT page {wait}s"); time.sleep(wait)

            if idx<len(rows)-1:
                wait=random.randint(args.match_delay_min,args.match_delay_max)
                print(f"WAIT match {wait}s"); time.sleep(wait)
    finally:
        sess.close()

    good=sum(
        (out_root/f"{args.round}_{int(r['match_no']):02d}_{k}.html").exists() and
        (out_root/f"{args.round}_{int(r['match_no']):02d}_{k}.html").stat().st_size>=10000
        for r in rows for k in ("home","h2h","away")
    )
    print(f"\nREADY {good}/{len(rows)*3}")
    print("DONE")

if __name__ == "__main__":
    main()
