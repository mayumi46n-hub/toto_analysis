#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


DB = "data/toto.db"

TOP_URL = (
    "https://"
    + "www.totoone.jp/"
)

GRAPHQL_URL = (
    "https://"
    + "v2.totoone.jp/api/v1/graphql/"
)

ARCHIVE_1645 = Path(
    "data/evaluation/"
    "toto_1645_analysis_06_candidate_20260814_173324_"
    "predicted_lineups_players.csv"
)

ROUND_MATCH_IDS = {
    1644: list(range(28095, 28108)),
    1645: list(range(28108, 28121)),
    1647: list(range(28069, 28082)),
}


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


TEAM_ALIASES = {
    "c大阪": "セレッソ大阪",
    "セレッソ大阪": "セレッソ大阪",

    "東京v": "東京ヴェルディ",
    "東京ヴェルディ": "東京ヴェルディ",

    "川崎f": "川崎フロンターレ",
    "川崎フロンターレ": "川崎フロンターレ",

    "横浜fm": "横浜fマリノス",
    "横浜fマリノス": "横浜fマリノス",

    "fc東京": "fc東京",
    "g大阪": "g大阪",
}


def norm_text(x: object) -> str:
    x = unicodedata.normalize(
        "NFKC",
        str(x),
    )

    x = x.translate(
        str.maketrans({
            "髙": "高",
            "﨑": "崎",
            "德": "徳",
            "濵": "濱",
        })
    )

    x = re.sub(
        r"[\s　・･·\.\-]",
        "",
        x,
    )

    return x.lower()


def norm_team(x: object) -> str:
    n = norm_text(x)
    return TEAM_ALIASES.get(
        n,
        n,
    )


def parse_player(
    raw: object,
) -> tuple[str, str]:

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


def clean_list(
    value: object,
) -> str:

    if not isinstance(
        value,
        list,
    ):
        return ""

    return "、".join(
        str(x).strip()
        for x in value
        if str(x).strip()
    )


def fetch_match(
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

    if body.get("errors"):
        raise RuntimeError(
            f"GraphQL error "
            f"match={match_id}: "
            f'{body["errors"]}'
        )

    rec = (
        body.get("data", {})
        .get("match")
    )

    if not rec:
        raise RuntimeError(
            f"match missing: {match_id}"
        )

    return body


def load_target_card() -> pd.DataFrame:

    con = sqlite3.connect(DB)

    q = """
    SELECT
        t.round_no,
        t.match_no,
        t.home_team,
        t.away_team,
        t.jleague_match_id,
        j.competition
    FROM toto_matches t
    JOIN jleague_matches j
      ON j.jleague_match_id =
         t.jleague_match_id
    WHERE
        t.round_no IN (1644,1645,1647)
    ORDER BY
        t.round_no,
        t.match_no
    """

    df = pd.read_sql_query(
        q,
        con,
    )

    con.close()

    if len(df) != 39:
        raise RuntimeError(
            "expected 39 toto matches, "
            f"got {len(df)}"
        )

    return df


def validate_card(
    round_no: int,
    match_no: int,
    gql_home: str,
    gql_away: str,
    db_row: pd.Series,
) -> None:

    gh = norm_team(gql_home)
    ga = norm_team(gql_away)

    dh = norm_team(
        db_row["home_team"]
    )

    da = norm_team(
        db_row["away_team"]
    )

    if gh != dh or ga != da:
        raise RuntimeError(
            "CARD MISMATCH: "
            f"{round_no} No{match_no:02d} "
            f"GraphQL={gql_home}-{gql_away} "
            f"DB={db_row['home_team']}-"
            f"{db_row['away_team']}"
        )


def compare_1645_archive(
    fresh: pd.DataFrame,
) -> None:

    if not ARCHIVE_1645.exists():
        raise RuntimeError(
            f"archive missing: "
            f"{ARCHIVE_1645}"
        )

    old = pd.read_csv(
        ARCHIVE_1645,
        low_memory=False,
    )

    old = old[
        old["match_no"].between(
            1,
            9,
        )
    ].copy()

    fresh = fresh[
        (
            fresh["toto_round"]
            == 1645
        )
        &
        (
            fresh["competition"]
            == "Ｊ１"
        )
    ].copy()

    if len(old) != 198:
        raise RuntimeError(
            "1645 archive J1 rows "
            f"!= 198: {len(old)}"
        )

    if len(fresh) != 198:
        raise RuntimeError(
            "1645 fresh J1 rows "
            f"!= 198: {len(fresh)}"
        )

    old["_norm"] = (
        old["totoone_player_name"]
        .map(norm_text)
    )

    fresh["_norm"] = (
        fresh["player_name"]
        .map(norm_text)
    )

    position_same = 0
    xi_set_same = 0

    audits = []

    for match_no in range(
        1,
        10,
    ):
        for side in [
            "home",
            "away",
        ]:

            a = old[
                (
                    old["match_no"]
                    == match_no
                )
                &
                (
                    old["side"]
                    == side
                )
            ].sort_values(
                "lineup_order"
            )

            b = fresh[
                (
                    fresh["match_no"]
                    == match_no
                )
                &
                (
                    fresh["side"]
                    == side
                )
            ].sort_values(
                "lineup_order"
            )

            if len(a) != 11 or len(b) != 11:
                raise RuntimeError(
                    "1645 XI count error: "
                    f"No{match_no} {side}"
                )

            same_pos = (
                a["_norm"].tolist()
                ==
                b["_norm"].tolist()
            )

            same_set = (
                set(a["_norm"])
                ==
                set(b["_norm"])
            )

            position_same += int(
                same_pos
            )

            xi_set_same += int(
                same_set
            )

            audits.append({
                "match_no":
                    match_no,

                "side":
                    side,

                "archive_team":
                    a["team"].iloc[0],

                "fresh_team":
                    b["team"].iloc[0],

                "same_position_order":
                    int(same_pos),

                "same_xi_set":
                    int(same_set),
            })

    # player/order level = 198/198
    merged = old[
        [
            "match_no",
            "side",
            "lineup_order",
            "_norm",
        ]
    ].merge(
        fresh[
            [
                "match_no",
                "side",
                "lineup_order",
                "_norm",
            ]
        ],
        on=[
            "match_no",
            "side",
            "lineup_order",
        ],
        suffixes=(
            "_archive",
            "_fresh",
        ),
        how="inner",
    )

    row_same = int(
        (
            merged["_norm_archive"]
            ==
            merged["_norm_fresh"]
        ).sum()
    )

    print()
    print(
        "========== 1645 ARCHIVE VALIDATION =========="
    )

    print(
        "player/order same:",
        row_same,
        "/ 198",
    )

    print(
        "team XI sets same:",
        xi_set_same,
        "/ 18",
    )

    print(
        "team order same:",
        position_same,
        "/ 18",
    )

    if row_same != 198:
        bad = merged[
            merged["_norm_archive"]
            != merged["_norm_fresh"]
        ]

        print(
            bad.to_string(
                index=False
            )
        )

        raise RuntimeError(
            "1645 archive player/order "
            "validation failed"
        )

    if xi_set_same != 18:
        raise RuntimeError(
            "1645 archive XI-set "
            "validation failed"
        )


def main() -> None:

    card = load_target_card()

    session = requests.Session()

    session.headers.update({
        "User-Agent":
            "Mozilla/5.0",
    })

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
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    raw_dir = Path(
        "data/raw/totoone/"
        f"historical_1644_1645_1647_"
        f"{stamp}_v1"
    )

    out_file = Path(
        "data/players/"
        "totoone_historical_"
        "1644_1645_1647_"
        f"predicted_lineups_{stamp}_v1.csv"
    )

    audit_file = Path(
        "data/evaluation/"
        "totoone_historical_"
        "1644_1645_1647_"
        f"fetch_audit_{stamp}_v1.csv"
    )

    for p in [
        raw_dir,
        out_file,
        audit_file,
    ]:
        if p.exists():
            raise RuntimeError(
                f"refusing overwrite: {p}"
            )

    raw_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    rows = []
    audits = []

    print(
        "========== FETCH HISTORICAL TOTOONE =========="
    )

    for round_no in [
        1644,
        1645,
        1647,
    ]:

        ids = ROUND_MATCH_IDS[
            round_no
        ]

        if len(ids) != 13:
            raise RuntimeError(
                f"{round_no}: IDs != 13"
            )

        print()
        print(
            f"========== ROUND {round_no} =========="
        )

        rc = card[
            card["round_no"]
            == round_no
        ]

        if len(rc) != 13:
            raise RuntimeError(
                f"{round_no}: DB card != 13"
            )

        for match_no, mid in enumerate(
            ids,
            start=1,
        ):

            db_hit = rc[
                rc["match_no"]
                == match_no
            ]

            if len(db_hit) != 1:
                raise RuntimeError(
                    f"{round_no} "
                    f"No{match_no}: DB row error"
                )

            db_row = db_hit.iloc[0]

            body = fetch_match(
                session,
                mid,
            )

            raw_file = (
                raw_dir
                / (
                    f"round{round_no}_"
                    f"no{match_no:02d}_"
                    f"{mid}.json"
                )
            )

            raw_file.write_text(
                json.dumps(
                    body,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rec = (
                body["data"]["match"]
            )

            home = str(
                rec["homeTeam"][
                    "shortName"
                ]
            ).strip()

            away = str(
                rec["awayTeam"][
                    "shortName"
                ]
            ).strip()

            validate_card(
                round_no,
                match_no,
                home,
                away,
                db_row,
            )

            counts = {}

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
                    rec.get(
                        detail_key
                    )
                    or {}
                )

                members = (
                    detail.get(
                        "startingMember"
                    )
                    or []
                )

                counts[side] = len(
                    members
                )

                if len(members) != 11:
                    raise RuntimeError(
                        f"{round_no} "
                        f"No{match_no:02d} "
                        f"{team}: "
                        f"starter count="
                        f"{len(members)}"
                    )

                if len(
                    {
                        norm_text(x)
                        for x in members
                    }
                ) != 11:
                    raise RuntimeError(
                        f"{round_no} "
                        f"No{match_no:02d} "
                        f"{team}: duplicate XI"
                    )

                formation = (
                    detail.get(
                        "formation"
                    )
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

                for order, raw_player in enumerate(
                    members,
                    start=1,
                ):

                    shirt, name = (
                        parse_player(
                            raw_player
                        )
                    )

                    rows.append({
                        "toto_round":
                            round_no,

                        "match_no":
                            match_no,

                        "totoone_match_id":
                            mid,

                        "jleague_match_id":
                            int(
                                db_row[
                                    "jleague_match_id"
                                ]
                            ),

                        "competition":
                            db_row[
                                "competition"
                            ],

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
                            shirt,

                        "player_name":
                            name,

                        "normalized_name":
                            norm_text(
                                name
                            ),

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

                        "raw_json_path":
                            str(
                                raw_file
                            ),
                    })

            print(
                f"{round_no} "
                f"No{match_no:02d} "
                f"{home}-{away} "
                f'{counts["home"]}/'
                f'{counts["away"]} '
                f'league='
                f'{db_row["competition"]}'
            )

            audits.append({
                "toto_round":
                    round_no,

                "match_no":
                    match_no,

                "totoone_match_id":
                    mid,

                "jleague_match_id":
                    int(
                        db_row[
                            "jleague_match_id"
                        ]
                    ),

                "competition":
                    db_row[
                        "competition"
                    ],

                "home":
                    home,

                "away":
                    away,

                "home_starters":
                    counts["home"],

                "away_starters":
                    counts["away"],
            })

    out = pd.DataFrame(
        rows
    )

    audit = pd.DataFrame(
        audits
    )

    # 39 matches × 22
    if len(out) != 858:
        raise RuntimeError(
            "expected 858 starter rows, "
            f"got {len(out)}"
        )

    if len(audit) != 39:
        raise RuntimeError(
            "expected 39 match rows, "
            f"got {len(audit)}"
        )

    j1 = out[
        out["competition"]
        == "Ｊ１"
    ]

    if len(j1) != 528:
        raise RuntimeError(
            "expected 528 J1 starter rows, "
            f"got {len(j1)}"
        )

    # strongest historical integrity check
    compare_1645_archive(
        out
    )

    out_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    out.to_csv(
        out_file,
        index=False,
        encoding="utf-8-sig",
    )

    audit.to_csv(
        audit_file,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print(
        "========== FINAL VALIDATION =========="
    )

    print(
        "matches:",
        len(audit),
        "/ 39",
    )

    print(
        "all starter rows:",
        len(out),
        "/ 858",
    )

    print(
        "J1 starter rows:",
        len(j1),
        "/ 528",
    )

    print()

    print(
        j1.groupby(
            "toto_round"
        )
        .size()
        .to_string()
    )

    print()
    print(
        "========== SAVED =========="
    )

    print(out_file)
    print(audit_file)
    print(raw_dir)


if __name__ == "__main__":
    main()
