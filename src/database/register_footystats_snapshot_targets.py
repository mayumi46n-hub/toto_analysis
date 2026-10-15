#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FootyStats試合ページをスナップショット取得対象として登録する。

FootyStatsリーグページを「Webページ、完全」で保存したHTMLから、
未開催試合の対戦URL、ホーム・アウェイ、キックオフ時刻を抽出する。
Jリーグ公式DBの試合と完全照合できたものだけを対象として登録し、
キックオフ72時間前・24時間前・6時間前の取得予定を生成する。

このスクリプトはWebアクセスを行わない。保存済みHTMLの解析と、
以下のテーブルへの登録だけを行う。

* web_snapshot_targets
* web_snapshot_jobs

実行例:

    python src/database/register_footystats_snapshot_targets.py \
        --db data/toto.db \
        --season 2026 \
        --league j1 \
        --html "/path/to/J1リーグ 2026_試合タブ.html" \
        --dry-run \
        --verbose \
        --report data/interim/footystats_snapshot_targets_2026_j1.json
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Final, Iterable
from urllib.parse import urlsplit, urlunsplit
from zoneinfo import ZoneInfo

try:
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover - friendly CLI error
    raise SystemExit(
        "BeautifulSoupが必要です。"
        " `python -m pip install beautifulsoup4` を実行してください。"
    ) from exc


DEFAULT_DB_PATH: Final = Path("data/toto.db")
DEFAULT_TIMEZONE: Final = "Asia/Tokyo"
DEFAULT_CAPTURE_OFFSETS: Final = (72, 24, 6)

TARGET_TABLE: Final = "web_snapshot_targets"
JOB_TABLE: Final = "web_snapshot_jobs"

LEAGUE_TO_COMPETITION: Final = {
    "j1": "J1",
    "j2": "J2",
    "j3": "J3",
}

REQUIRED_TABLE_COLUMNS: Final = {
    "jleague_matches": {
        "jleague_match_id",
        "season",
        "competition",
        "match_date",
        "kickoff_time",
        "home_team",
        "away_team",
    },
    "team_master": {
        "team_id",
        "short_name",
        "full_name",
    },
    "team_alias_v2": {
        "team_id",
        "alias_name",
    },
    "team_source_map": {
        "team_id",
        "source_name",
        "external_team_id",
    },
    TARGET_TABLE: {
        "snapshot_target_id",
        "target_key",
        "source_name",
        "source_url",
        "jleague_match_id",
        "season",
        "league",
        "home_team_name",
        "away_team_name",
        "scheduled_at",
        "timezone_name",
        "is_active",
        "updated_at",
        "metadata_json",
    },
    JOB_TABLE: {
        "snapshot_job_id",
        "snapshot_target_id",
        "capture_slot",
        "anchor_type",
        "target_capture_at",
        "expires_at",
        "job_status",
        "attempt_count",
        "last_error",
        "updated_at",
    },
}


@dataclass(frozen=True)
class ParsedFixture:
    source_file: str
    source_url: str
    source_timestamp: int
    scheduled_at: datetime
    home_external_team_id: str
    away_external_team_id: str
    home_external_name: str
    away_external_name: str
    row_status: str


@dataclass(frozen=True)
class OfficialMatch:
    jleague_match_id: int
    season: int
    league: str
    match_date: date
    kickoff_time: str
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str


@dataclass(frozen=True)
class ResolvedTarget:
    fixture: ParsedFixture
    official: OfficialMatch


@dataclass
class RegistrationStats:
    html_files: int = 0
    fixture_rows: int = 0
    incomplete_rows: int = 0
    suspended_rows: int = 0
    ignored_rows: int = 0
    duplicate_rows: int = 0
    unconfirmed_time_rows: int = 0
    external_mapping_missing: int = 0
    official_match_missing: int = 0
    ambiguous_official_matches: int = 0
    kickoff_mismatch: int = 0
    resolved_targets: int = 0
    targets_inserted: int = 0
    targets_updated: int = 0
    targets_unchanged: int = 0
    jobs_inserted: int = 0
    jobs_existing: int = 0
    jobs_cancelled_for_reschedule: int = 0
    jobs_marked_skipped: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みFootyStatsリーグHTMLから未開催試合を抽出し、"
            "72時間前・24時間前・6時間前の取得予定を登録します。"
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite DB path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="対象シーズン。例: 2026",
    )
    parser.add_argument(
        "--league",
        choices=sorted(LEAGUE_TO_COMPETITION),
        required=True,
        help="対象リーグ。",
    )
    parser.add_argument(
        "--html",
        type=Path,
        action="append",
        required=True,
        help="FootyStats試合タブHTML。複数回指定できます。",
    )
    parser.add_argument(
        "--capture-hours",
        type=int,
        nargs="+",
        default=list(DEFAULT_CAPTURE_OFFSETS),
        help="キックオフ何時間前に取得するか (default: 72 24 6)",
    )
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help=f"保存時刻のタイムゾーン (default: {DEFAULT_TIMEZONE})",
    )
    parser.add_argument(
        "--include-0900",
        action="store_true",
        help=(
            "FootyStatsの09:00表示も確定時刻として扱います。"
            "通常は未確定時刻の可能性が高いため除外します。"
        ),
    )
    parser.add_argument(
        "--include-past",
        action="store_true",
        help="キックオフ済みの試合も対象として解析します。",
    )
    parser.add_argument(
        "--now",
        help=(
            "判定基準日時をISO 8601で指定します。"
            "省略時は現在時刻です。主に検証用です。"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="登録内容を検証しますが、データベースは変更しません。",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="登録対象と除外理由を詳しく表示します。",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="JSONレポートの保存先。",
    )
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (Path.cwd() / expanded).resolve()


def normalize_name(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[\s\u3000・･.\-‐‑‒–—―ー_'’]+", "", text)


def normalize_competition(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").upper()
    compact = re.sub(r"\s+", "", text)
    match = re.search(r"J([123])", compact)
    return f"J{match.group(1)}" if match else compact


def clean_source_url(value: str) -> str:
    value = value.strip()
    if value.startswith("/"):
        value = "https" + "://" + "footystats.org" + value
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"URL schemeが不正です: {value}")
    if parsed.netloc.casefold() not in {
        "footystats.org",
        "www.footystats.org",
    }:
        raise ValueError(f"FootyStats以外のURLです: {value}")
    if not parsed.path.endswith("-h2h-stats"):
        raise ValueError(f"対戦ページURLではありません: {value}")
    return urlunsplit(
        (
            "https",
            "footystats.org",
            parsed.path,
            "",
            "",
        )
    )


def parse_external_team_id(url: str) -> str | None:
    parsed = urlsplit(url)
    match = re.search(r"-(\d+)/?$", parsed.path)
    return match.group(1) if match else None


def parse_iso_datetime(
    value: str,
    timezone: ZoneInfo,
) -> datetime:
    candidate = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def iso_seconds(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def parse_official_date(
    value: str | None,
    season: int,
) -> date | None:
    text = unicodedata.normalize("NFKC", value or "").strip()
    match = re.match(
        r"^(?:(\d{2,4})[/-])?(\d{1,2})[/-](\d{1,2})",
        text,
    )
    if not match:
        return None

    year_text, month_text, day_text = match.groups()
    if year_text is None:
        year = season
    else:
        year = int(year_text)
        if year < 100:
            year += 2000

    try:
        return date(year, int(month_text), int(day_text))
    except ValueError:
        return None


def table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    rows = connection.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()
    return {str(row[1]) for row in rows}


def validate_schema(connection: sqlite3.Connection) -> None:
    for table_name, required in REQUIRED_TABLE_COLUMNS.items():
        actual = table_columns(connection, table_name)
        if not actual:
            raise RuntimeError(
                f"必要なテーブルがありません: {table_name}"
            )
        missing = required - actual
        if missing:
            raise RuntimeError(
                f"{table_name} の列が不足しています: "
                f"{sorted(missing)}"
            )


def add_alias(
    aliases: dict[str, int],
    alias: str | None,
    team_id: int,
) -> None:
    key = normalize_name(alias)
    if not key:
        return
    existing = aliases.get(key)
    if existing is not None and existing != team_id:
        raise RuntimeError(
            "チーム別名が複数team_idへ登録されています: "
            f"alias={alias!r}, team_id={existing}/{team_id}"
        )
    aliases[key] = team_id


def load_internal_aliases(
    connection: sqlite3.Connection,
) -> dict[str, int]:
    aliases: dict[str, int] = {}

    rows = connection.execute(
        """
        SELECT team_id, short_name, full_name
        FROM team_master
        """
    ).fetchall()
    for row in rows:
        team_id = int(row["team_id"])
        add_alias(aliases, row["short_name"], team_id)
        add_alias(aliases, row["full_name"], team_id)

    rows = connection.execute(
        """
        SELECT team_id, alias_name
        FROM team_alias_v2
        """
    ).fetchall()
    for row in rows:
        add_alias(
            aliases,
            row["alias_name"],
            int(row["team_id"]),
        )

    return aliases


def load_footystats_team_map(
    connection: sqlite3.Connection,
) -> dict[str, int]:
    rows = connection.execute(
        """
        SELECT team_id, external_team_id
        FROM team_source_map
        WHERE lower(source_name) = 'footystats'
          AND external_team_id IS NOT NULL
          AND trim(external_team_id) <> ''
        """
    ).fetchall()

    result: dict[str, int] = {}
    for row in rows:
        external_id = str(row["external_team_id"]).strip()
        team_id = int(row["team_id"])
        existing = result.get(external_id)
        if existing is not None and existing != team_id:
            raise RuntimeError(
                "FootyStats external_team_idが重複しています: "
                f"{external_id}"
            )
        result[external_id] = team_id
    return result


def load_official_matches(
    connection: sqlite3.Connection,
    season: int,
    league: str,
    aliases: dict[str, int],
) -> dict[tuple[int, int, date], list[OfficialMatch]]:
    rows = connection.execute(
        """
        SELECT
            jleague_match_id,
            season,
            competition,
            match_date,
            kickoff_time,
            home_team,
            away_team
        FROM jleague_matches
        WHERE season = ?
        ORDER BY jleague_match_id
        """,
        (season,),
    ).fetchall()

    expected_competition = LEAGUE_TO_COMPETITION[league]
    matches: dict[
        tuple[int, int, date],
        list[OfficialMatch],
    ] = {}

    for row in rows:
        if (
            normalize_competition(row["competition"])
            != expected_competition
        ):
            continue

        match_date = parse_official_date(
            row["match_date"],
            season,
        )
        if match_date is None:
            continue

        home_team_id = aliases.get(
            normalize_name(row["home_team"])
        )
        away_team_id = aliases.get(
            normalize_name(row["away_team"])
        )
        if home_team_id is None or away_team_id is None:
            unresolved = (
                row["home_team"]
                if home_team_id is None
                else row["away_team"]
            )
            raise RuntimeError(
                "Jリーグ公式チーム名をteam_idへ解決できません: "
                f"{unresolved}"
            )

        official = OfficialMatch(
            jleague_match_id=int(row["jleague_match_id"]),
            season=int(row["season"]),
            league=league,
            match_date=match_date,
            kickoff_time=str(row["kickoff_time"] or "").strip(),
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_team_name=str(row["home_team"]),
            away_team_name=str(row["away_team"]),
        )
        key = (home_team_id, away_team_id, match_date)
        matches.setdefault(key, []).append(official)

    return matches


def row_status(row: object) -> str:
    classes = {
        str(value).casefold()
        for value in (row.get("class") or [])
    }
    marker = row.select_one("[data-match-status]")
    status = (
        str(marker.get("data-match-status") or "").casefold()
        if marker is not None
        else ""
    )
    if status:
        return status
    if "incomplete" in classes:
        return "incomplete"
    if "suspended" in classes:
        return "suspended"
    return "other"


def extract_fixtures(
    html_path: Path,
    timezone: ZoneInfo,
    stats: RegistrationStats,
    verbose: bool,
) -> list[ParsedFixture]:
    try:
        html = html_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise RuntimeError(
            f"HTMLを読み込めません: {html_path}: {exc}"
        ) from exc

    soup = BeautifulSoup(html, "html.parser")
    fixtures: list[ParsedFixture] = []

    for row in soup.select("tr.match, ul.match"):
        stats.fixture_rows += 1
        status = row_status(row)
        if status == "suspended":
            stats.suspended_rows += 1
            continue
        if status != "incomplete":
            stats.ignored_rows += 1
            continue
        stats.incomplete_rows += 1

        date_cell = row.select_one("td.date[data-time], li.date[data-time]")
        home_link = row.select_one("td.team-home a[href], a.team.home[href]")
        away_link = row.select_one("td.team-away a[href], a.team.away[href]")
        page_link = row.select_one('a.h2h-link[href*="-h2h-stats"], a[href*="-h2h-stats"]')
        if not all((date_cell, home_link, away_link, page_link)):
            if verbose:
                print(
                    f"SKIP malformed row: {html_path.name}",
                    file=sys.stderr,
                )
            continue

        try:
            timestamp = int(str(date_cell["data-time"]))
            scheduled_at = datetime.fromtimestamp(
                timestamp,
                timezone,
            )
            source_url = clean_source_url(
                str(page_link["href"])
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"試合行の日時またはURLが不正です: "
                f"{html_path.name}: {exc}"
            ) from exc

        home_external_id = parse_external_team_id(
            str(home_link["href"])
        )
        away_external_id = parse_external_team_id(
            str(away_link["href"])
        )
        if home_external_id is None or away_external_id is None:
            raise RuntimeError(
                "FootyStatsクラブURLからexternal_team_idを"
                f"取得できません: {source_url}"
            )

        fixtures.append(
            ParsedFixture(
                source_file=str(html_path),
                source_url=source_url,
                source_timestamp=timestamp,
                scheduled_at=scheduled_at,
                home_external_team_id=home_external_id,
                away_external_team_id=away_external_id,
                home_external_name=home_link.get_text(
                    " ",
                    strip=True,
                ),
                away_external_name=away_link.get_text(
                    " ",
                    strip=True,
                ),
                row_status=status,
            )
        )

    return fixtures


def deduplicate_fixtures(
    fixtures: Iterable[ParsedFixture],
    stats: RegistrationStats,
) -> list[ParsedFixture]:
    unique: dict[
        tuple[int, str, str, str],
        ParsedFixture,
    ] = {}

    for fixture in fixtures:
        key = (
            fixture.source_timestamp,
            fixture.home_external_team_id,
            fixture.away_external_team_id,
            fixture.source_url,
        )
        previous = unique.get(key)
        if previous is not None:
            stats.duplicate_rows += 1
            continue
        unique[key] = fixture

    return sorted(
        unique.values(),
        key=lambda item: (
            item.scheduled_at,
            item.home_external_team_id,
            item.away_external_team_id,
        ),
    )


def resolve_targets(
    fixtures: Iterable[ParsedFixture],
    team_map: dict[str, int],
    official_matches: dict[
        tuple[int, int, date],
        list[OfficialMatch],
    ],
    now: datetime,
    include_0900: bool,
    include_past: bool,
    stats: RegistrationStats,
    verbose: bool,
) -> tuple[list[ResolvedTarget], list[dict[str, object]]]:
    resolved: list[ResolvedTarget] = []
    issues: list[dict[str, object]] = []

    for fixture in fixtures:
        if (
            not include_0900
            and fixture.scheduled_at.strftime("%H:%M") == "09:00"
        ):
            stats.unconfirmed_time_rows += 1
            continue

        if not include_past and fixture.scheduled_at <= now:
            continue

        home_team_id = team_map.get(
            fixture.home_external_team_id
        )
        away_team_id = team_map.get(
            fixture.away_external_team_id
        )
        if home_team_id is None or away_team_id is None:
            stats.external_mapping_missing += 1
            issue = {
                "reason": "external_team_mapping_missing",
                "source_url": fixture.source_url,
                "home_external_team_id": (
                    fixture.home_external_team_id
                ),
                "away_external_team_id": (
                    fixture.away_external_team_id
                ),
            }
            issues.append(issue)
            if verbose:
                print(
                    "UNRESOLVED external mapping: "
                    f"{fixture.home_external_name} vs "
                    f"{fixture.away_external_name}"
                )
            continue

        key = (
            home_team_id,
            away_team_id,
            fixture.scheduled_at.date(),
        )
        candidates = official_matches.get(key, [])
        if not candidates:
            stats.official_match_missing += 1
            issue = {
                "reason": "official_match_missing",
                "source_url": fixture.source_url,
                "scheduled_at": iso_seconds(
                    fixture.scheduled_at
                ),
                "home_external_name": (
                    fixture.home_external_name
                ),
                "away_external_name": (
                    fixture.away_external_name
                ),
            }
            issues.append(issue)
            if verbose:
                print(
                    "UNRESOLVED official match: "
                    f"{fixture.scheduled_at:%Y-%m-%d %H:%M} "
                    f"{fixture.home_external_name} vs "
                    f"{fixture.away_external_name}"
                )
            continue

        source_time = fixture.scheduled_at.strftime("%H:%M")
        exact = [
            candidate
            for candidate in candidates
            if candidate.kickoff_time == source_time
        ]
        if len(exact) == 1:
            official = exact[0]
        elif len(exact) > 1:
            stats.ambiguous_official_matches += 1
            issues.append(
                {
                    "reason": "ambiguous_official_matches",
                    "source_url": fixture.source_url,
                    "candidate_ids": [
                        item.jleague_match_id
                        for item in exact
                    ],
                }
            )
            continue
        else:
            stats.kickoff_mismatch += 1
            issues.append(
                {
                    "reason": "kickoff_mismatch",
                    "source_url": fixture.source_url,
                    "footystats_time": source_time,
                    "jleague_times": [
                        candidate.kickoff_time
                        for candidate in candidates
                    ],
                    "candidate_ids": [
                        candidate.jleague_match_id
                        for candidate in candidates
                    ],
                }
            )
            if verbose:
                print(
                    "UNRESOLVED kickoff mismatch: "
                    f"{fixture.home_external_name} vs "
                    f"{fixture.away_external_name} "
                    f"FootyStats={source_time}, "
                    "JLeague="
                    f"{[item.kickoff_time for item in candidates]}"
                )
            continue

        resolved.append(
            ResolvedTarget(
                fixture=fixture,
                official=official,
            )
        )

    stats.resolved_targets = len(resolved)
    return resolved, issues


def target_metadata(target: ResolvedTarget) -> str:
    data = {
        "source_file": target.fixture.source_file,
        "source_timestamp": target.fixture.source_timestamp,
        "row_status": target.fixture.row_status,
        "home_external_team_id": (
            target.fixture.home_external_team_id
        ),
        "away_external_team_id": (
            target.fixture.away_external_team_id
        ),
        "home_external_name": (
            target.fixture.home_external_name
        ),
        "away_external_name": (
            target.fixture.away_external_name
        ),
    }
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
    )


def upsert_target(
    connection: sqlite3.Connection,
    target: ResolvedTarget,
    timezone_name: str,
    stats: RegistrationStats,
) -> tuple[int, bool]:
    target_key = (
        "footystats:jleague:"
        f"{target.official.jleague_match_id}"
    )
    scheduled_at = iso_seconds(target.fixture.scheduled_at)

    existing = connection.execute(
        f"""
        SELECT
            snapshot_target_id,
            source_url,
            scheduled_at,
            is_active,
            metadata_json
        FROM {TARGET_TABLE}
        WHERE target_key = ?
        """,
        (target_key,),
    ).fetchone()

    metadata_json = target_metadata(target)
    schedule_changed = False

    if existing is None:
        cursor = connection.execute(
            f"""
            INSERT INTO {TARGET_TABLE} (
                target_key,
                source_name,
                source_url,
                jleague_match_id,
                season,
                league,
                home_team_name,
                away_team_name,
                scheduled_at,
                timezone_name,
                is_active,
                metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                target_key,
                "footystats",
                target.fixture.source_url,
                target.official.jleague_match_id,
                target.official.season,
                target.official.league,
                target.official.home_team_name,
                target.official.away_team_name,
                scheduled_at,
                timezone_name,
                metadata_json,
            ),
        )
        stats.targets_inserted += 1
        return int(cursor.lastrowid), False

    target_id = int(existing["snapshot_target_id"])
    schedule_changed = str(existing["scheduled_at"]) != scheduled_at
    changed = (
        schedule_changed
        or str(existing["source_url"]) != target.fixture.source_url
        or int(existing["is_active"]) != 1
        or str(existing["metadata_json"] or "") != metadata_json
    )

    if changed:
        connection.execute(
            f"""
            UPDATE {TARGET_TABLE}
            SET
                source_name = 'footystats',
                source_url = ?,
                jleague_match_id = ?,
                season = ?,
                league = ?,
                home_team_name = ?,
                away_team_name = ?,
                scheduled_at = ?,
                timezone_name = ?,
                is_active = 1,
                metadata_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE snapshot_target_id = ?
            """,
            (
                target.fixture.source_url,
                target.official.jleague_match_id,
                target.official.season,
                target.official.league,
                target.official.home_team_name,
                target.official.away_team_name,
                scheduled_at,
                timezone_name,
                metadata_json,
                target_id,
            ),
        )
        stats.targets_updated += 1
    else:
        stats.targets_unchanged += 1

    if schedule_changed:
        cursor = connection.execute(
            f"""
            UPDATE {JOB_TABLE}
            SET
                job_status = 'cancelled',
                last_error = 'kickoff time changed',
                updated_at = CURRENT_TIMESTAMP
            WHERE snapshot_target_id = ?
              AND job_status IN ('pending', 'running', 'failed')
            """,
            (target_id,),
        )
        stats.jobs_cancelled_for_reschedule += int(
            cursor.rowcount
        )

    return target_id, schedule_changed


def generate_job_specs(
    scheduled_at: datetime,
    offsets: tuple[int, ...],
    now: datetime,
) -> list[dict[str, object]]:

    descending = sorted(
        set(offsets),
        reverse=True,
    )

    specs: list[
        dict[str, object]
    ] = []

    if not descending:
        return specs

    first_capture_at = (
        scheduled_at
        -
        timedelta(
            hours=descending[0]
        )
    )

    # 72時間前より早く登録された場合、
    # 発表時点スナップショットを即時取得する
    announcement_opens_at = (
        scheduled_at
        -
        timedelta(
            hours=168
        )
    )

    if (
        announcement_opens_at
        <= now
        <
        first_capture_at
    ):

        specs.append(
            {
                "capture_slot":
                    "announcement",
                "anchor_type":
                    "manual",
                "target_capture_at":
                    now,
                "expires_at":
                    first_capture_at,
                "job_status":
                    "pending",
                "last_error":
                    None,
            }
        )

    for index, hours in enumerate(
        descending
    ):

        target_capture_at = (
            scheduled_at
            -
            timedelta(
                hours=hours
            )
        )

        if index + 1 < len(
            descending
        ):

            next_hours = (
                descending[
                    index + 1
                ]
            )

            expires_at = (
                scheduled_at
                -
                timedelta(
                    hours=next_hours
                )
            )

        else:
            expires_at = scheduled_at

        expired = now >= expires_at

        specs.append(
            {
                "capture_slot":
                    f"t{hours:02d}h",
                "anchor_type":
                    "kickoff",
                "target_capture_at":
                    target_capture_at,
                "expires_at":
                    expires_at,
                "job_status":
                    (
                        "skipped"
                        if expired
                        else "pending"
                    ),
                "last_error":
                    (
                        "capture window expired "
                        "before registration"
                        if expired
                        else None
                    ),
            }
        )

    return specs

def insert_jobs(
    connection: sqlite3.Connection,
    target_id: int,
    scheduled_at: datetime,
    offsets: tuple[int, ...],
    now: datetime,
    stats: RegistrationStats,
) -> None:
    for spec in generate_job_specs(
        scheduled_at=scheduled_at,
        offsets=offsets,
        now=now,
    ):
        cursor = connection.execute(
            f"""
            INSERT OR IGNORE INTO {JOB_TABLE} (
                snapshot_target_id,
                capture_slot,
                anchor_type,
                target_capture_at,
                expires_at,
                job_status,
                last_error
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
           (
                target_id,
                spec["capture_slot"],
                spec["anchor_type"],
                iso_seconds(
                    spec[
                        "target_capture_at"
                    ]
                ),
                iso_seconds(
                    spec["expires_at"]
                ),
                spec["job_status"],
                spec["last_error"],
            ),

        )
        if int(cursor.rowcount) == 1:
            stats.jobs_inserted += 1
            if spec["job_status"] == "skipped":
                stats.jobs_marked_skipped += 1
        else:
            stats.jobs_existing += 1


def write_report(
    report_path: Path,
    payload: dict[str, object],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(
        report_path.suffix + ".tmp"
    )
    temporary.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(report_path)


def validate_offsets(values: Iterable[int]) -> tuple[int, ...]:
    offsets = tuple(sorted(set(values), reverse=True))
    if not offsets:
        raise ValueError("capture-hoursが空です。")
    if any(value <= 0 for value in offsets):
        raise ValueError(
            "capture-hoursは正の整数で指定してください。"
        )
    return offsets


def run(args: argparse.Namespace) -> None:
    db_path = resolve_path(args.db)
    html_paths = [resolve_path(path) for path in args.html]
    report_path = (
        resolve_path(args.report)
        if args.report is not None
        else None
    )

    if not db_path.is_file():
        raise FileNotFoundError(f"DBが見つかりません: {db_path}")
    for html_path in html_paths:
        if not html_path.is_file():
            raise FileNotFoundError(
                f"HTMLが見つかりません: {html_path}"
            )

    timezone = ZoneInfo(args.timezone)
    now = (
        parse_iso_datetime(args.now, timezone)
        if args.now
        else datetime.now(timezone)
    )
    offsets = validate_offsets(args.capture_hours)
    stats = RegistrationStats(html_files=len(html_paths))

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    issues: list[dict[str, object]] = []
    registered: list[dict[str, object]] = []

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        validate_schema(connection)

        aliases = load_internal_aliases(connection)
        team_map = load_footystats_team_map(connection)
        official_matches = load_official_matches(
            connection=connection,
            season=args.season,
            league=args.league,
            aliases=aliases,
        )

        fixtures: list[ParsedFixture] = []
        for html_path in html_paths:
            fixtures.extend(
                extract_fixtures(
                    html_path=html_path,
                    timezone=timezone,
                    stats=stats,
                    verbose=args.verbose,
                )
            )
        fixtures = deduplicate_fixtures(fixtures, stats)

        targets, issues = resolve_targets(
            fixtures=fixtures,
            team_map=team_map,
            official_matches=official_matches,
            now=now,
            include_0900=bool(args.include_0900),
            include_past=bool(args.include_past),
            stats=stats,
            verbose=bool(args.verbose),
        )

        connection.execute("BEGIN IMMEDIATE")
        for target in targets:
            target_id, _ = upsert_target(
                connection=connection,
                target=target,
                timezone_name=args.timezone,
                stats=stats,
            )
            insert_jobs(
                connection=connection,
                target_id=target_id,
                scheduled_at=target.fixture.scheduled_at,
                offsets=offsets,
                now=now,
                stats=stats,
            )

            registered.append(
                {
                    "snapshot_target_id": target_id,
                    "jleague_match_id": (
                        target.official.jleague_match_id
                    ),
                    "league": target.official.league,
                    "scheduled_at": iso_seconds(
                        target.fixture.scheduled_at
                    ),
                    "home_team": (
                        target.official.home_team_name
                    ),
                    "away_team": (
                        target.official.away_team_name
                    ),
                    "source_url": target.fixture.source_url,
                }
            )
            if args.verbose:
                print(
                    f"{target.official.jleague_match_id:>6} "
                    f"{target.fixture.scheduled_at:%Y-%m-%d %H:%M} "
                    f"{target.official.home_team_name} vs "
                    f"{target.official.away_team_name}"
                )

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
        if violations:
            raise RuntimeError(
                "外部キー違反が見つかりました: "
                f"{[tuple(row) for row in violations[:5]]}"
            )

        if args.dry_run:
            connection.rollback()
        else:
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    payload: dict[str, object] = {
        "database": str(db_path),
        "season": args.season,
        "league": args.league,
        "timezone": args.timezone,
        "now": iso_seconds(now),
        "capture_hours": list(offsets),
        "dry_run": bool(args.dry_run),
        "html_files": [str(path) for path in html_paths],
        "statistics": asdict(stats),
        "issue_counts": dict(
            sorted(
                Counter(
                    str(item["reason"])
                    for item in issues
                ).items()
            )
        ),
        "issues": issues,
        "registered_targets": registered,
    }

    if report_path is not None:
        write_report(report_path, payload)

    print("=" * 104)
    print("FootyStats Pre-Match Snapshot Target Registration")
    print("=" * 104)
    print(f"database          : {db_path}")
    print(f"season            : {args.season}")
    print(f"league            : {args.league.upper()}")
    print(f"HTML files        : {stats.html_files}")
    print(f"fixture rows      : {stats.fixture_rows}")
    print(f"incomplete rows   : {stats.incomplete_rows}")
    print(f"suspended rows    : {stats.suspended_rows}")
    print(f"unconfirmed times : {stats.unconfirmed_time_rows}")
    print(f"resolved targets  : {stats.resolved_targets}")
    print(f"targets inserted  : {stats.targets_inserted}")
    print(f"targets updated   : {stats.targets_updated}")
    print(f"targets unchanged : {stats.targets_unchanged}")
    print(f"jobs inserted     : {stats.jobs_inserted}")
    print(f"jobs existing     : {stats.jobs_existing}")
    print(f"issues            : {len(issues)}")
    print(f"dry run           : {bool(args.dry_run)}")
    if report_path is not None:
        print(f"report            : {report_path}")
    print()

    if args.dry_run:
        print(
            "RESULT: target/job validation completed; "
            "database unchanged."
        )
    else:
        print(
            "RESULT: FootyStats snapshot targets and jobs "
            "registered."
        )


def main() -> int:
    args = parse_args()
    try:
        run(args)
    except (
        FileNotFoundError,
        RuntimeError,
        ValueError,
        sqlite3.Error,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
