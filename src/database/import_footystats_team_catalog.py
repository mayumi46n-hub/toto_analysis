#!/usr/bin/env python3
"""
Import a FootyStats team catalog directly from league pages.

Purpose
-------
Build a local catalog of FootyStats club URLs without relying on search engines.
The importer reads one or more FootyStats league pages, extracts /clubs/... links,
filters women/youth/reserve teams when requested, and upserts the results into
SQLite.

Typical usage
-------------
python src/database/import_footystats_team_catalog.py \
    --db data/toto_analysis.sqlite3 \
    --season 2025 \
    --league-url https://footystats.org/japan/j1-league \
    --league-url https://footystats.org/japan/j2-league \
    --league-url https://footystats.org/japan/j3-league

Or provide a text/CSV file:

python src/database/import_footystats_team_catalog.py \
    --db data/toto_analysis.sqlite3 \
    --season 2025 \
    --league-file config/footystats_leagues_2025.txt

The league file may contain:
    https://footystats.org/japan/j1-league
or:
    J1 League,https://footystats.org/japan/j1-league

Notes
-----
* FootyStats club URLs are stable identifiers such as:
  https://footystats.org/clubs/kashima-antlers-1006
* The importer deliberately stores the numeric FootyStats club ID when present.
* It is safe to rerun. Existing records are updated with the latest metadata.
* By default, obvious women, youth, reserve, academy, and B-team pages are excluded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import random
import re
import sqlite3
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LOGGER = logging.getLogger("import_footystats_team_catalog")

DEFAULT_BASE_URL = "https://footystats.org"
DEFAULT_TABLE = "footystats_team_catalog"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_SLEEP_SECONDS = 1.0

CLUB_PATH_RE = re.compile(
    r"^/(?:[a-z]{2}/)?clubs/(?P<slug>[^/?#]+?)(?:-(?P<club_id>\d+))?/?$",
    re.IGNORECASE,
)

# Markers intentionally cover common English and URL forms.
DEFAULT_EXCLUDE_MARKERS = {
    "academy",
    "amateur",
    "b-team",
    "bteam",
    "development",
    "femenil",
    "feminine",
    "femmes",
    "femminile",
    "frauen",
    "girls",
    "ii",
    "ladies",
    "res",
    "reserve",
    "reserves",
    "u17",
    "u18",
    "u19",
    "u20",
    "u21",
    "u23",
    "women",
    "womens",
    "woman",
    "youth",
}

TEAM_NAME_NOISE_RE = re.compile(
    r"\s+(?:stats?|form|fixtures?|results?|squad|table|xg)(?:\s.*)?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LeagueSource:
    league_name: str | None
    league_url: str


@dataclass(frozen=True)
class TeamCatalogRow:
    source: str
    season: int
    country_slug: str | None
    league_slug: str | None
    league_name: str | None
    league_url: str
    team_name: str
    team_slug: str
    footystats_team_id: int | None
    team_url: str
    is_excluded: int
    exclusion_reason: str | None
    discovered_at: str
    content_hash: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_ascii(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return value.casefold()


def clean_team_name(value: str, fallback_slug: str) -> str:
    text = normalize_space(value)
    text = TEAM_NAME_NOISE_RE.sub("", text).strip(" -|:")

    slug_text = fallback_slug.replace("-", " ").strip()
    slug_tokens = {
        token for token in normalize_ascii(slug_text).split()
        if len(token) >= 2
    }
    name_tokens = {
        token for token in re.sub(
            r"[^a-z0-9]+", " ", normalize_ascii(text)
        ).split()
        if len(token) >= 2
    }

    # FootyStatsのリーグページには、隣接クラブの表示名を含む広い<a>要素が
    # 混在することがある。URL slugと表示名に共通語が一つもない場合は、
    # URLを信頼してslug由来の名称へフォールバックする。
    if not text or (
        slug_tokens
        and name_tokens
        and slug_tokens.isdisjoint(name_tokens)
    ):
        text = slug_text.title()

    return text


def canonicalize_url(url: str, base_url: str = DEFAULT_BASE_URL) -> str:
    absolute = urljoin(base_url.rstrip("/") + "/", url)
    parts = urlsplit(absolute)

    scheme = "https"
    netloc = parts.netloc.casefold()
    if netloc.startswith("www."):
        netloc = netloc[4:]

    path = re.sub(r"/+", "/", parts.path)
    if path != "/":
        path = path.rstrip("/")

    # Tracking and language-independent noise are removed. Season parameters are
    # retained only on league URLs where they may affect page content.
    query_pairs = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.casefold().startswith(("utm_", "fbclid", "gclid"))
    ]
    query = urlencode(sorted(query_pairs))

    return urlunsplit((scheme, netloc, path, query, ""))


def add_season_to_url(url: str, season: int) -> str:
    """
    Add a season query parameter without replacing an explicitly supplied one.

    FootyStats has changed its season-selection implementation over time. The
    parameter is therefore configurable and can be disabled with
    --season-param "".
    """
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.setdefault("season", str(season))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def parse_league_identity(url: str) -> tuple[str | None, str | None]:
    parts = [p for p in urlsplit(url).path.split("/") if p]
    if parts and re.fullmatch(r"[a-z]{2}", parts[0], re.IGNORECASE):
        parts = parts[1:]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, parts[-1] if parts else None


def parse_club_url(url: str) -> tuple[str, int | None] | None:
    path = urlsplit(url).path
    match = CLUB_PATH_RE.match(path)
    if not match:
        return None

    slug_with_possible_id = match.group("slug")
    club_id_text = match.group("club_id")

    # Because the slug group is non-greedy only at the regex level, perform an
    # explicit final numeric suffix parse as a defensive fallback.
    if club_id_text is None:
        suffix_match = re.match(r"^(?P<slug>.+)-(?P<id>\d+)$", slug_with_possible_id)
        if suffix_match:
            slug_with_possible_id = suffix_match.group("slug")
            club_id_text = suffix_match.group("id")

    return slug_with_possible_id.casefold(), int(club_id_text) if club_id_text else None


def exclusion_reason(
    team_name: str,
    team_slug: str,
    markers: set[str],
) -> str | None:
    normalized = normalize_ascii(f"{team_name} {team_slug}")
    tokenized = re.sub(r"[^a-z0-9]+", " ", normalized)
    padded = f" {tokenized} "

    for marker in sorted(markers, key=len, reverse=True):
        marker_norm = re.sub(r"[^a-z0-9]+", " ", normalize_ascii(marker)).strip()
        if not marker_norm:
            continue

        if marker_norm in {"ii", "res"}:
            if f" {marker_norm} " in padded:
                return marker
        elif marker_norm in tokenized:
            return marker

    return None


def build_session(
    *,
    user_agent: str,
    retries: int,
    backoff_factor: float,
) -> requests.Session:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(408, 425, 429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=8)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ja;q=0.7",
            "Cache-Control": "no-cache",
        }
    )
    return session


def fetch_html(
    session: requests.Session,
    url: str,
    *,
    timeout: float,
) -> str:
    LOGGER.info("GET %s", url)
    response = session.get(url, timeout=timeout)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.casefold() and not response.text.lstrip().startswith("<"):
        raise ValueError(
            f"Expected HTML from {url}, received Content-Type={content_type!r}"
        )
    return response.text


def iter_anchor_candidates(
    soup: BeautifulSoup,
    league_url: str,
) -> Iterator[tuple[str, str]]:
    for anchor in soup.select("a[href]"):
        href = normalize_space(anchor.get("href", ""))
        if not href:
            continue

        absolute = canonicalize_url(href, league_url)
        if parse_club_url(absolute) is None:
            continue

        # aria-label/title/alt often contain a cleaner name than all visible text.
        name_candidates = [
            anchor.get("aria-label", ""),
            anchor.get("title", ""),
            " ".join(
                img.get("alt", "")
                for img in anchor.select("img[alt]")
                if img.get("alt")
            ),
            anchor.get_text(" ", strip=True),
        ]
        team_name = next(
            (normalize_space(v) for v in name_candidates if normalize_space(v)),
            "",
        )
        yield absolute, team_name


def iter_embedded_url_candidates(
    html: str,
    league_url: str,
) -> Iterator[tuple[str, str]]:
    """
    Fallback for club URLs embedded in JSON/script payloads but not rendered as
    ordinary anchors.
    """
    patterns = (
        r"""(?P<url>https?://(?:www\.)?footystats\.org/(?:[a-z]{2}/)?clubs/[A-Za-z0-9_%./'()-]+-\d+)""",
        r"""(?P<url>/(?:[a-z]{2}/)?clubs/[A-Za-z0-9_%./'()-]+-\d+)""",
    )
    seen: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, html, re.IGNORECASE):
            raw_url = match.group("url").replace(r"\/", "/")
            absolute = canonicalize_url(raw_url, league_url)
            if absolute in seen or parse_club_url(absolute) is None:
                continue
            seen.add(absolute)
            yield absolute, ""


def extract_teams_from_html(
    html: str,
    *,
    league: LeagueSource,
    season: int,
    exclude_markers: set[str],
    include_excluded: bool,
) -> list[TeamCatalogRow]:
    soup = BeautifulSoup(html, "html.parser")
    country_slug, league_slug = parse_league_identity(league.league_url)
    discovered_at = utc_now_iso()

    candidates: dict[str, str] = {}
    for team_url, team_name in iter_anchor_candidates(soup, league.league_url):
        current = candidates.get(team_url, "")
        if len(team_name) > len(current):
            candidates[team_url] = team_name

    for team_url, team_name in iter_embedded_url_candidates(html, league.league_url):
        candidates.setdefault(team_url, team_name)

    rows: list[TeamCatalogRow] = []
    for team_url, raw_name in candidates.items():
        parsed = parse_club_url(team_url)
        if parsed is None:
            continue

        team_slug, team_id = parsed
        team_name = clean_team_name(raw_name, team_slug)
        reason = exclusion_reason(team_name, team_slug, exclude_markers)

        if reason and not include_excluded:
            LOGGER.debug("Excluded %s (%s)", team_url, reason)
            continue

        stable_payload = {
            "season": season,
            "league_url": canonicalize_url(league.league_url),
            "team_name": team_name,
            "team_slug": team_slug,
            "team_id": team_id,
            "team_url": canonicalize_url(team_url),
            "is_excluded": bool(reason),
            "exclusion_reason": reason,
        }
        content_hash = hashlib.sha256(
            json.dumps(stable_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()

        rows.append(
            TeamCatalogRow(
                source="footystats",
                season=season,
                country_slug=country_slug,
                league_slug=league_slug,
                league_name=league.league_name,
                league_url=canonicalize_url(league.league_url),
                team_name=team_name,
                team_slug=team_slug,
                footystats_team_id=team_id,
                team_url=canonicalize_url(team_url),
                is_excluded=int(reason is not None),
                exclusion_reason=reason,
                discovered_at=discovered_at,
                content_hash=content_hash,
            )
        )

    # A URL is the strongest identity. Sort for deterministic DB and JSON output.
    return sorted(rows, key=lambda row: (row.team_name.casefold(), row.team_url))


def ensure_schema(conn: sqlite3.Connection, table: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
        raise ValueError(f"Unsafe table name: {table!r}")

    conn.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS {table} (
            catalog_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL DEFAULT 'footystats',
            season INTEGER NOT NULL,
            country_slug TEXT,
            league_slug TEXT,
            league_name TEXT,
            league_url TEXT NOT NULL,
            team_name TEXT NOT NULL,
            team_slug TEXT NOT NULL,
            footystats_team_id INTEGER,
            team_url TEXT NOT NULL,
            is_excluded INTEGER NOT NULL DEFAULT 0 CHECK (is_excluded IN (0, 1)),
            exclusion_reason TEXT,
            discovered_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            UNIQUE (season, league_url, team_url)
        );

        CREATE INDEX IF NOT EXISTS idx_{table}_season
            ON {table} (season);

        CREATE INDEX IF NOT EXISTS idx_{table}_team_id
            ON {table} (footystats_team_id);

        CREATE INDEX IF NOT EXISTS idx_{table}_team_slug
            ON {table} (team_slug);

        CREATE INDEX IF NOT EXISTS idx_{table}_league
            ON {table} (season, country_slug, league_slug);
        """
    )


def upsert_rows(
    conn: sqlite3.Connection,
    table: str,
    rows: Sequence[TeamCatalogRow],
) -> int:
    if not rows:
        return 0

    now = utc_now_iso()
    sql = f"""
        INSERT INTO {table} (
            source,
            season,
            country_slug,
            league_slug,
            league_name,
            league_url,
            team_name,
            team_slug,
            footystats_team_id,
            team_url,
            is_excluded,
            exclusion_reason,
            discovered_at,
            updated_at,
            content_hash
        )
        VALUES (
            :source,
            :season,
            :country_slug,
            :league_slug,
            :league_name,
            :league_url,
            :team_name,
            :team_slug,
            :footystats_team_id,
            :team_url,
            :is_excluded,
            :exclusion_reason,
            :discovered_at,
            :updated_at,
            :content_hash
        )
        ON CONFLICT (season, league_url, team_url) DO UPDATE SET
            source = excluded.source,
            country_slug = excluded.country_slug,
            league_slug = excluded.league_slug,
            league_name = COALESCE(excluded.league_name, {table}.league_name),
            team_name = excluded.team_name,
            team_slug = excluded.team_slug,
            footystats_team_id = COALESCE(
                excluded.footystats_team_id,
                {table}.footystats_team_id
            ),
            is_excluded = excluded.is_excluded,
            exclusion_reason = excluded.exclusion_reason,
            updated_at = excluded.updated_at,
            content_hash = excluded.content_hash
    """

    payload = []
    for row in rows:
        item = asdict(row)
        item["updated_at"] = now
        payload.append(item)

    conn.executemany(sql, payload)
    return len(payload)


def deactivate_missing_rows(
    conn: sqlite3.Connection,
    table: str,
    *,
    season: int,
    league_url: str,
    current_team_urls: set[str],
) -> int:
    """
    Optional strict synchronization.

    Records absent from the latest page are marked excluded rather than deleted,
    preserving historical traceability.
    """
    if current_team_urls:
        placeholders = ",".join("?" for _ in current_team_urls)
        sql = f"""
            UPDATE {table}
               SET is_excluded = 1,
                   exclusion_reason = 'missing_from_latest_catalog',
                   updated_at = ?
             WHERE season = ?
               AND league_url = ?
               AND team_url NOT IN ({placeholders})
               AND (
                    is_excluded = 0
                    OR exclusion_reason = 'missing_from_latest_catalog'
               )
        """
        params = [
            utc_now_iso(),
            season,
            canonicalize_url(league_url),
            *sorted(current_team_urls),
        ]
    else:
        sql = f"""
            UPDATE {table}
               SET is_excluded = 1,
                   exclusion_reason = 'missing_from_latest_catalog',
                   updated_at = ?
             WHERE season = ?
               AND league_url = ?
        """
        params = [utc_now_iso(), season, canonicalize_url(league_url)]

    cursor = conn.execute(sql, params)
    return cursor.rowcount


def parse_league_file(path: Path) -> list[LeagueSource]:
    if not path.exists():
        raise FileNotFoundError(path)

    sources: list[LeagueSource] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            row = next(csv.reader([stripped]))
            row = [normalize_space(cell) for cell in row]
            if len(row) == 1:
                league_name, league_url = None, row[0]
            elif len(row) >= 2:
                league_name, league_url = row[0] or None, row[1]
            else:
                continue

            if not league_url.startswith(("http://", "https://")):
                raise ValueError(
                    f"{path}:{line_number}: invalid league URL: {league_url!r}"
                )
            sources.append(
                LeagueSource(
                    league_name=league_name,
                    league_url=canonicalize_url(league_url),
                )
            )
    return sources


def deduplicate_sources(sources: Iterable[LeagueSource]) -> list[LeagueSource]:
    deduped: dict[str, LeagueSource] = {}
    for source in sources:
        url = canonicalize_url(source.league_url)
        existing = deduped.get(url)
        if existing is None or (not existing.league_name and source.league_name):
            deduped[url] = LeagueSource(source.league_name, url)
    return list(deduped.values())


def write_json_report(path: Path, rows: Sequence[TeamCatalogRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Import FootyStats club URLs directly from league pages into SQLite."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        required=True,
        help="SQLite database path.",
    )
    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="Season key stored in the catalog, for example 2025.",
    )
    parser.add_argument(
        "--league-url",
        action="append",
        default=[],
        help="FootyStats league URL. Repeat for multiple leagues.",
    )
    parser.add_argument(
        "--league-file",
        type=Path,
        help="UTF-8 text/CSV file containing league URLs.",
    )
    parser.add_argument(
        "--table",
        default=DEFAULT_TABLE,
        help=f"Destination table name. Default: {DEFAULT_TABLE}",
    )
    parser.add_argument(
        "--season-param",
        default="season",
        help=(
            "Query parameter used to request a season. Use an empty string to "
            "leave league URLs unchanged. Default: season"
        ),
    )
    parser.add_argument(
        "--include-excluded",
        action="store_true",
        help="Store women/youth/reserve candidates with is_excluded=1.",
    )
    parser.add_argument(
        "--exclude-marker",
        action="append",
        default=[],
        help="Additional case-insensitive exclusion marker. Repeatable.",
    )
    parser.add_argument(
        "--replace-exclude-markers",
        action="store_true",
        help="Use only --exclude-marker values, replacing the defaults.",
    )
    parser.add_argument(
        "--sync-missing",
        action="store_true",
        help=(
            "Mark previously stored teams missing from a league page as excluded. "
            "Use only when the fetched page is known to be complete."
        ),
    )
    parser.add_argument(
        "--min-teams",
        type=int,
        default=1,
        help=(
            "Fail a league import when fewer than this many teams are extracted. "
            "Set this to the expected lower bound, e.g. 10. Default: 1"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout seconds. Default: {DEFAULT_TIMEOUT_SECONDS}",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help=f"Delay between league requests. Default: {DEFAULT_SLEEP_SECONDS}",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="HTTP retry count. Default: 4",
    )
    parser.add_argument(
        "--backoff-factor",
        type=float,
        default=1.0,
        help="Retry exponential backoff factor. Default: 1.0",
    )
    parser.add_argument(
        "--user-agent",
        default=(
            "Mozilla/5.0 (compatible; toto_analysis/1.0; "
            "+local-data-pipeline)"
        ),
        help="HTTP User-Agent.",
    )
    parser.add_argument(
        "--html-dir",
        type=Path,
        help="Optional directory in which fetched HTML pages are archived.",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Optional JSON report containing all extracted rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and parse pages but do not modify SQLite.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def resolve_sources(args: argparse.Namespace) -> list[LeagueSource]:
    sources = [
        LeagueSource(league_name=None, league_url=canonicalize_url(url))
        for url in args.league_url
    ]
    if args.league_file:
        sources.extend(parse_league_file(args.league_file))

    sources = deduplicate_sources(sources)
    if not sources:
        raise ValueError(
            "At least one --league-url or --league-file entry is required."
        )
    return sources


def archive_html(
    html_dir: Path,
    *,
    league: LeagueSource,
    season: int,
    html: str,
) -> Path:
    _, league_slug = parse_league_identity(league.league_url)
    safe_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", league_slug or "league")
    path = html_dir / str(season) / f"{safe_slug}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def run(args: argparse.Namespace) -> int:
    sources = resolve_sources(args)

    if args.replace_exclude_markers:
        markers = set(args.exclude_marker)
    else:
        markers = DEFAULT_EXCLUDE_MARKERS | set(args.exclude_marker)

    session = build_session(
        user_agent=args.user_agent,
        retries=args.retries,
        backoff_factor=args.backoff_factor,
    )

    all_rows: list[TeamCatalogRow] = []
    failures: list[str] = []

    conn: sqlite3.Connection | None = None
    if not args.dry_run:
        args.db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        ensure_schema(conn, args.table)

    try:
        for index, league in enumerate(sources):
            request_url = league.league_url
            if args.season_param:
                parts = urlsplit(request_url)
                query = dict(parse_qsl(parts.query, keep_blank_values=True))
                query.setdefault(args.season_param, str(args.season))
                request_url = urlunsplit(
                    (
                        parts.scheme,
                        parts.netloc,
                        parts.path,
                        urlencode(query),
                        "",
                    )
                )

            try:
                html = fetch_html(session, request_url, timeout=args.timeout)
                if args.html_dir:
                    archived = archive_html(
                        args.html_dir,
                        league=league,
                        season=args.season,
                        html=html,
                    )
                    LOGGER.info("Archived HTML: %s", archived)

                rows = extract_teams_from_html(
                    html,
                    league=league,
                    season=args.season,
                    exclude_markers=markers,
                    include_excluded=args.include_excluded,
                )

                active_count = sum(row.is_excluded == 0 for row in rows)
                excluded_count = len(rows) - active_count
                LOGGER.info(
                    "%s: extracted=%d active=%d excluded=%d",
                    league.league_url,
                    len(rows),
                    active_count,
                    excluded_count,
                )

                if active_count < args.min_teams:
                    raise RuntimeError(
                        f"Only {active_count} active teams extracted; "
                        f"--min-teams={args.min_teams}"
                    )

                all_rows.extend(rows)

                if conn is not None:
                    with conn:
                        upsert_rows(conn, args.table, rows)
                        if args.sync_missing:
                            current_urls = {
                                row.team_url for row in rows if row.is_excluded == 0
                            }
                            changed = deactivate_missing_rows(
                                conn,
                                args.table,
                                season=args.season,
                                league_url=league.league_url,
                                current_team_urls=current_urls,
                            )
                            LOGGER.info(
                                "%s: marked missing rows=%d",
                                league.league_url,
                                changed,
                            )

            except Exception as exc:
                message = f"{league.league_url}: {exc}"
                failures.append(message)
                LOGGER.exception("League import failed: %s", league.league_url)

            if index < len(sources) - 1 and args.sleep > 0:
                time.sleep(args.sleep + random.uniform(0.0, min(0.5, args.sleep)))

    finally:
        if conn is not None:
            conn.close()
        session.close()

    if args.json_report:
        write_json_report(args.json_report, all_rows)
        LOGGER.info("JSON report: %s", args.json_report)

    print(
        json.dumps(
            {
                "season": args.season,
                "league_count": len(sources),
                "row_count": len(all_rows),
                "active_count": sum(row.is_excluded == 0 for row in all_rows),
                "excluded_count": sum(row.is_excluded == 1 for row in all_rows),
                "failure_count": len(failures),
                "failures": failures,
                "dry_run": args.dry_run,
                "database": None if args.dry_run else str(args.db),
                "table": args.table,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 1 if failures else 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        return run(args)
    except KeyboardInterrupt:
        LOGGER.error("Interrupted")
        return 130
    except Exception:
        LOGGER.exception("Fatal error")
        return 2


if __name__ == "__main__":
    sys.exit(main())
