# -*- coding: utf-8 -*-

"""
Project AKAMURASAKI

File:
    check_footystats_match_sides.py

Purpose:
    FootyStats試合ページからホーム・アウェイを判定する。

判定方法:
    1. HTMLの<title>から「ホーム対アウェイ」を取得
    2. ページ内のクラブリンクからFootyStats外部IDを取得
    3. 日本語名、英語名、URLスラッグを使って対応づける

このスクリプトはDBやJSONを変更しない。
判定結果の確認だけを行う。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HTML_PATH = (
    PROJECT_ROOT
    / "data/raw/footystats/matches/2026/"
    "kataller_toyama_vs_vanraure_hachinohe.html"
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


def normalize_name(
    value: str | None,
) -> str:
    if value is None:
        return ""

    normalized = value.casefold()

    normalized = re.sub(
        r"[\s・\.．\-ー_'’]",
        "",
        normalized,
    )

    normalized = normalized.replace(
        "fc",
        "",
    )

    normalized = normalized.replace(
        "f.c",
        "",
    )

    return normalized


def extract_team_id(
    href: str,
) -> int | None:
    path = urlparse(
        href
    ).path

    match = re.search(
        r"/clubs/[^/?#]+-(\d+)(?:/)?$",
        path,
    )

    if match is None:
        return None

    return int(
        match.group(1)
    )


def extract_slug_name(
    href: str,
) -> str | None:
    path = urlparse(
        href
    ).path

    match = re.search(
        r"/clubs/([^/?#]+)-\d+(?:/)?$",
        path,
    )

    if match is None:
        return None

    return match.group(1)


def extract_title_sides(
    soup: BeautifulSoup,
) -> tuple[str, str]:
    if soup.title is None:
        raise ValueError(
            "HTMLにtitleがありません"
        )

    title = clean_text(
        soup.title.get_text(
            " ",
            strip=True,
        )
    )

    if not title:
        raise ValueError(
            "titleが空です"
        )

    # 日本語タイトル:
    #   "浦和レッズ 対 湘南ベルマーレ 統計情報 | FootyStats"
    japanese_prefix = re.split(
        r"\s*(?:統計情報|結果|対戦成績|\|)\s*",
        title,
        maxsplit=1,
    )[0]

    japanese_match = re.match(
        r"(.+?)\s*対\s*(.+)$",
        japanese_prefix,
    )

    if japanese_match is not None:
        home_name = clean_text(
            japanese_match.group(1)
        )
        away_name = clean_text(
            japanese_match.group(2)
        )
    else:
        # 英語タイトル:
        #   "Urawa Reds vs Shonan Bellmare Stats, H2H, xG | FootyStats"
        english_title = re.sub(
            r"\s*\|\s*FootyStats\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        english_title = re.sub(
            r"\s+Stats(?:,\s*H2H)?(?:,\s*xG)?\s*$",
            "",
            english_title,
            flags=re.IGNORECASE,
        )

        english_match = re.match(
            r"(.+?)\s+vs\.?\s+(.+)$",
            english_title,
            flags=re.IGNORECASE,
        )

        if english_match is None:
            raise ValueError(
                "titleから対戦チームを取得できません: "
                f"{title}"
            )

        home_name = clean_text(
            english_match.group(1)
        )
        away_name = clean_text(
            english_match.group(2)
        )

    if not home_name or not away_name:
        raise ValueError(
            "ホームまたはアウェイ名が空です"
        )

    return (
        home_name,
        away_name,
    )


def collect_team_candidates(
    soup: BeautifulSoup,
) -> list[dict[str, Any]]:
    teams: dict[
        int,
        dict[str, Any],
    ] = {}

    links = soup.select(
        'a[href*="/clubs/"]'
    )

    for link in links:
        if not isinstance(
            link,
            Tag,
        ):
            continue

        href = link.get("href")

        if not isinstance(
            href,
            str,
        ):
            continue

        external_team_id = extract_team_id(
            href
        )

        if external_team_id is None:
            continue

        item = teams.setdefault(
            external_team_id,
            {
                "external_team_id": (
                    external_team_id
                ),
                "source_url": href,
                "slug_name": (
                    extract_slug_name(
                        href
                    )
                ),
                "names": set(),
            },
        )

        link_text = clean_text(
            link.get_text(
                " ",
                strip=True,
            )
        )

        if link_text:
            item["names"].add(
                link_text
            )

        image = link.find("img")

        if isinstance(
            image,
            Tag,
        ):
            alt = image.get("alt")

            if isinstance(
                alt,
                str,
            ):
                alt_text = clean_text(
                    alt
                )

                if alt_text:
                    alt_text = re.sub(
                        r"\s+(?:Logo|ロゴ)$",
                        "",
                        alt_text,
                        flags=re.IGNORECASE,
                    ).strip()

                    item["names"].add(
                        alt_text
                    )

    results: list[
        dict[str, Any]
    ] = []

    for item in teams.values():
        item["names"] = sorted(
            item["names"]
        )

        results.append(
            item
        )

    return sorted(
        results,
        key=lambda item: int(
            item["external_team_id"]
        ),
    )


def candidate_score(
    target_name: str,
    candidate: dict[str, Any],
) -> int:
    target = normalize_name(
        target_name
    )

    if not target:
        return 0

    score = 0

    candidate_names = list(
        candidate.get(
            "names",
            [],
        )
    )

    slug_name = candidate.get(
        "slug_name"
    )

    if isinstance(
        slug_name,
        str,
    ):
        candidate_names.append(
            slug_name.replace(
                "-",
                " ",
            )
        )

    for candidate_name in candidate_names:
        normalized_candidate = (
            normalize_name(
                str(candidate_name)
            )
        )

        if not normalized_candidate:
            continue

        if target == normalized_candidate:
            score = max(
                score,
                100,
            )
            continue

        if (
            target in normalized_candidate
            or normalized_candidate in target
        ):
            score = max(
                score,
                70,
            )

    return score


def resolve_side(
    target_name: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    scored = [
        (
            candidate_score(
                target_name,
                candidate,
            ),
            candidate,
        )
        for candidate in candidates
    ]

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    if not scored:
        raise ValueError(
            f"チーム候補がありません: {target_name}"
        )

    best_score, best_candidate = (
        scored[0]
    )

    if best_score <= 0:
        raise ValueError(
            "外部IDを解決できません: "
            f"{target_name}"
        )

    return {
        "display_name": target_name,
        "external_team_id": (
            best_candidate[
                "external_team_id"
            ]
        ),
        "source_url": (
            best_candidate[
                "source_url"
            ]
        ),
        "candidate_names": (
            best_candidate[
                "names"
            ]
        ),
        "match_score": best_score,
    }


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

    home_title_name, away_title_name = (
        extract_title_sides(
            soup
        )
    )

    candidates = collect_team_candidates(
        soup
    )

    home = resolve_side(
        home_title_name,
        candidates,
    )

    away = resolve_side(
        away_title_name,
        candidates,
    )

    if (
        home["external_team_id"]
        == away["external_team_id"]
    ):
        raise ValueError(
            "ホームとアウェイが同じ外部IDです"
        )

    print("=" * 100)
    print(
        "FootyStats Match Side Check"
    )
    print("=" * 100)

    print(
        f"home_team_name          : "
        f"{home['display_name']}"
    )
    print(
        f"home_external_team_id   : "
        f"{home['external_team_id']}"
    )
    print(
        f"home_source_url         : "
        f"{home['source_url']}"
    )
    print(
        f"home_candidate_names    : "
        f"{home['candidate_names']}"
    )
    print()
    print(
        f"away_team_name          : "
        f"{away['display_name']}"
    )
    print(
        f"away_external_team_id   : "
        f"{away['external_team_id']}"
    )
    print(
        f"away_source_url         : "
        f"{away['source_url']}"
    )
    print(
        f"away_candidate_names    : "
        f"{away['candidate_names']}"
    )


if __name__ == "__main__":
    main()
