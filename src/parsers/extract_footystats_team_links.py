# -*- coding: utf-8 -*-

"""
totoLABO

File:
    extract_footystats_team_links.py

Version:
    1.0

Purpose:
    保存済みFootyStatsクラブHTMLに含まれるクラブページリンクから、
    FootyStats外部チームID・クラブ名・URLを抽出する。

Important:
    試合一覧の表示順とmh_matchDataの順番は使用しない。
    /clubs/<slug>-<team_id> のリンクそのものを情報源とする。
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag


DEFAULT_HTML_PATH = Path(
    "data/raw/footystats/2026/avispa_fukuoka_877.html"
)

DEFAULT_OUTPUT_PATH = Path(
    "data/master/footystats_team_candidates_2026.csv"
)

BASE_URL = "https://footystats.org"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStats HTMLから"
            "クラブIDとクラブ名を抽出します。"
        )
    )

    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help=f"入力HTML。省略時: {DEFAULT_HTML_PATH}",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"出力CSV。省略時: {DEFAULT_OUTPUT_PATH}",
    )

    return parser.parse_args()


def read_html(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"HTMLが見つかりません: {path}"
        )

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def extract_team_id(href: str) -> int | None:
    parsed = urlparse(href)

    match = re.search(
        r"/clubs/[^/?#]+-(\d+)(?:/)?$",
        parsed.path,
    )

    if match is None:
        return None

    return int(match.group(1))


def clean_team_name(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def extract_link_name(link: Tag) -> str | None:
    candidates: list[str] = []

    text = clean_team_name(
        link.get_text(
            " ",
            strip=True,
        )
    )

    if text:
        candidates.append(text)

    title = link.get("title")

    if isinstance(title, str):
        title = clean_team_name(title)

        if title:
            candidates.append(title)

    image = link.find("img")

    if isinstance(image, Tag):
        alt = image.get("alt")

        if isinstance(alt, str):
            alt = clean_team_name(alt)

            if alt:
                alt = re.sub(
                    r"\s+(Logo|Club Lineup|ロゴ|データ)$",
                    "",
                    alt,
                    flags=re.IGNORECASE,
                ).strip()

                if alt:
                    candidates.append(alt)

    for candidate in candidates:
        if candidate:
            return candidate

    return None


def extract_team_links(
    html: str,
) -> list[dict[str, object]]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    teams: dict[int, dict[str, object]] = {}

    for link in soup.find_all(
        "a",
        href=True,
    ):
        if not isinstance(link, Tag):
            continue

        href = link.get("href")

        if not isinstance(href, str):
            continue

        team_id = extract_team_id(href)

        if team_id is None:
            continue

        team_name = extract_link_name(link)

        absolute_url = urljoin(
            BASE_URL,
            href,
        )

        current = teams.get(team_id)

        if current is None:
            teams[team_id] = {
                "external_team_id": team_id,
                "team_name": team_name,
                "source_url": absolute_url,
            }
            continue

        if (
            not current.get("team_name")
            and team_name
        ):
            current["team_name"] = team_name

    return [
        teams[team_id]
        for team_id in sorted(teams)
    ]


def write_csv(
    rows: list[dict[str, object]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "external_team_id",
                "team_name",
                "source_url",
                "internal_team_id",
                "internal_short_name",
            ],
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "external_team_id": row[
                        "external_team_id"
                    ],
                    "team_name": (
                        row.get("team_name") or ""
                    ),
                    "source_url": row[
                        "source_url"
                    ],
                    "internal_team_id": "",
                    "internal_short_name": "",
                }
            )


def print_summary(
    rows: list[dict[str, object]],
    output_path: Path,
) -> None:
    print("=" * 100)
    print("FootyStats Team Link Extraction")
    print("=" * 100)

    print(f"抽出件数: {len(rows)}")
    print(f"CSV保存 : {output_path}")
    print()

    for row in rows:
        print(
            f"{row['external_team_id']:<8}"
            f" -> {row.get('team_name')}"
            f" | {row['source_url']}"
        )


def main() -> None:
    args = parse_args()

    html = read_html(
        args.html_path
    )

    rows = extract_team_links(
        html
    )

    write_csv(
        rows,
        args.output,
    )

    print_summary(
        rows,
        args.output,
    )


if __name__ == "__main__":
    main()
