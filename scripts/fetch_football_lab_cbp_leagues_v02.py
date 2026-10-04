#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlunparse
import csv
import hashlib
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


BASE = "https://www.football-lab.jp"
YEAR = "2026"

LEAGUES = ["j1", "j2", "j3"]

CATEGORIES = {
    "offense": "攻撃",
    "pass": "パス",
    "cross": "クロス",
    "dribble": "ドリブル",
    "receive": "パスレシーブ",
    "shot": "シュート",
    "goal": "ゴール",
    "gain": "奪取",
    "defense": "守備",
    "save": "セーブ",
}

OUT_ROOT = Path(
    "data/raw/football_lab/cbp/2026"
)

MANIFEST_JSON = OUT_ROOT / "manifest_v01.json"
MANIFEST_CSV = OUT_ROOT / "manifest_v01.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "Chrome/126 Safari/537.36 "
        "totoLABO-research/1.0"
    ),
    "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
}

TIMEOUT = 30
SLEEP_SEC = 2.0
MIN_BYTES = 8000


def clean_text(s):
    return re.sub(r"\s+", "", str(s or "")).strip()


def force_year(url):
    p = urlparse(url)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q["year"] = YEAR

    return urlunparse(
        (
            p.scheme,
            p.netloc,
            p.path,
            p.params,
            urlencode(q),
            p.fragment,
        )
    )


def validate_response(resp, url):
    if resp.status_code != 200:
        raise RuntimeError(
            f"HTTP {resp.status_code}: {url}"
        )

    if len(resp.content) < MIN_BYTES:
        raise RuntimeError(
            f"SHORT RESPONSE "
            f"bytes={len(resp.content)}: {url}"
        )

    low = resp.text.lower()

    block_words = [
        "cloudflare",
        "captcha",
        "access denied",
        "too many requests",
    ]

    for word in block_words:
        if word in low:
            raise RuntimeError(
                f"POSSIBLE BLOCK '{word}': {url}"
            )


def fetch(session, url):
    resp = session.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    validate_response(resp, url)

    return resp


def discover_menu_urls(html, league):
    soup = BeautifulSoup(html, "html.parser")

    wanted_by_label = {
        clean_text(label): key
        for key, label in CATEGORIES.items()
    }

    found = {}

    for a in soup.find_all("a", href=True):
        text = clean_text(
            a.get_text(" ", strip=True)
        )

        if text not in wanted_by_label:
            continue

        href = urljoin(
            BASE,
            a["href"],
        )

        parsed = urlparse(href)

        expected_path = (
            f"/summary/cbp_ranking/{league}"
        )

        # Football LAB menu links use a trailing slash:
        # /summary/cbp_ranking/j1/
        # Normalize both forms before comparison.
        if parsed.path.rstrip("/") != expected_path.rstrip("/"):
            continue

        key = wanted_by_label[text]

        found[key] = force_year(href)

    return found


def page_metadata(content):
    soup = BeautifulSoup(
        content,
        "html.parser",
    )

    title = ""

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True,
        )

    text = soup.get_text(
        " ",
        strip=True,
    )

    m = re.search(
        r"20\d{2}\.\d{1,2}\.\d{1,2}\s*update",
        text,
        flags=re.I,
    )

    update_text = (
        m.group(0)
        if m
        else ""
    )

    return {
        "title": title,
        "tables": len(
            soup.find_all("table")
        ),
        "update_text": update_text,
    }


def verify_category(content, label):
    soup = BeautifulSoup(
        content,
        "html.parser",
    )

    title = clean_text(
        soup.title.get_text(
            " ",
            strip=True,
        )
        if soup.title
        else ""
    )

    # "ゴール"など短いラベルもあるため
    # title内にカテゴリ名が存在することを確認。
    if clean_text(label) not in title:
        raise RuntimeError(
            f"CATEGORY TITLE MISMATCH "
            f"expected={label} "
            f"title={title[:120]}"
        )

    if not soup.find("table"):
        raise RuntimeError(
            f"NO TABLE FOUND "
            f"category={label}"
        )


def main():
    OUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    session = requests.Session()

    records = []

    for league in LEAGUES:
        print(
            f"\n=== DISCOVER {league.upper()} ==="
        )

        seed_url = (
            f"{BASE}/summary/"
            f"cbp_ranking/{league}"
            f"?data=offense&year={YEAR}"
        )

        try:
            seed_resp = fetch(
                session,
                seed_url,
            )
        except Exception as e:
            print(
                f"STOP: seed fetch failed: {e}"
            )
            sys.exit(1)

        discovered = discover_menu_urls(
            seed_resp.text,
            league,
        )

        # Seed自身がData Menu上で
        # selected itemとしてリンクになっていない場合に備える。
        discovered.setdefault(
            "offense",
            seed_url,
        )

        print(
            "DISCOVERED:",
            len(discovered),
            "/",
            len(CATEGORIES),
        )

        for key, label in CATEGORIES.items():
            url = discovered.get(key)

            if not url:
                print(
                    f"STOP: missing menu URL "
                    f"{league} {key} {label}"
                )
                print(
                    "FOUND:",
                    sorted(discovered)
                )
                sys.exit(1)

            print(
                f"  {key:8s} "
                f"{label:8s} "
                f"{url}"
            )

        league_dir = OUT_ROOT / league

        league_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for i, (key, label) in enumerate(
            CATEGORIES.items(),
            start=1,
        ):
            url = discovered[key]

            # offense seedだけは再取得しない
            if key == "offense":
                resp = seed_resp
            else:
                time.sleep(SLEEP_SEC)

                try:
                    resp = fetch(
                        session,
                        url,
                    )
                except Exception as e:
                    print(
                        f"STOP: fetch failed "
                        f"{league} {key}: {e}"
                    )
                    sys.exit(1)

            try:
                verify_category(
                    resp.content,
                    label,
                )
            except Exception as e:
                print(
                    f"STOP: validation failed "
                    f"{league} {key}: {e}"
                )
                sys.exit(1)

            path = (
                league_dir
                / f"{key}.html"
            )

            path.write_bytes(
                resp.content
            )

            meta = page_metadata(
                resp.content
            )

            sha = hashlib.sha256(
                resp.content
            ).hexdigest()

            record = {
                "year": YEAR,
                "league": league,
                "category": key,
                "label": label,
                "url": url,
                "http_status":
                    resp.status_code,
                "bytes":
                    len(resp.content),
                "tables":
                    meta["tables"],
                "update_text":
                    meta["update_text"],
                "title":
                    meta["title"],
                "sha256":
                    sha,
                "saved_path":
                    str(path),
            }

            records.append(record)

            print(
                f"FETCH "
                f"{league.upper()} "
                f"{i:02d}/10 "
                f"{key:8s} "
                f"status={resp.status_code} "
                f"bytes={len(resp.content)} "
                f"tables={meta['tables']}"
            )

    if len(records) != 30:
        raise SystemExit(
            f"STOP: records={len(records)} "
            f"expected=30"
        )

    MANIFEST_JSON.write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    fields = list(
        records[0].keys()
    )

    with MANIFEST_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        w = csv.DictWriter(
            f,
            fieldnames=fields,
        )

        w.writeheader()
        w.writerows(records)

    print(
        "\n=== FOOTBALL LAB CBP RAW V01 ==="
    )

    print(
        "FETCHED:",
        len(records),
        "/ 30",
    )

    for league in LEAGUES:
        subset = [
            x for x in records
            if x["league"] == league
        ]

        print(
            league.upper(),
            f"{len(subset)}/10",
            "bytes=",
            sum(x["bytes"] for x in subset),
        )

    print(
        "MANIFEST JSON:",
        MANIFEST_JSON,
    )

    print(
        "MANIFEST CSV :",
        MANIFEST_CSV,
    )

    print(
        "RAW ROOT     :",
        OUT_ROOT,
    )

    print(
        "\nSTEP 6a RAW ACQUISITION: PASS"
    )


if __name__ == "__main__":
    main()
