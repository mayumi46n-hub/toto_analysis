# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from check_footystats_match_sides import (
    collect_team_candidates,
    extract_title_sides,
    resolve_side,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HTML_PATH = (
    PROJECT_ROOT
    / "data/raw/footystats/matches/2026/"
    "kataller_toyama_vs_vanraure_hachinohe.html"
)

JSON_PATH = (
    PROJECT_ROOT
    / "data/parsed/footystats/matches/2026/"
    "kataller_toyama_vs_vanraure_hachinohe.json"
)


def load_json() -> dict[str, Any]:
    if not JSON_PATH.exists():
        raise FileNotFoundError(
            f"JSONが見つかりません: {JSON_PATH}"
        )

    data = json.loads(
        JSON_PATH.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "JSONのルートが辞書ではありません"
        )

    return data


def write_json(
    data: dict[str, Any],
) -> None:
    temporary_path = JSON_PATH.with_suffix(
        ".json.tmp"
    )

    temporary_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(
        JSON_PATH
    )


def main() -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(
            f"HTMLが見つかりません: {HTML_PATH}"
        )

    html = HTML_PATH.read_text(
        encoding="utf-8",
        errors="replace",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    home_name, away_name = extract_title_sides(
        soup
    )

    candidates = collect_team_candidates(
        soup
    )

    home = resolve_side(
        home_name,
        candidates,
    )

    away = resolve_side(
        away_name,
        candidates,
    )

    if (
        home["external_team_id"]
        == away["external_team_id"]
    ):
        raise ValueError(
            "ホームとアウェイの外部IDが同一です"
        )

    data = load_json()

    data["home_team_name"] = home[
        "display_name"
    ]
    data["home_external_team_id"] = home[
        "external_team_id"
    ]
    data["home_source_url"] = home[
        "source_url"
    ]

    data["away_team_name"] = away[
        "display_name"
    ]
    data["away_external_team_id"] = away[
        "external_team_id"
    ]
    data["away_source_url"] = away[
        "source_url"
    ]

    data["side_resolution"] = {
        "method": "page_title_and_club_links",
        "home_match_score": home[
            "match_score"
        ],
        "away_match_score": away[
            "match_score"
        ],
    }

    write_json(
        data
    )

    print("=" * 100)
    print("FootyStats Match Side Enrichment")
    print("=" * 100)
    print(
        f"home_team_name         : "
        f"{data['home_team_name']}"
    )
    print(
        f"home_external_team_id  : "
        f"{data['home_external_team_id']}"
    )
    print(
        f"away_team_name         : "
        f"{data['away_team_name']}"
    )
    print(
        f"away_external_team_id  : "
        f"{data['away_external_team_id']}"
    )
    print(
        f"table_count            : "
        f"{data.get('table_count')}"
    )
    print(
        f"metric_row_count       : "
        f"{data.get('metric_row_count')}"
    )
    print(
        "json_updated           : "
        "data/parsed/footystats/matches/2026/"
        "kataller_toyama_vs_vanraure_hachinohe.json"
    )


if __name__ == "__main__":
    main()

