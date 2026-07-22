# -*- coding: utf-8 -*-

"""
totoLABO

File:
    parse_footystats_team.py

Version:
    2.0

Updated:
    2026-07-17

Purpose:
    保存済みのFootyStatsクラブHTMLから、
    チーム基本情報と埋め込み試合データを抽出する。

Input example:
    data/raw/footystats/2026/avispa_fukuoka_877.html

Output:
    標準出力へ解析結果を表示する。

Notes:
    - この段階ではSQLiteへ保存しない。
    - FootyStatsのmh_matchDataはJavaScript配列であり、
      配列末尾にカンマが付く場合がある。
    - 末尾カンマを除去してからJSONとして解析する。
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


DEFAULT_HTML_PATH = Path(
    "data/raw/footystats/2026/avispa_fukuoka_877.html"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStatsクラブHTMLを解析します。"
        )
    )

    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help=(
            "保存済みFootyStatsクラブHTMLのパス。"
            f"省略時: {DEFAULT_HTML_PATH}"
        ),
    )

    return parser.parse_args()


def read_html(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"HTMLが見つかりません: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"HTMLファイルではありません: {path}"
        )

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def build_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(
        html,
        "html.parser",
    )


def extract_page_form(
    html: str,
) -> str | None:
    match = re.search(
        r"var\s+page_form\s*=\s*['\"]([^'\"]+)['\"]",
        html,
    )

    if match is None:
        return None

    return match.group(1).strip()


def extract_team_name(
    soup: BeautifulSoup,
) -> str | None:
    heading = soup.find("h1")

    if heading is not None:
        text = heading.get_text(
            " ",
            strip=True,
        )

        if text:
            return text

    if soup.title is None:
        return None

    title = soup.title.get_text(
        " ",
        strip=True,
    )

    if "のスタッツ" in title:
        return title.split(
            "のスタッツ",
            maxsplit=1,
        )[0].strip()

    return title or None


def extract_value_from_label_row(
    soup: BeautifulSoup,
    label_text: str,
) -> str | None:
    label = soup.find(
        string=lambda value: (
            isinstance(value, str)
            and value.strip() == label_text
        )
    )

    if label is None:
        return None

    label_element = label.parent

    if label_element is None:
        return None

    row = label_element.parent

    if row is None:
        return None

    columns = row.find_all("p")

    if len(columns) < 2:
        return None

    value = columns[1].get_text(
        " ",
        strip=True,
    )

    return value or None


def extract_english_name(
    soup: BeautifulSoup,
) -> str | None:
    return extract_value_from_label_row(
        soup,
        "英語名",
    )


def extract_stadium(
    soup: BeautifulSoup,
) -> str | None:
    return extract_value_from_label_row(
        soup,
        "スタジアム",
    )


def extract_address(
    soup: BeautifulSoup,
) -> str | None:
    return extract_value_from_label_row(
        soup,
        "住所",
    )


def extract_country(
    soup: BeautifulSoup,
) -> str | None:
    return extract_value_from_label_row(
        soup,
        "国",
    )


def extract_official_site(
    soup: BeautifulSoup,
) -> str | None:
    label = soup.find(
        string=lambda value: (
            isinstance(value, str)
            and value.strip() == "オフィシャルサイト"
        )
    )

    if label is None:
        return None

    label_element = label.parent

    if label_element is None:
        return None

    row = label_element.parent

    if row is None:
        return None

    link = row.find(
        "a",
        href=True,
    )

    if link is None:
        return None

    href = link.get("href")

    if not isinstance(href, str):
        return None

    return href.strip() or None


def extract_footystats_team_id(
    html: str,
    html_path: Path,
) -> int | None:
    filename_match = re.search(
        r"_(\d+)$",
        html_path.stem,
    )

    if filename_match is not None:
        return int(
            filename_match.group(1)
        )

    url_match = re.search(
        r"/clubs/[^\"']+-(\d+)",
        html,
    )

    if url_match is not None:
        return int(
            url_match.group(1)
        )

    home_id_match = re.search(
        r'"matchHomeID"\s*:\s*(\d+)',
        html,
    )

    if home_id_match is not None:
        return int(
            home_id_match.group(1)
        )

    return None


def extract_season_label(
    soup: BeautifulSoup,
) -> str | None:
    page_text = soup.get_text(
        " ",
        strip=True,
    )

    match = re.search(
        r"(\d{4}/\d{2})年シーズン",
        page_text,
    )

    if match is None:
        return None

    return match.group(1)


def extract_season_start_year(
    season_label: str | None,
) -> int | None:
    if season_label is None:
        return None

    match = re.match(
        r"(\d{4})/",
        season_label,
    )

    if match is None:
        return None

    return int(
        match.group(1)
    )


def clean_javascript_json(
    raw_json: str,
) -> str:
    cleaned = raw_json.strip()

    # JavaScriptでは許可されるが、
    # JSONでは許可されない末尾カンマを除去する。
    cleaned = re.sub(
        r",\s*]",
        "]",
        cleaned,
    )

    cleaned = re.sub(
        r",\s*}",
        "}",
        cleaned,
    )

    return cleaned


def extract_match_data(
    html: str,
) -> list[dict[str, Any]]:
    match = re.search(
        r"var\s+mh_matchData\s*=\s*"
        r"(\[[\s\S]*?\])\s*;"
        r"\s*var\s+page_form",
        html,
    )

    if match is None:
        return []

    raw_json = match.group(1)

    cleaned_json = clean_javascript_json(
        raw_json
    )

    try:
        data = json.loads(
            cleaned_json
        )
    except json.JSONDecodeError as exc:
        context_start = max(
            0,
            exc.pos - 120,
        )
        context_end = min(
            len(cleaned_json),
            exc.pos + 120,
        )

        error_context = cleaned_json[
            context_start:context_end
        ]

        raise ValueError(
            "mh_matchDataのJSON解析に失敗しました。\n"
            f"位置: {exc.pos}\n"
            f"理由: {exc.msg}\n"
            f"周辺データ: {error_context}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            "mh_matchDataが配列ではありません"
        )

    normalized_matches: list[
        dict[str, Any]
    ] = []

    for record in data:
        if not isinstance(
            record,
            dict,
        ):
            continue

        normalized_matches.append(
            normalize_match_record(
                record
            )
        )

    return normalized_matches


def unix_to_iso(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    try:
        timestamp = int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    try:
        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).isoformat()
    except (
        OverflowError,
        OSError,
        ValueError,
    ):
        return None


def normalize_goal_list(
    value: Any,
) -> list[Any]:
    if isinstance(
        value,
        list,
    ):
        return value

    return []


def normalize_match_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "footystats_match_id": record.get(
            "id"
        ),
        "home_team_external_id": record.get(
            "matchHomeID"
        ),
        "away_team_external_id": record.get(
            "matchAwayID"
        ),
        "team_side": record.get(
            "teamIs"
        ),
        "status": record.get(
            "status"
        ),
        "scheduled_at_unix": record.get(
            "date"
        ),
        "scheduled_at_utc": unix_to_iso(
            record.get("date")
        ),
        "match_winner": record.get(
            "matchWinner"
        ),
        "home_goals": normalize_goal_list(
            record.get("homeGoals")
        ),
        "away_goals": normalize_goal_list(
            record.get("awayGoals")
        ),
        "goals": normalize_goal_list(
            record.get("goals")
        ),
    }


def count_match_statuses(
    matches: list[dict[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}

    for match in matches:
        status_value = match.get(
            "status"
        )

        status = (
            str(status_value)
            if status_value is not None
            else "unknown"
        )

        counts[status] = (
            counts.get(status, 0) + 1
        )

    return counts


def build_result(
    html_path: Path,
    html: str,
) -> dict[str, Any]:
    soup = build_soup(
        html
    )

    season_label = extract_season_label(
        soup
    )

    matches = extract_match_data(
        html
    )

    return {
        "source": "footystats",
        "source_file": str(
            html_path
        ),
        "page_form": extract_page_form(
            html
        ),
        "team_name": extract_team_name(
            soup
        ),
        "english_name": extract_english_name(
            soup
        ),
        "stadium": extract_stadium(
            soup
        ),
        "address": extract_address(
            soup
        ),
        "country": extract_country(
            soup
        ),
        "official_site": extract_official_site(
            soup
        ),
        "footystats_team_id": (
            extract_footystats_team_id(
                html,
                html_path,
            )
        ),
        "season_label": season_label,
        "season_start_year": (
            extract_season_start_year(
                season_label
            )
        ),
        "match_count": len(
            matches
        ),
        "match_status_counts": (
            count_match_statuses(
                matches
            )
        ),
        "matches": matches,
    }


def print_field(
    label: str,
    value: Any,
) -> None:
    print(
        f"{label:<24}: {value}"
    )


def print_match_sample(
    matches: list[dict[str, Any]],
    limit: int = 10,
) -> None:
    print()
    print("MATCH SAMPLE")
    print("-" * 100)

    if not matches:
        print(
            "No embedded match data found."
        )
        return

    for match in matches[:limit]:
        print(
            "id="
            f"{match['footystats_match_id']} "
            "home="
            f"{match['home_team_external_id']} "
            "away="
            f"{match['away_team_external_id']} "
            "side="
            f"{match['team_side']} "
            "status="
            f"{match['status']} "
            "date="
            f"{match['scheduled_at_utc']}"
        )


def print_summary(
    result: dict[str, Any],
) -> None:
    print("=" * 100)
    print(
        "FootyStats Team HTML Parser"
    )
    print("=" * 100)

    print_field(
        "source_file",
        result["source_file"],
    )
    print_field(
        "page_form",
        result["page_form"],
    )
    print_field(
        "team_name",
        result["team_name"],
    )
    print_field(
        "english_name",
        result["english_name"],
    )
    print_field(
        "stadium",
        result["stadium"],
    )
    print_field(
        "address",
        result["address"],
    )
    print_field(
        "country",
        result["country"],
    )
    print_field(
        "official_site",
        result["official_site"],
    )
    print_field(
        "footystats_team_id",
        result["footystats_team_id"],
    )
    print_field(
        "season_label",
        result["season_label"],
    )
    print_field(
        "season_start_year",
        result["season_start_year"],
    )
    print_field(
        "match_count",
        result["match_count"],
    )
    print_field(
        "match_status_counts",
        result["match_status_counts"],
    )

    print_match_sample(
        result["matches"],
        limit=10,
    )


def main() -> None:
    args = parse_args()

    html = read_html(
        args.html_path
    )

    result = build_result(
        html_path=args.html_path,
        html=html,
    )

    print_summary(
        result
    )


if __name__ == "__main__":
    main()