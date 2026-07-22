# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_HTML_PATH = (
    PROJECT_ROOT
    / "data/raw/footystats/2026/"
    "avispa_fukuoka_877.html"
)

DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data/master/"
    "footystats_match_candidates_2026.csv"
)

BASE_URL = "https://footystats.org"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStatsチームHTMLから"
            "試合・H2HページURLを抽出してCSV保存します。"
        )
    )

    parser.add_argument(
        "html_path",
        nargs="?",
        type=Path,
        default=DEFAULT_HTML_PATH,
        help="対象のFootyStatsチームHTML",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="出力CSVパス",
    )

    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def clean_text(value: str | None) -> str:
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def normalize_url(href: str) -> str:
    return urljoin(
        BASE_URL,
        href,
    )


def is_match_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.netloc not in {
        "footystats.org",
        "www.footystats.org",
    }:
        return False

    path = parsed.path.rstrip("/")

    if not path.startswith("/jp/"):
        return False

    if not path.endswith("-h2h-stats"):
        return False

    if "/clubs/" in path:
        return False

    return True


def extract_slug(url: str) -> str:
    path = urlparse(url).path.rstrip("/")

    return path.rsplit(
        "/",
        maxsplit=1,
    )[-1]


def extract_match_links(
    html: str,
) -> list[dict[str, str]]:
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    candidates: dict[
        str,
        dict[str, str],
    ] = {}

    for link in soup.find_all(
        "a",
        href=True,
    ):
        if not isinstance(link, Tag):
            continue

        href = link.get("href")

        if not isinstance(href, str):
            continue

        url = normalize_url(
            href.strip()
        )

        if not is_match_url(url):
            continue

        text = clean_text(
            link.get_text(
                " ",
                strip=True,
            )
        )

        slug = extract_slug(
            url
        )

        item = candidates.setdefault(
            url,
            {
                "match_slug": slug,
                "link_text": text,
                "url": url,
            },
        )

        if (
            not item["link_text"]
            and text
        ):
            item["link_text"] = text

    return sorted(
        candidates.values(),
        key=lambda row: row["url"],
    )


def write_csv(
    rows: list[dict[str, str]],
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
                "match_slug",
                "link_text",
                "url",
            ],
        )

        writer.writeheader()
        writer.writerows(
            rows
        )


def display_path(path: Path) -> str:
    try:
        return str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
    except ValueError:
        return str(path)


def print_summary(
    html_path: Path,
    output_path: Path,
    rows: list[dict[str, str]],
) -> None:
    print("=" * 110)
    print(
        "FootyStats Match Link Extraction"
    )
    print("=" * 110)

    print(
        f"source HTML : "
        f"{display_path(html_path)}"
    )
    print(
        f"抽出件数    : {len(rows)}"
    )
    print(
        f"CSV保存     : "
        f"{display_path(output_path)}"
    )

    print()
    print("MATCH LINKS")
    print("-" * 110)

    for row in rows[:30]:
        print(
            f"{row['match_slug']:<65} "
            f"| {row['link_text']}"
        )
        print(
            f"  {row['url']}"
        )

    if len(rows) > 30:
        print()
        print(
            f"... 残り {len(rows) - 30} 件"
        )


def main() -> None:
    args = parse_args()

    html_path = resolve_path(
        args.html_path
    )

    output_path = resolve_path(
        args.output
    )

    if not html_path.exists():
        raise FileNotFoundError(
            f"HTMLが見つかりません: {html_path}"
        )

    if not html_path.is_file():
        raise ValueError(
            f"ファイルではありません: {html_path}"
        )

    html = html_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    rows = extract_match_links(
        html
    )

    write_csv(
        rows=rows,
        output_path=output_path,
    )

    print_summary(
        html_path=html_path,
        output_path=output_path,
        rows=rows,
    )


if __name__ == "__main__":
    main()