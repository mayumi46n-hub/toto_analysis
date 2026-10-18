#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    p = argparse.ArgumentParser(description="Prepare a toto round using validated generic pipeline components.")
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--fetch-footystats", action="store_true")
    p.add_argument("--fetch-football-lab", action="store_true")
    return p.parse_args()


def validate_card(rnd):
    card = ROOT / "data" / "config" / "toto_rounds" / f"{rnd}_card_official.csv"
    if not card.exists():
        raise RuntimeError(f"CARD_NOT_FOUND {card}")
    with card.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 13:
        raise RuntimeError(f"CARD_ROW_COUNT {len(rows)} expected=13")
    nums = sorted(int(r["match_no"]) for r in rows)
    if nums != list(range(1, 14)):
        raise RuntimeError(f"CARD_MATCH_NO_INVALID {nums}")
    print(f"CARD_QA: PASS round={rnd} matches=13")
    return card


def run(label, command, dry_run=False):
    print(f"STEP: {label}")
    print("$", " ".join(map(str, command)))
    if dry_run:
        print("DRY_RUN: SKIP EXECUTION")
        return
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(f"PIPELINE_STOP {label} returncode={result.returncode}")


if __name__ == "__main__":
    args = parse_args()
    card = validate_card(args.round)
    manifest = ROOT / "data" / "config" / "toto_rounds" / f"{args.round}_footystats_3html_manifest.csv"
    run("FOOTYSTATS MANIFEST", [sys.executable, str(ROOT / "scripts" / "build_footystats_round_manifest_v02.py"), "--round", str(args.round), "--card", str(card), "--out", str(manifest)], False)
    if args.fetch_footystats:
        run("FOOTYSTATS FETCH", [sys.executable, str(ROOT / "scripts" / "fetch_footystats_round_3html_v02.py"), "--round", str(args.round), "--manifest", str(manifest)], args.dry_run)
    if args.fetch_football_lab:
        run("FOOTBALL LAB FETCH", [sys.executable, str(ROOT / "scripts" / "fetch_football_lab_round_previews_v01.py"), "--round", str(args.round)], args.dry_run)
