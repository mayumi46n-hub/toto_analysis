#!/usr/bin/env python3

import argparse
import csv
import sqlite3
from pathlib import Path


def clean_url(value, label):
    url = (value or "").strip()
    if not url.startswith(("http://", "https://")):
        raise SystemExit(f"BAD_URL {label}: {url!r}")
    if any(ch in url for ch in "[]()"):
        raise SystemExit(f"MARKDOWN_CONTAMINATION {label}: {url!r}")
    return url


def resolve_team_id(con, team_name):
    rows = con.execute(
        """
        SELECT DISTINCT team_id
        FROM team_alias_v2
        WHERE alias_name = ?
        """,
        (team_name,),
    ).fetchall()

    ids = sorted({int(r[0]) for r in rows})

    if len(ids) != 1:
        raise SystemExit(
            f"TEAM_ID_RESOLUTION_ERROR team={team_name!r} ids={ids}"
        )

    return ids[0]


def resolve_club_url(con, team_id, team_name):
    rows = con.execute(
        """
        SELECT DISTINCT source_url
        FROM team_source_map
        WHERE team_id = ?
          AND source_name = 'footystats'
          AND is_primary = 1
          AND source_url IS NOT NULL
          AND TRIM(source_url) <> ''
        """,
        (team_id,),
    ).fetchall()

    urls = sorted({r[0].strip() for r in rows if r[0]})

    if len(urls) != 1:
        raise SystemExit(
            f"CLUB_URL_RESOLUTION_ERROR team={team_name!r} "
            f"team_id={team_id} urls={urls}"
        )

    return clean_url(urls[0], f"club:{team_name}")


def resolve_jleague_match_id(con, season, match_date, home_id, away_id):
    md = match_date.strip().replace("/", "")
    if len(md) != 4 or not md.isdigit():
        raise SystemExit(f"BAD_MATCH_DATE: {match_date}")
    prefix = f"{str(season)[-2:]}/{md[:2]}/{md[2:]}%"
    rows = con.execute("SELECT jleague_match_id,home_team,away_team FROM jleague_matches WHERE season=? AND match_date LIKE ?", (season, prefix)).fetchall()
    ids = []
    for mid, home, away in rows:
        if resolve_team_id(con, home) == home_id and resolve_team_id(con, away) == away_id:
            ids.append(int(mid))
    ids = sorted(set(ids))
    if len(ids) != 1:
        raise SystemExit(f"JLEAGUE_ID_RESOLUTION_ERROR date={match_date} home_id={home_id} away_id={away_id} ids={ids}")
    return ids[0]


def resolve_h2h_url(con, jleague_match_id):
    rows = con.execute(
        """
        SELECT DISTINCT source_url
        FROM web_snapshot_targets
        WHERE jleague_match_id = ?
          AND source_name = 'footystats'
          AND is_active = 1
          AND source_url IS NOT NULL
          AND TRIM(source_url) <> ''
        """,
        (jleague_match_id,),
    ).fetchall()

    urls = sorted({r[0].strip() for r in rows if r[0]})

    if len(urls) != 1:
        raise SystemExit(
            f"H2H_URL_RESOLUTION_ERROR "
            f"jleague_match_id={jleague_match_id} urls={urls}"
        )

    return clean_url(urls[0], f"h2h:{jleague_match_id}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--card", type=Path)
    ap.add_argument("--db", type=Path, default=Path("data/toto.db"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    card_path = args.card or Path(
        f"data/config/toto_rounds/{args.round}_card_official.csv"
    )
    out_path = args.out or Path(
        f"data/config/toto_rounds/"
        f"{args.round}_footystats_3html_manifest.csv"
    )

    if not card_path.is_file():
        raise SystemExit(f"CARD_NOT_FOUND: {card_path}")

    if not args.db.is_file():
        raise SystemExit(f"DB_NOT_FOUND: {args.db}")

    with card_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        card = list(csv.DictReader(f))

    if len(card) != 13:
        raise SystemExit(f"CARD_ROW_COUNT_ERROR: {len(card)}")

    required = {
        "match_no",
        "home_team",
        "away_team",
    }

    if not card:
        raise SystemExit("CARD_EMPTY")

    missing_columns = required - set(card[0].keys())
    if missing_columns:
        raise SystemExit(
            f"CARD_MISSING_COLUMNS: {sorted(missing_columns)}"
        )

    round_column = None
    if "toto_round" in card[0]:
        round_column = "toto_round"
    elif "round_no" in card[0]:
        round_column = "round_no"

    if round_column:
        bad_rounds = [
            row.get(round_column)
            for row in card
            if int(row[round_column]) != args.round
        ]
        if bad_rounds:
            raise SystemExit(
                f"CARD_ROUND_MISMATCH: requested={args.round} "
                f"values={bad_rounds}"
            )

    match_nos = [int(row["match_no"]) for row in card]
    if sorted(match_nos) != list(range(1, 14)):
        raise SystemExit(f"MATCH_NO_ERROR: {match_nos}")

    con = sqlite3.connect(args.db)
    resolved_jleague_ids = []

    try:
        output_rows = []

        for row in sorted(
            card, key=lambda x: int(x["match_no"])
        ):
            match_no = int(row["match_no"])
            home_team = row["home_team"].strip()
            away_team = row["away_team"].strip()

            home_id = resolve_team_id(con, home_team)
            away_id = resolve_team_id(con, away_team)

            raw_jleague_id = (row.get("jleague_match_id") or "").strip()
            if raw_jleague_id:
                jleague_match_id = int(raw_jleague_id)
            else:
                match_date = (row.get("match_date") or "").strip()
                if not match_date:
                    raise SystemExit(f"JLEAGUE_ID_AND_DATE_MISSING match_no={match_no}")
                seasons = [int(x[0]) for x in con.execute("SELECT DISTINCT season FROM web_snapshot_targets WHERE toto_round_no=? AND season IS NOT NULL", (args.round,)).fetchall()]
                if len(seasons) != 1:
                    raise SystemExit(f"SEASON_RESOLUTION_ERROR round={args.round} seasons={seasons}")
                jleague_match_id = resolve_jleague_match_id(
                    con, seasons[0], match_date, home_id, away_id
                )

            resolved_jleague_ids.append(jleague_match_id)

            home_url = resolve_club_url(
                con, home_id, home_team
            )
            away_url = resolve_club_url(
                con, away_id, away_team
            )
            h2h_url = resolve_h2h_url(
                con, jleague_match_id
            )

            output_rows.append(
                {
                    "round_no": args.round,
                    "match_no": match_no,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_url": home_url,
                    "h2h_url": h2h_url,
                    "away_url": away_url,
                }
            )
    finally:
        con.close()

    if len(resolved_jleague_ids) != 13 or len(set(resolved_jleague_ids)) != 13:
        raise SystemExit(f"JLEAGUE_MATCH_ID_DUPLICATE: {resolved_jleague_ids}")

    all_urls = []
    for row in output_rows:
        all_urls.extend(
            [
                row["home_url"],
                row["h2h_url"],
                row["away_url"],
            ]
        )

    if len(output_rows) != 13:
        raise SystemExit(
            f"MANIFEST_ROW_COUNT_ERROR: {len(output_rows)}"
        )

    if len(all_urls) != 39:
        raise SystemExit(f"URL_COUNT_ERROR: {len(all_urls)}")

    h2h_urls = {row["h2h_url"] for row in output_rows}
    if len(h2h_urls) != 13:
        raise SystemExit(
            f"H2H_UNIQUE_ERROR: {len(h2h_urls)}"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "round_no",
        "match_no",
        "home_team",
        "away_team",
        "home_url",
        "h2h_url",
        "away_url",
    ]

    with out_path.open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print("MANIFEST_QA: PASS")
    print("ROUND:", args.round)
    print("MATCHES:", len(output_rows))
    print("URLS:", len(all_urls))
    print("H2H_UNIQUE:", len(h2h_urls))
    print("OUTPUT:", out_path)


if __name__ == "__main__":
    main()
