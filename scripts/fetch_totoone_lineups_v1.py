#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


TOP_URL = "https://www.totoone.jp/"
GRAPHQL_URL = "https://v2.totoone.jp/api/v1/graphql/"

QUERY = """
query GetMatchQuery($id: ID!) {
  match(id: $id) {
    id
    kickOff
    sectionText
    homeTeam { shortName }
    awayTeam { shortName }
    homeDetail {
      formation
      startingMember
      playerDifficult
      playerMiss
      playerSuspended
    }
    awayDetail {
      formation
      startingMember
      playerDifficult
      playerMiss
      playerSuspended
    }
  }
}
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Fetch current totoONE predicted starting XI "
            "for the current toto round."
        )
    )

    p.add_argument(
        "--toto-round",
        type=int,
        default=None,
        help=(
            "Expected toto round. "
            "If specified, current totoONE top-page round "
            "must match."
        ),
    )

    p.add_argument(
        "--out-dir",
        default="data/players",
        help="CSV output directory.",
    )

    p.add_argument(
        "--raw-dir",
        default="data/raw/totoone",
        help="Raw HTML/JSON parent directory.",
    )

    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and validate without saving files.",
    )

    return p.parse_args()


def normalize_team(value: object) -> str:
    return unicodedata.normalize(
        "NFKC",
        str(value),
    ).strip()


def normalize_name(value: object) -> str:
    text = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    text = text.translate(
        str.maketrans({
            "髙": "高",
            "﨑": "崎",
            "德": "徳",
            "濵": "濱",
        })
    )

    text = re.sub(
        r"[\s　・･·.\-]",
        "",
        text,
    )

    return text.lower()


def parse_player(raw: object) -> tuple[str, str]:
    text = unicodedata.normalize(
        "NFKC",
        str(raw),
    ).strip()

    m = re.match(
        r"^\s*(\d+)\s+(.+?)\s*$",
        text,
    )

    if m:
        return (
            m.group(1),
            m.group(2).strip(),
        )

    return "", text


def clean_list(value: object) -> str:
    if not isinstance(value, list):
        return ""

    return "、".join(
        str(x).strip()
        for x in value
        if str(x).strip()
    )


def get_top_round(
    session: requests.Session,
) -> tuple[str, dict]:
    r = session.get(
        TOP_URL,
        timeout=30,
    )

    r.raise_for_status()

    html = r.text

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    node = soup.find(
        "script",
        id="__NEXT_DATA__",
    )

    if node is None:
        raise RuntimeError(
            "__NEXT_DATA__ not found"
        )

    data = json.loads(
        node.get_text()
    )

    page_props = (
        data["props"]["pageProps"]
    )

    rd = page_props["round"]

    return html, rd


def get_toto_matches(
    round_data: dict,
) -> list[dict]:
    lotteries = (
        round_data.get("lotteries")
        or []
    )

    candidates = [
        x for x in lotteries
        if x.get("category") == "toto"
    ]

    if len(candidates) != 1:
        raise RuntimeError(
            "toto lottery not uniquely found: "
            f"{len(candidates)}"
        )

    matches = (
        candidates[0].get("matches")
        or []
    )

    if len(matches) != 13:
        raise RuntimeError(
            "expected 13 toto matches, "
            f"got {len(matches)}"
        )

    return matches


def fetch_match_detail(
    session: requests.Session,
    match_id: int,
) -> dict:
    res = session.post(
        GRAPHQL_URL,
        json={
            "operationName":
                "GetMatchQuery",

            "variables": {
                "id": match_id,
            },

            "query":
                QUERY,
        },
        headers={
            "Origin":
                TOP_URL,

            "Content-Type":
                "application/json",
        },
        timeout=30,
    )

    res.raise_for_status()

    body = res.json()

    errors = body.get("errors")

    if errors:
        raise RuntimeError(
            f"GraphQL error match={match_id}: "
            f"{errors}"
        )

    rec = (
        body
        .get("data", {})
        .get("match")
    )

    if rec is None:
        raise RuntimeError(
            "match detail unavailable: "
            f"{match_id}"
        )

    return body


def validate_member_count(
    match_no: int,
    team: str,
    members: list,
) -> None:
    n = len(members)

    # 0 = totoONE側に予想XIなし
    # 11 = 正常な予想XI
    if n in (0, 11):
        return

    raise RuntimeError(
        f"No.{match_no} {team}: "
        f"predicted starters must be 0 or 11, "
        f"got {n}"
    )


def main() -> None:
    args = parse_args()

    session = requests.Session()

    session.headers.update({
        "User-Agent":
            "Mozilla/5.0",
    })

    html, round_data = (
        get_top_round(session)
    )

    current_round = int(
        round_data["id"]
    )

    if (
        args.toto_round is not None
        and current_round
        != args.toto_round
    ):
        raise RuntimeError(
            "round mismatch: "
            f"totoONE current={current_round}, "
            f"requested={args.toto_round}"
        )

    round_no = (
        args.toto_round
        if args.toto_round is not None
        else current_round
    )

    matches = get_toto_matches(
        round_data
    )

    collected_at = (
        datetime.now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )

    stamp = (
        datetime.now()
        .astimezone()
        .strftime("%Y%m%d_%H%M%S")
    )

    details: dict[int, dict] = {}

    player_rows = []
    side_rows = []
    match_rows = []

    print(
        "========== FETCH TOTOONE =========="
    )
    print("round:", round_no)
    print("matches:", len(matches))

    for match_no, meta in enumerate(
        matches,
        start=1,
    ):
        mid = int(meta["id"])

        body = fetch_match_detail(
            session,
            mid,
        )

        details[mid] = body

        rec = body["data"]["match"]

        home = normalize_team(
            rec["homeTeam"]["shortName"]
        )

        away = normalize_team(
            rec["awayTeam"]["shortName"]
        )

        side_info = {}

        for (
            side,
            team,
            detail_key,
        ) in [
            (
                "home",
                home,
                "homeDetail",
            ),
            (
                "away",
                away,
                "awayDetail",
            ),
        ]:
            detail = (
                rec.get(detail_key)
                or {}
            )

            members = (
                detail.get(
                    "startingMember"
                )
                or []
            )

            validate_member_count(
                match_no,
                team,
                members,
            )

            formation = (
                detail.get("formation")
                or ""
            )

            difficult = clean_list(
                detail.get(
                    "playerDifficult"
                )
            )

            miss = clean_list(
                detail.get(
                    "playerMiss"
                )
            )

            suspended = clean_list(
                detail.get(
                    "playerSuspended"
                )
            )

            side_rows.append({
                "toto_round":
                    round_no,

                "match_no":
                    match_no,

                "totoone_match_id":
                    mid,

                "kickoff":
                    rec.get(
                        "kickOff"
                    ),

                "section_text":
                    rec.get(
                        "sectionText"
                    ),

                "home":
                    home,

                "away":
                    away,

                "side":
                    side,

                "team":
                    team,

                "formation":
                    formation,

                "predicted_starters":
                    len(members),

                "lineup_available":
                    int(
                        len(members)
                        == 11
                    ),

                "player_difficult":
                    difficult,

                "player_miss":
                    miss,

                "player_suspended":
                    suspended,

                "collected_at":
                    collected_at,
            })

            side_info[side] = {
                "formation":
                    formation,

                "starters":
                    len(members),
            }

            for order, raw in enumerate(
                members,
                start=1,
            ):
                (
                    shirt_number,
                    player_name,
                ) = parse_player(raw)

                player_rows.append({
                    "toto_round":
                        round_no,

                    "match_no":
                        match_no,

                    "totoone_match_id":
                        mid,

                    "kickoff":
                        rec.get(
                            "kickOff"
                        ),

                    "section_text":
                        rec.get(
                            "sectionText"
                        ),

                    "home":
                        home,

                    "away":
                        away,

                    "side":
                        side,

                    "team":
                        team,

                    "formation":
                        formation,

                    "lineup_order":
                        order,

                    "shirt_number":
                        shirt_number,

                    "player_name":
                        player_name,

                    "normalized_name":
                        normalize_name(
                            player_name
                        ),

                    "is_starter":
                        1,

                    "lineup_status":
                        (
                            "予想先発"
                            "（確定先発ではない）"
                        ),

                    "player_difficult":
                        difficult,

                    "player_miss":
                        miss,

                    "player_suspended":
                        suspended,

                    "collected_at":
                        collected_at,
                })

        match_rows.append({
            "toto_round":
                round_no,

            "match_no":
                match_no,

            "totoone_match_id":
                mid,

            "kickoff":
                rec.get("kickOff"),

            "section_text":
                rec.get(
                    "sectionText"
                ),

            "home":
                home,

            "away":
                away,

            "home_formation":
                side_info[
                    "home"
                ]["formation"],

            "away_formation":
                side_info[
                    "away"
                ]["formation"],

            "home_predicted_starters":
                side_info[
                    "home"
                ]["starters"],

            "away_predicted_starters":
                side_info[
                    "away"
                ]["starters"],

            "collected_at":
                collected_at,
        })

        print(
            f"No{match_no:02d}",
            f"{home}-{away}",
            f"{side_info['home']['starters']}/"
            f"{side_info['away']['starters']}",
        )

    players = pd.DataFrame(
        player_rows
    )

    sides = pd.DataFrame(
        side_rows
    )

    match_df = pd.DataFrame(
        match_rows
    )

    if len(match_df) != 13:
        raise RuntimeError(
            "match validation failed: "
            f"{len(match_df)}"
        )

    if len(sides) != 26:
        raise RuntimeError(
            "side validation failed: "
            f"{len(sides)}"
        )

    duplicate_side = (
        sides.duplicated(
            [
                "match_no",
                "side",
            ]
        ).any()
    )

    if duplicate_side:
        raise RuntimeError(
            "duplicate match-side rows"
        )

    bad_counts = sides[
        ~sides[
            "predicted_starters"
        ].isin([0, 11])
    ]

    if len(bad_counts):
        raise RuntimeError(
            "invalid starter counts"
        )

    print()
    print(
        "========== VALIDATION =========="
    )

    print(
        "match rows:",
        len(match_df),
    )

    print(
        "team-side rows:",
        len(sides),
    )

    print(
        "starter rows:",
        len(players),
    )

    available = int(
        sides[
            "lineup_available"
        ].sum()
    )

    print(
        "teams with XI:",
        f"{available}/26",
    )

    unavailable = sides[
        sides[
            "lineup_available"
        ].eq(0)
    ]

    if len(unavailable):
        print()
        print(
            "========== XI UNAVAILABLE =========="
        )

        print(
            unavailable[
                [
                    "match_no",
                    "side",
                    "team",
                ]
            ].to_string(
                index=False
            )
        )

    if args.dry_run:
        print()
        print(
            "DRY RUN: no files saved"
        )
        return

    out_dir = Path(
        args.out_dir
    )

    raw_parent = Path(
        args.raw_dir
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    base = (
        f"totoone_toto{round_no}"
    )

    players_out = (
        out_dir
        / (
            f"{base}_predicted_lineups_"
            f"{stamp}_v1.csv"
        )
    )

    sides_out = (
        out_dir
        / (
            f"{base}_summary_"
            f"{stamp}_v1.csv"
        )
    )

    matches_out = (
        out_dir
        / (
            f"{base}_matches_"
            f"{stamp}_v1.csv"
        )
    )

    raw_dir = (
        raw_parent
        / (
            f"toto{round_no}_"
            f"{stamp}_v1"
        )
    )

    targets = [
        players_out,
        sides_out,
        matches_out,
        raw_dir,
    ]

    existing = [
        str(x)
        for x in targets
        if x.exists()
    ]

    if existing:
        print(
            "STOP: refusing overwrite"
        )

        for x in existing:
            print(x)

        sys.exit(1)

    raw_dir.mkdir(
        parents=True
    )

    (
        raw_dir
        / "totoone_top.html"
    ).write_text(
        html,
        encoding="utf-8",
    )

    for mid, body in details.items():
        (
            raw_dir
            / f"match{mid}.json"
        ).write_text(
            json.dumps(
                body,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    players.to_csv(
        players_out,
        index=False,
        encoding="utf-8-sig",
    )

    sides.to_csv(
        sides_out,
        index=False,
        encoding="utf-8-sig",
    )

    match_df.to_csv(
        matches_out,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print(
        "========== SAVED =========="
    )
    print(players_out)
    print(sides_out)
    print(matches_out)
    print(raw_dir)


if __name__ == "__main__":
    main()
