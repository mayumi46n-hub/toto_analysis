# -*- coding: utf-8 -*-

"""
totoLABO

File:
    parse_footystats_team.py

Version:
    3.0

Updated:
    2026-07-18

Purpose:
    保存済みFootyStatsクラブHTMLから、以下を抽出する。

    - クラブ基本情報
    - FootyStatsクラブID
    - シーズン
    - 埋め込み試合データ
    - 各試合のホーム・アウェイチーム名
    - FootyStats外部チームIDとチーム名の対応表

Important:
    このParserはDBへ書き込まない。
    HTMLをPython辞書へ変換することだけを担当する。
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag


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
            f"ファイルではありません: {path}"
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

    cleaned_json = clean_javascript_json(
        match.group(1)
    )

    try:
        data = json.loads(
            cleaned_json
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "mh_matchDataのJSON解析に失敗しました。"
            f" 位置={exc.pos}, 理由={exc.msg}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            "mh_matchDataが配列ではありません"
        )

    return [
        normalize_match_record(record)
        for record in data
        if isinstance(record, dict)
    ]


def unix_to_iso(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        timestamp = int(value)
    except (TypeError, ValueError):
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
    if isinstance(value, list):
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
        "home_team_name": None,
        "away_team_name": None,
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


def clean_team_name(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    return cleaned or None


def extract_team_name_from_container(
    container: Tag | None,
) -> str | None:
    if container is None:
        return None

    paragraph = container.find("p")

    if paragraph is not None:
        return clean_team_name(
            paragraph.get_text(
                " ",
                strip=True,
            )
        )

    return clean_team_name(
        container.get_text(
            " ",
            strip=True,
        )
    )


def extract_match_name_pairs(
    soup: BeautifulSoup,
) -> list[dict[str, str | None]]:
    history = soup.find(
        id="matchHistoryList"
    )

    if history is None:
        return []

    pairs: list[
        dict[str, str | None]
    ] = []

    list_items = history.find_all(
        "li",
        recursive=False,
    )

    for item in list_items:
        if not isinstance(item, Tag):
            continue

        home_container = item.find(
            attrs={
                "itemprop": "homeTeam",
            }
        )

        away_container = item.find(
            attrs={
                "itemprop": "awayTeam",
            }
        )

        home_name = extract_team_name_from_container(
            home_container
        )

        away_name = extract_team_name_from_container(
            away_container
        )

        if (
            home_name is None
            and away_name is None
        ):
            continue

        pairs.append(
            {
                "home_team_name": home_name,
                "away_team_name": away_name,
            }
        )

    if pairs:
        return pairs

    # 保存形式によってli構造を正常に読めない場合の代替処理
    name_elements = history.find_all(
        attrs={
            "itemprop": "name",
        }
    )

    for element in name_elements:
        if not isinstance(element, Tag):
            continue

        paragraphs = element.find_all("p")

        if len(paragraphs) < 2:
            continue

        home_name = clean_team_name(
            paragraphs[0].get_text(
                " ",
                strip=True,
            )
        )

        away_name = clean_team_name(
            paragraphs[1].get_text(
                " ",
                strip=True,
            )
        )

        pairs.append(
            {
                "home_team_name": home_name,
                "away_team_name": away_name,
            }
        )

    return pairs


def attach_match_names(
    matches: list[dict[str, Any]],
    name_pairs: list[dict[str, str | None]],
) -> dict[str, Any]:
    attached_count = min(
        len(matches),
        len(name_pairs),
    )

    for index in range(
        attached_count
    ):
        matches[index]["home_team_name"] = (
            name_pairs[index].get(
                "home_team_name"
            )
        )

        matches[index]["away_team_name"] = (
            name_pairs[index].get(
                "away_team_name"
            )
        )

    return {
        "match_data_count": len(matches),
        "name_pair_count": len(name_pairs),
        "attached_count": attached_count,
        "counts_match": (
            len(matches) == len(name_pairs)
        ),
    }


def build_external_team_map(
    matches: list[dict[str, Any]],
    subject_team_id: int | None,
    subject_team_name: str | None,
) -> list[dict[str, Any]]:
    mapping: dict[int, str | None] = {}

    if subject_team_id is not None:
        mapping[subject_team_id] = (
            subject_team_name
        )

    for match in matches:
        home_id = match.get(
            "home_team_external_id"
        )
        away_id = match.get(
            "away_team_external_id"
        )

        home_name = match.get(
            "home_team_name"
        )
        away_name = match.get(
            "away_team_name"
        )

        if isinstance(home_id, int):
            current_name = mapping.get(
                home_id
            )

            if current_name is None and home_name:
                mapping[home_id] = str(
                    home_name
                )
            elif home_id not in mapping:
                mapping[home_id] = (
                    str(home_name)
                    if home_name
                    else None
                )

        if isinstance(away_id, int):
            current_name = mapping.get(
                away_id
            )

            if current_name is None and away_name:
                mapping[away_id] = str(
                    away_name
                )
            elif away_id not in mapping:
                mapping[away_id] = (
                    str(away_name)
                    if away_name
                    else None
                )

    return [
        {
            "external_team_id": external_id,
            "team_name": mapping[external_id],
        }
        for external_id in sorted(mapping)
    ]


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

    team_name = extract_team_name(
        soup
    )

    external_team_id = (
        extract_footystats_team_id(
            html,
            html_path,
        )
    )

    season_label = extract_season_label(
        soup
    )

    matches = extract_match_data(
        html
    )

    name_pairs = extract_match_name_pairs(
        soup
    )

    match_name_alignment = attach_match_names(
        matches,
        name_pairs,
    )

    external_team_map = build_external_team_map(
        matches=matches,
        subject_team_id=external_team_id,
        subject_team_name=team_name,
    )

    return {
        "source": "footystats",
        "source_file": str(
            html_path
        ),
        "page_form": extract_page_form(
            html
        ),
        "team_name": team_name,
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
        "footystats_team_id": external_team_id,
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
        "match_name_alignment": (
            match_name_alignment
        ),
        "external_team_count": len(
            external_team_map
        ),
        "external_team_map": (
            external_team_map
        ),
        "matches": matches,
    }


def print_field(
    label: str,
    value: Any,
) -> None:
    print(
        f"{label:<25}: {value}"
    )


def print_external_team_map(
    team_map: list[dict[str, Any]],
) -> None:
    print()
    print("EXTERNAL TEAM MAP")
    print("-" * 100)

    if not team_map:
        print(
            "No external team mapping found."
        )
        return

    for item in team_map:
        external_id = item.get(
            "external_team_id"
        )

        team_name = item.get(
            "team_name"
        )

        print(
            f"{external_id:<10}"
            f" -> {team_name}"
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
            f"id={match['footystats_match_id']} "
            f"home={match['home_team_external_id']} "
            f"({match['home_team_name']}) "
            f"away={match['away_team_external_id']} "
            f"({match['away_team_name']}) "
            f"status={match['status']} "
            f"date={match['scheduled_at_utc']}"
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
    print_field(
        "match_name_alignment",
        result["match_name_alignment"],
    )
    print_field(
        "external_team_count",
        result["external_team_count"],
    )

    print_external_team_map(
        result["external_team_map"]
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