# -*- coding: utf-8 -*-

"""
Project AKAMURASAKI

File:
    parse_footystats_match.py

Purpose:
    保存済みFootyStatsの試合・H2Hページを解析し、
    ページ基本情報、試合日、対戦チーム、
    比較統計テーブルをJSONへ保存する。

Notes:
    - DBへの書き込みは行わない。
    - 試合日は本文の「YYYY年M月D日」から取得する。
    - season_yearは原則として試合日の年を使用する。
    - Premium限定セルはlocked=trueとして保存する。
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_HTML_PATH = (
    PROJECT_ROOT
    / "data/raw/footystats/matches/2026/"
    "kataller_toyama_vs_vanraure_hachinohe.html"
)

DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data/parsed/footystats/matches/2026"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStats試合ページを解析して、"
            "JSONへ保存します。"
        )
    )

    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help=(
            "解析対象HTML。省略時: "
            f"{DEFAULT_HTML_PATH}"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "出力JSONパス。省略時は"
            "data/parsed/footystats/matches/2026/"
            "へ保存します。"
        ),
    )

    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


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


def clean_text(
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


def tag_text(
    tag: Tag | None,
) -> str | None:
    if tag is None:
        return None

    return clean_text(
        tag.get_text(
            " ",
            strip=True,
        )
    )


def extract_canonical_url(
    soup: BeautifulSoup,
) -> str | None:
    link = soup.find(
        "link",
        rel="canonical",
    )

    if not isinstance(link, Tag):
        return None

    href = link.get("href")

    if not isinstance(href, str):
        return None

    return href.strip() or None


def extract_page_title(
    soup: BeautifulSoup,
) -> str | None:
    if soup.title is None:
        return None

    return tag_text(
        soup.title
    )


def extract_meta_description(
    soup: BeautifulSoup,
) -> str | None:
    tag = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    if not isinstance(tag, Tag):
        return None

    content = tag.get("content")

    if not isinstance(content, str):
        return None

    return clean_text(content)


def extract_league_name(
    soup: BeautifulSoup,
) -> str | None:
    description = extract_meta_description(
        soup
    )

    if description:
        match = re.search(
            r"([^。、]+リーグ)での成績",
            description,
        )

        if match is not None:
            return clean_text(
                match.group(1)
            )

    page_text = soup.get_text(
        " ",
        strip=True,
    )

    match = re.search(
        r"(J[123]リーグ)",
        page_text,
    )

    if match is not None:
        return match.group(1)

    return None


def extract_match_analysis(
    soup: BeautifulSoup,
) -> str | None:
    articles = soup.select(
        "article.stat-article"
    )

    for article in articles:
        if not isinstance(article, Tag):
            continue

        heading = article.find(
            ["h1", "h2", "h3", "h4"]
        )

        heading_text = tag_text(
            heading
        )

        paragraphs = article.find_all("p")

        for paragraph in paragraphs:
            if not isinstance(paragraph, Tag):
                continue

            paragraph_text = tag_text(
                paragraph
            )

            if not paragraph_text:
                continue

            if (
                heading_text
                and "試合分析" in heading_text
            ):
                return paragraph_text

            if (
                "過去数シーズン" in paragraph_text
                or re.search(
                    r"20\d{2}年\d{1,2}月\d{1,2}日",
                    paragraph_text,
                )
            ):
                return paragraph_text

    return None


def parse_japanese_date(
    text: str | None,
) -> str | None:
    if not text:
        return None

    match = re.search(
        r"(20\d{2})年"
        r"\s*(\d{1,2})月"
        r"\s*(\d{1,2})日",
        text,
    )

    if match is None:
        return None

    year = int(
        match.group(1)
    )
    month = int(
        match.group(2)
    )
    day = int(
        match.group(3)
    )

    try:
        return date(
            year,
            month,
            day,
        ).isoformat()
    except ValueError:
        return None


def extract_match_date(
    soup: BeautifulSoup,
    analysis_text: str | None,
) -> str | None:
    # FootyStats英語版では、メイン試合情報に
    # schema.org/SportsEventのstartDateが入る。
    # 過去H2H一覧の日付より先に、必ずこちらを優先する。
    start_date = soup.find(
        attrs={
            "itemprop": "startDate",
        }
    )

    if start_date is not None:
        content = start_date.get(
            "content"
        )

        if isinstance(content, str):
            match = re.match(
                r"(\d{4}-\d{2}-\d{2})",
                content.strip(),
            )

            if match is not None:
                return match.group(1)

    # 一部ページではtime要素のdatetimeに入る。
    main_time = soup.select_one(
        ".match-infodropdown "
        "time[datetime]"
    )

    if main_time is not None:
        datetime_value = main_time.get(
            "datetime"
        )

        if isinstance(
            datetime_value,
            str,
        ):
            match = re.match(
                r"(\d{4}-\d{2}-\d{2})",
                datetime_value.strip(),
            )

            if match is not None:
                return match.group(1)

    match_date = parse_japanese_date(
        analysis_text
    )

    if match_date:
        return match_date

    page_text = soup.get_text(
        " ",
        strip=True,
    )

    return parse_japanese_date(
        page_text
    )


def extract_season_year(
    match_date: str | None,
    soup: BeautifulSoup,
) -> int | None:
    if match_date:
        return int(
            match_date[:4]
        )

    page_text = soup.get_text(
        " ",
        strip=True,
    )

    explicit_patterns = (
        r"(20\d{2})シーズン",
        r"(20\d{2})年シーズン",
        r"(20\d{2})年度",
    )

    for pattern in explicit_patterns:
        match = re.search(
            pattern,
            page_text,
        )

        if match is not None:
            return int(
                match.group(1)
            )

    return None


def extract_team_id_from_url(
    href: str | None,
) -> int | None:
    if not href:
        return None

    parsed = urlparse(
        href
    )

    match = re.search(
        r"/clubs/[^/?#]+-(\d+)(?:/)?$",
        parsed.path,
    )

    if match is None:
        return None

    return int(
        match.group(1)
    )


def extract_team_reference(
    header: Tag,
) -> dict[str, Any]:
    link = header.find(
        "a",
        href=True,
    )

    if isinstance(link, Tag):
        href = link.get("href")

        if isinstance(href, str):
            return {
                "name": tag_text(link),
                "external_team_id": (
                    extract_team_id_from_url(
                        href
                    )
                ),
                "source_url": href,
            }

    return {
        "name": tag_text(header),
        "external_team_id": None,
        "source_url": None,
    }


def extract_primary_teams(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    counts: dict[
        int,
        dict[str, Any],
    ] = {}

    links = soup.select(
        "table.comparison-table-table "
        'thead a[href*="/clubs/"]'
    )

    for link in links:
        if not isinstance(link, Tag):
            continue

        href = link.get("href")

        if not isinstance(href, str):
            continue

        external_team_id = (
            extract_team_id_from_url(
                href
            )
        )

        if external_team_id is None:
            continue

        team_name = tag_text(
            link
        )

        item = counts.setdefault(
            external_team_id,
            {
                "external_team_id": (
                    external_team_id
                ),
                "team_name": team_name,
                "source_url": href,
                "occurrences": 0,
            },
        )

        item["occurrences"] += 1

        if not item.get(
            "team_name"
        ) and team_name:
            item["team_name"] = (
                team_name
            )

    ordered = sorted(
        counts.values(),
        key=lambda item: (
            -int(item["occurrences"]),
            int(item["external_team_id"]),
        ),
    )

    return ordered[:2]


def find_section_title(
    table: Tag,
) -> str | None:
    section = table.find_parent(
        "section"
    )

    if not isinstance(
        section,
        Tag,
    ):
        return None

    heading = section.find(
        ["h1", "h2", "h3", "h4"]
    )

    return tag_text(
        heading
    )


def extract_table_headers(
    table: Tag,
) -> list[dict[str, Any]]:
    header_row = table.select_one(
        "thead tr"
    )

    if header_row is None:
        header_row = table.find(
            "tr"
        )

    if not isinstance(
        header_row,
        Tag,
    ):
        return []

    headers: list[
        dict[str, Any]
    ] = []

    cells = header_row.find_all(
        ["th", "td"],
        recursive=False,
    )

    for cell in cells:
        if not isinstance(
            cell,
            Tag,
        ):
            continue

        headers.append(
            extract_team_reference(
                cell
            )
        )

    return headers


def parse_numeric_value(
    text: str | None,
) -> dict[str, Any]:
    if text is None:
        return {
            "raw": None,
            "value": None,
            "unit": None,
        }

    compact = text.replace(
        ",",
        "",
    ).strip()

    percentage_match = re.fullmatch(
        r"(-?\d+(?:\.\d+)?)\s*%",
        compact,
    )

    if percentage_match is not None:
        return {
            "raw": text,
            "value": float(
                percentage_match.group(1)
            ),
            "unit": "percent",
        }

    numeric_match = re.fullmatch(
        r"-?\d+(?:\.\d+)?",
        compact,
    )

    if numeric_match is not None:
        value = float(
            compact
        )

        normalized: int | float

        if value.is_integer():
            normalized = int(
                value
            )
        else:
            normalized = value

        return {
            "raw": text,
            "value": normalized,
            "unit": "number",
        }

    fraction_match = re.fullmatch(
        r"(\d+)\s*試合\s*/\s*"
        r"(\d+)\s*試合",
        compact,
    )

    if fraction_match is not None:
        return {
            "raw": text,
            "value": {
                "numerator": int(
                    fraction_match.group(1)
                ),
                "denominator": int(
                    fraction_match.group(2)
                ),
            },
            "unit": "fraction",
        }

    return {
        "raw": text,
        "value": None,
        "unit": "text",
    }


def parse_data_cell(
    cell: Tag,
) -> dict[str, Any]:
    class_names = {
        str(value)
        for value in cell.get(
            "class",
            [],
        )
    }

    locked = (
        "locked" in class_names
        or cell.select_one(
            ".fa-lock"
        ) is not None
    )

    text = tag_text(
        cell
    )

    parsed = parse_numeric_value(
        text
    )

    return {
        "raw": parsed["raw"],
        "value": (
            None
            if locked
            else parsed["value"]
        ),
        "unit": (
            "locked"
            if locked
            else parsed["unit"]
        ),
        "locked": locked,
        "classes": sorted(
            class_names
        ),
    }


def extract_table_rows(
    table: Tag,
) -> list[dict[str, Any]]:
    body_rows = table.select(
        "tbody tr"
    )

    if not body_rows:
        body_rows = table.find_all(
            "tr",
            recursive=True,
        )

    rows: list[
        dict[str, Any]
    ] = []

    for row_index, row in enumerate(
        body_rows,
        start=1,
    ):
        if row.find("th") is not None:
            continue

        cells = row.find_all(
            ["th", "td"],
            recursive=False,
        )

        if len(cells) < 2:
            continue

        metric = tag_text(
            cells[0]
        )

        if not metric:
            continue

        values = [
            parse_data_cell(cell)
            for cell in cells[1:]
            if isinstance(cell, Tag)
        ]

        rows.append(
            {
                "row_index": row_index,
                "metric": metric,
                "values": values,
            }
        )

    return rows


def extract_tables(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    parsed_tables: list[
        dict[str, Any]
    ] = []

    tables = soup.select(
        "table.comparison-table-table"
    )

    for table_index, table in enumerate(
        tables,
        start=1,
    ):
        if not isinstance(
            table,
            Tag,
        ):
            continue

        headers = extract_table_headers(
            table
        )

        rows = extract_table_rows(
            table
        )

        parsed_tables.append(
            {
                "table_index": table_index,
                "section_title": (
                    find_section_title(
                        table
                    )
                ),
                "table_title": (
                    headers[0]["name"]
                    if headers
                    else None
                ),
                "column_count": len(
                    headers
                ),
                "row_count": len(
                    rows
                ),
                "columns": headers,
                "rows": rows,
            }
        )

    return parsed_tables


def parse_match_analysis_values(
    analysis_text: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "historical_match_count": None,
        "historical_average_goals": None,
        "historical_btts_percent": None,
        "home_ppg": None,
        "away_ppg": None,
    }

    if not analysis_text:
        return result

    match_count = re.search(
        r"過去数シーズンで"
        r"\s*(\d+)\s*回",
        analysis_text,
    )

    if match_count is not None:
        result[
            "historical_match_count"
        ] = int(
            match_count.group(1)
        )

    average_goals = re.search(
        r"平均ゴール数は"
        r"\s*(\d+(?:\.\d+)?)",
        analysis_text,
    )

    if average_goals is not None:
        result[
            "historical_average_goals"
        ] = float(
            average_goals.group(1)
        )

    btts = re.search(
        r"両チーム得点は"
        r"\s*(\d+(?:\.\d+)?)%",
        analysis_text,
    )

    if btts is not None:
        result[
            "historical_btts_percent"
        ] = float(
            btts.group(1)
        )

    ppg_values = re.findall(
        r"平均勝ち点"
        r"\s*(\d+(?:\.\d+)?)",
        analysis_text,
    )

    if len(ppg_values) >= 1:
        result["home_ppg"] = float(
            ppg_values[0]
        )

    if len(ppg_values) >= 2:
        result["away_ppg"] = float(
            ppg_values[1]
        )

    return result


def build_result(
    html_path: Path,
    html: str,
) -> dict[str, Any]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    analysis_text = extract_match_analysis(
        soup
    )

    match_date = extract_match_date(
        soup=soup,
        analysis_text=analysis_text,
    )

    tables = extract_tables(
        soup
    )

    locked_value_count = 0
    public_value_count = 0

    for table in tables:
        for row in table["rows"]:
            for value in row["values"]:
                if value["locked"]:
                    locked_value_count += 1
                else:
                    public_value_count += 1

    return {
        "source_name": "footystats",
        "page_type": "match_h2h",
        "source_file": str(
            html_path
        ),
        "canonical_url": (
            extract_canonical_url(
                soup
            )
        ),
        "page_title": (
            extract_page_title(
                soup
            )
        ),
        "description": (
            extract_meta_description(
                soup
            )
        ),
        "league_name": (
            extract_league_name(
                soup
            )
        ),
        "match_date": match_date,
        "season_year": (
            extract_season_year(
                match_date=match_date,
                soup=soup,
            )
        ),
        "primary_teams": (
            extract_primary_teams(
                soup
            )
        ),
        "match_analysis_text": (
            analysis_text
        ),
        "match_analysis_values": (
            parse_match_analysis_values(
                analysis_text
            )
        ),
        "table_count": len(
            tables
        ),
        "metric_row_count": sum(
            table["row_count"]
            for table in tables
        ),
        "public_value_count": (
            public_value_count
        ),
        "locked_value_count": (
            locked_value_count
        ),
        "tables": tables,
    }


def default_output_path(
    html_path: Path,
) -> Path:
    return (
        DEFAULT_OUTPUT_DIR
        / f"{html_path.stem}.json"
    )


def write_json(
    result: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def display_path(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
    except ValueError:
        return str(
            path
        )


def print_summary(
    result: dict[str, Any],
    output_path: Path,
) -> None:
    print("=" * 100)
    print(
        "FootyStats Match HTML Parser"
    )
    print("=" * 100)

    print(
        f"source_file        : "
        f"{display_path(Path(result['source_file']))}"
    )
    print(
        f"page_title         : "
        f"{result['page_title']}"
    )
    print(
        f"league_name        : "
        f"{result['league_name']}"
    )
    print(
        f"match_date         : "
        f"{result['match_date']}"
    )
    print(
        f"season_year        : "
        f"{result['season_year']}"
    )
    print(
        f"primary_teams      : "
        f"{result['primary_teams']}"
    )
    print(
        f"table_count        : "
        f"{result['table_count']}"
    )
    print(
        f"metric_row_count   : "
        f"{result['metric_row_count']}"
    )
    print(
        f"public_values      : "
        f"{result['public_value_count']}"
    )
    print(
        f"locked_values      : "
        f"{result['locked_value_count']}"
    )
    print(
        f"output_json        : "
        f"{display_path(output_path)}"
    )

    print()
    print("TABLE SAMPLE")
    print("-" * 100)

    for table in result["tables"][:5]:
        print(
            f"[{table['table_index']:02d}] "
            f"{table['section_title']} / "
            f"{table['table_title']} "
            f"({table['row_count']} rows)"
        )

        for row in table["rows"][:3]:
            raw_values = [
                value["raw"]
                for value in row["values"]
            ]

            print(
                f"     {row['metric']} "
                f"-> {raw_values}"
            )


def main() -> None:
    args = parse_args()

    html_path = resolve_path(
        args.html_path
    )

    output_path = (
        resolve_path(
            args.output
        )
        if args.output is not None
        else default_output_path(
            html_path
        )
    )

    html = read_html(
        html_path
    )

    result = build_result(
        html_path=html_path,
        html=html,
    )

    write_json(
        result=result,
        output_path=output_path,
    )

    print_summary(
        result=result,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
