#!/usr/bin/env python3
from pathlib import Path
import argparse
import csv
import hashlib
import random
import requests
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

def validate_existing(kind, out):
    content=out.read_bytes()
    if len(content) < 10000:
        return False
    low=content.decode("utf-8", errors="ignore").casefold()
    if any(m in low for m in BLOCK_MARKERS):
        return False
    if "footystats" not in low:
        return False
    return True

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
    ap.add_argument("--dry-run", action="store_true")
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

                if out.exists():
                    if validate_existing(out.stem, out):
                        print(f"SKIP {kind}: validated existing {out.stat().st_size} bytes")
                        continue
                    raise RuntimeError(f"EXISTING_HTML_INVALID {out}")

                if args.dry_run:
                    print(f"WOULD_GET {kind}: {url}")
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

            if idx<len(rows)-1 and not args.dry_run:
                wait=random.randint(args.match_delay_min,args.match_delay_max)
                print(f"WAIT match {wait}s"); time.sleep(wait)
    finally:
        sess.close()

    good=sum(
        validate_existing(k, out_root/f"{args.round}_{int(r['match_no']):02d}_{k}.html")
        for r in rows for k in ("home","h2h","away")
        if (out_root/f"{args.round}_{int(r['match_no']):02d}_{k}.html").exists()
    )
    print(f"\nREADY {good}/{len(rows)*3}")
    print("DONE")

if __name__ == "__main__":
    main()
