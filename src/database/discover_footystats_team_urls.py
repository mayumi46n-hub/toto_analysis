# -*- coding: utf-8 -*-
"""
FootyStatsクラブURL探索・team_source_map登録ツール

デフォルトはdry-runです。DBへ登録する場合だけ --apply を付けます。

使用例:
    python src/database/discover_footystats_team_urls.py
    python src/database/discover_footystats_team_urls.py --team 仙台
    python src/database/discover_footystats_team_urls.py --apply

依存:
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sqlite3
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "toto.db"
SOURCE_NAME = "footystats"
BASE_URL = "https://footystats.org"
SEARCH_URL = "https://html.duckduckgo.com/html/"
REQUEST_TIMEOUT = 20
REQUEST_DELAY_SECONDS = 1.2
MAX_SEARCH_RESULTS = 10
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)

FALLBACK_2025_MISSING_TEAMS = (
    (2, "いわき"), (4, "今治"), (5, "仙台"), (9, "大分"),
    (10, "大宮"), (16, "徳島"), (18, "札幌"), (21, "横浜FC"),
    (27, "甲府"), (29, "磐田"), (32, "秋田"), (33, "藤枝"),
    (37, "鳥栖"), (95, "山口"), (96, "山形"), (99, "愛媛"),
    (100, "新潟"), (103, "湘南"), (104, "熊本"),
)

TEAM_SEARCH_ALIASES = {
    "いわき": ("Iwaki FC", "Iwaki"),
    "今治": ("FC Imabari", "Imabari"),
    "仙台": ("Vegalta Sendai",),
    "大分": ("Oita Trinita",),
    "大宮": ("Omiya Ardija", "RB Omiya Ardija"),
    "徳島": ("Tokushima Vortis",),
    "札幌": ("Consadole Sapporo", "Hokkaido Consadole Sapporo"),
    "横浜FC": ("Yokohama FC",),
    "甲府": ("Ventforet Kofu",),
    "磐田": ("Jubilo Iwata",),
    "秋田": ("Blaublitz Akita",),
    "藤枝": ("Fujieda MYFC",),
    "鳥栖": ("Sagan Tosu",),
    "山口": ("Renofa Yamaguchi", "Renofa Yamaguchi FC"),
    "山形": ("Montedio Yamagata",),
    "愛媛": ("Ehime FC",),
    "新潟": ("Albirex Niigata",),
    "湘南": ("Shonan Bellmare",),
    "熊本": ("Roasso Kumamoto",),
}

KNOWN_CANDIDATES = {
    "今治": ("https://footystats.org/jp/clubs/fc-imabari-8118",),
    "仙台": ("https://footystats.org/jp/clubs/vegalta-sendai-1009",),
    "大分": ("https://footystats.org/jp/clubs/oita-trinita-875",),
    "新潟": ("https://footystats.org/jp/clubs/albirex-niigata-1011",),
    "湘南": ("https://footystats.org/jp/clubs/shonan-bellmare-879",),
}


@dataclass(frozen=True)
class Team:
    team_id: int
    team_name: str


@dataclass(frozen=True)
class Candidate:
    team: Team
    url: str
    external_team_id: str
    external_name: str
    page_title: str
    score: int
    source: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="未登録のFootyStatsクラブURLを探索し、team_source_mapへ登録します。"
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--team", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--no-web-search", action="store_true")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY_SECONDS)
    parser.add_argument("--min-score", type=int, default=70)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龠]+", "", value)


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone() is not None


def table_columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()]


def detect_team_table(conn: sqlite3.Connection):
    for table, id_col, name_col in (
        ("team_master", "team_id", "team_name"),
        ("teams", "team_id", "team_name"),
        ("team", "team_id", "team_name"),
    ):
        if table_exists(conn, table):
            cols = set(table_columns(conn, table))
            if {id_col, name_col}.issubset(cols):
                return table, id_col, name_col
    return None


def load_unmapped_teams(conn: sqlite3.Connection, season: int) -> list[Team]:
    if not table_exists(conn, "team_source_map"):
        raise RuntimeError("team_source_map テーブルが見つかりません。")

    detected = detect_team_table(conn)
    if detected is None:
        return [Team(i, n) for i, n in FALLBACK_2025_MISSING_TEAMS]

    team_table, id_col, name_col = detected

    if season == 2025:
        target_ids = [i for i, _ in FALLBACK_2025_MISSING_TEAMS]
        placeholders = ",".join("?" for _ in target_ids)
        sql = f'''
            SELECT t."{id_col}" AS team_id, t."{name_col}" AS team_name
            FROM "{team_table}" t
            WHERE t."{id_col}" IN ({placeholders})
              AND NOT EXISTS (
                  SELECT 1 FROM team_source_map m
                  WHERE m.team_id=t."{id_col}"
                    AND lower(m.source_name)=lower(?)
              )
            ORDER BY t."{id_col}"
        '''
        rows = conn.execute(sql, (*target_ids, SOURCE_NAME)).fetchall()
        found = [Team(int(r["team_id"]), str(r["team_name"])) for r in rows]
        found_ids = {t.team_id for t in found}
        for team_id, team_name in FALLBACK_2025_MISSING_TEAMS:
            if team_id in found_ids:
                continue
            exists = conn.execute(
                "SELECT 1 FROM team_source_map WHERE team_id=? AND lower(source_name)=lower(?)",
                (team_id, SOURCE_NAME),
            ).fetchone()
            if exists is None:
                found.append(Team(team_id, team_name))
        return sorted(found, key=lambda x: x.team_id)

    sql = f'''
        SELECT t."{id_col}" AS team_id, t."{name_col}" AS team_name
        FROM "{team_table}" t
        WHERE NOT EXISTS (
            SELECT 1 FROM team_source_map m
            WHERE m.team_id=t."{id_col}"
              AND lower(m.source_name)=lower(?)
        )
        ORDER BY t."{id_col}"
    '''
    rows = conn.execute(sql, (SOURCE_NAME,)).fetchall()
    return [Team(int(r["team_id"]), str(r["team_name"])) for r in rows]


def filter_teams(teams: list[Team], selectors: list[str]) -> list[Team]:
    if not selectors:
        return teams
    result = []
    wanted = {normalize_text(x) for x in selectors}
    for team in teams:
        if str(team.team_id) in selectors or normalize_text(team.team_name) in wanted:
            result.append(team)
    return result


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
        "Accept": "text/html,application/xhtml+xml",
    })
    return session


def canonicalize_footystats_url(raw_url: str) -> str | None:
    raw_url = html.unescape(raw_url.strip())
    parsed = urlparse(raw_url)
    if "duckduckgo.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if query.get("uddg"):
            raw_url = unquote(query["uddg"][0])
            parsed = urlparse(raw_url)

    if parsed.netloc.lower() not in {"footystats.org", "www.footystats.org"}:
        return None
    match = re.search(r"/(?:jp/)?clubs/([^/?#]+-\d+)", parsed.path)
    if not match:
        return None
    return f"{BASE_URL}/jp/clubs/{match.group(1).rstrip('/')}"


def extract_external_id(url: str) -> str:
    match = re.search(r"-(\d+)$", url.rstrip("/"))
    if not match:
        raise ValueError(f"external_team_idを取得できません: {url}")
    return match.group(1)


def search_web(session: requests.Session, team: Team, delay: float) -> list[str]:
    urls = []
    seen = set()
    names = TEAM_SEARCH_ALIASES.get(team.team_name, (team.team_name,))
    for name in names:
        query = f'site:footystats.org/clubs "{name}" FootyStats'
        response = session.get(SEARCH_URL, params={"q": query}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("a[href]"):
            href = link.get("href")
            if not isinstance(href, str):
                continue
            canonical = canonicalize_footystats_url(href)
            if canonical and canonical not in seen:
                seen.add(canonical)
                urls.append(canonical)
                if len(urls) >= MAX_SEARCH_RESULTS:
                    return urls
        time.sleep(max(delay, 0.0))
    return urls


def title_to_name(title: str) -> str:
    value = re.sub(r"\s*[|\-]\s*FootyStats.*$", "", title, flags=re.I)
    value = re.sub(r"\s+(Stats|スタッツ).*$", "", value, flags=re.I)
    return value.strip()


def score_candidate(
    team: Team,
    external_name: str,
    title: str,
    url: str,
) -> int:
    targets = [
        team.team_name,
        *TEAM_SEARCH_ALIASES.get(team.team_name, ()),
    ]
    values = [
        external_name,
        title,
        url.rsplit("/", 1)[-1],
    ]

    best = 0

    for target in targets:
        nt = normalize_text(target)

        for value in values:
            nv = normalize_text(value)

            if nt and nt == nv:
                best = max(best, 100)

            elif nt and (nt in nv or nv in nt):
                best = max(best, 90)

            else:
                target_tokens = set(
                    re.findall(r"[a-z0-9]+", target.casefold())
                )
                value_tokens = set(
                    re.findall(r"[a-z0-9]+", value.casefold())
                )

                if target_tokens:
                    token_score = int(
                        len(target_tokens & value_tokens)
                        / len(target_tokens)
                        * 80
                    )
                    best = max(best, token_score)

    excluded_markers = (
        "ladies",
        "lady",
        "women",
        "woman",
        "womens",
        "female",
        "レディース",
        "女子",
        "academy",
        "アカデミー",
        "youth",
        "ユース",
        "u18",
        "u-18",
        "u23",
        "u-23",
        "reserve",
        "reserves",
        "リザーブ",
    )

    candidate_text = " ".join(
        [
            external_name,
            title,
            url,
        ]
    ).casefold()

    normalized_candidate_text = normalize_text(candidate_text)

    has_excluded_marker = any(
        marker.casefold() in candidate_text
        or normalize_text(marker) in normalized_candidate_text
        for marker in excluded_markers
    )

    if has_excluded_marker:
        best = max(0, best - 70)

    return best


    excluded_markers = (
        "ladies",
        "lady",
        "women",
        "woman",
        "womens",
        "female",
        "レディース",
        "女子",
        "academy",
        "アカデミー",
        "youth",
        "ユース",
        "u18",
        "u-18",
        "u23",
        "u-23",
        "reserve",
        "reserves",
        "リザーブ",
    )

    candidate_text = " ".join(
        [
            external_name,
            title,
            url,
        ]
    ).casefold()

    normalized_candidate_text = normalize_text(candidate_text)

    has_excluded_marker = any(
        marker.casefold() in candidate_text
        or normalize_text(marker) in normalized_candidate_text
        for marker in excluded_markers
    )

    if has_excluded_marker:
        best = max(0, best - 70)

    return best


def validate_candidate(
    session: requests.Session,
    team: Team,
    url: str,
    source: str,
) -> Candidate | None:
    canonical = canonicalize_footystats_url(url)
    if not canonical:
        return None
    response = session.get(canonical, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    if response.status_code != 200:
        return None
    final_url = canonicalize_footystats_url(response.url) or canonical
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    h1 = soup.find("h1")
    external_name = h1.get_text(" ", strip=True) if h1 else title_to_name(title)
    if not external_name or "404" in title or "Page Not Found" in title:
        return None
    return Candidate(
        team=team,
        url=final_url,
        external_team_id=extract_external_id(final_url),
        external_name=external_name,
        page_title=title,
        score=score_candidate(team, external_name, title, final_url),
        source=source,
    )


def discover_team(
    session: requests.Session,
    team: Team,
    no_web_search: bool,
    delay: float,
    verbose: bool,
) -> list[Candidate]:
    urls = []
    seen = set()
    for url in KNOWN_CANDIDATES.get(team.team_name, ()):
        canonical = canonicalize_footystats_url(url)
        if canonical and canonical not in seen:
            seen.add(canonical)
            urls.append((canonical, "known"))

    if not no_web_search:
        try:
            for url in search_web(session, team, delay):
                if url not in seen:
                    seen.add(url)
                    urls.append((url, "search"))
        except requests.RequestException as exc:
            print(f"    WARNING: Web検索失敗: {exc}")

    candidates = []
    for url, source in urls:
        try:
            candidate = validate_candidate(session, team, url, source)
            if candidate:
                candidates.append(candidate)
                if verbose:
                    print(
                        f"    score={candidate.score:3d} id={candidate.external_team_id:<7} "
                        f"name={candidate.external_name} url={candidate.url}"
                    )
        except (requests.RequestException, ValueError) as exc:
            if verbose:
                print(f"    reject: {url} ({exc})")
        time.sleep(max(delay, 0.0))

    unique = {}
    for candidate in candidates:
        old = unique.get(candidate.external_team_id)
        if old is None or candidate.score > old.score:
            unique[candidate.external_team_id] = candidate
    return sorted(unique.values(), key=lambda c: (-c.score, c.external_team_id))


def choose_candidate(candidates: list[Candidate], min_score: int):
    if not candidates:
        return None, "候補なし"
    best = candidates[0]
    if best.score < min_score:
        return None, f"最高スコア不足 ({best.score} < {min_score})"
    if len(candidates) >= 2 and candidates[1].score == best.score:
        return None, f"同点候補あり ({best.score})"
    return best, "確定"


def backup_database(db_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.stem}.backup_{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    return backup


def insert_mapping(conn: sqlite3.Connection, candidate: Candidate) -> None:
    columns = set(table_columns(conn, "team_source_map"))
    values = {
        "team_id": candidate.team.team_id,
        "source_name": SOURCE_NAME,
        "external_team_id": candidate.external_team_id,
        "external_name": candidate.external_name,
        "source_url": candidate.url,
    }
    now = datetime.now().isoformat(timespec="seconds")
    if "created_at" in columns:
        values["created_at"] = now
    if "updated_at" in columns:
        values["updated_at"] = now

    values = {k: v for k, v in values.items() if k in columns}
    required = {"team_id", "source_name", "external_team_id"}
    if not required.issubset(values):
        raise RuntimeError(f"team_source_map列不足: {sorted(columns)}")

    exists = conn.execute(
        "SELECT 1 FROM team_source_map WHERE team_id=? AND lower(source_name)=lower(?)",
        (candidate.team.team_id, SOURCE_NAME),
    ).fetchone()
    if exists:
        return

    names = list(values)
    cols = ", ".join(f'"{name}"' for name in names)
    marks = ", ".join("?" for _ in names)
    conn.execute(
        f"INSERT INTO team_source_map ({cols}) VALUES ({marks})",
        tuple(values[name] for name in names),
    )


def main() -> int:
    args = parse_args()
    db_path = resolve_path(args.db)
    if not db_path.exists():
        print(f"ERROR: DBが見つかりません: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        teams = filter_teams(load_unmapped_teams(conn, args.season), args.team)
        print("=" * 120)
        print("FootyStats Team URL Discovery")
        print("=" * 120)
        print(f"database : {db_path}")
        print(f"season   : {args.season}")
        print(f"mode     : {'APPLY' if args.apply else 'DRY-RUN'}")
        print(f"targets  : {len(teams)}")
        print("-" * 120)

        if not teams:
            print("対象となる未登録クラブはありません。")
            return 0

        session = make_session()
        confirmed = []
        unresolved = []

        for index, team in enumerate(teams, 1):
            print(f"[{index:02d}/{len(teams):02d}] {team.team_id:>4}  {team.team_name}")
            candidates = discover_team(
                session, team, args.no_web_search, args.delay, args.verbose
            )
            chosen, reason = choose_candidate(candidates, args.min_score)
            if chosen is None:
                unresolved.append((team, reason))
                print(f"    RESULT: unresolved - {reason}")
                for candidate in candidates[:3]:
                    print(
                        f"      score={candidate.score:3d} id={candidate.external_team_id:<7} "
                        f"name={candidate.external_name}"
                    )
                    print(f"      {candidate.url}")
            else:
                confirmed.append(chosen)
                print(
                    f"    RESULT: confirmed score={chosen.score} "
                    f"external_id={chosen.external_team_id}"
                )
                print(f"      name: {chosen.external_name}")
                print(f"      url : {chosen.url}")

        print("\n" + "=" * 120)
        print("SUMMARY")
        print("=" * 120)
        print(f"CONFIRMED  : {len(confirmed)}")
        print(f"UNRESOLVED : {len(unresolved)}")

        if not args.apply:
            print("\nDRY-RUN: DBは変更していません。")
            print("確認後、登録する場合は --apply を付けて再実行してください。")
            return 0

        if not confirmed:
            print("登録可能な候補がないため、DBは変更していません。")
            return 1

        if not args.no_backup:
            print(f"DB BACKUP: {backup_database(db_path)}")

        conn.execute("BEGIN")
        for candidate in confirmed:
            insert_mapping(conn, candidate)
        conn.commit()
        print(f"APPLIED: {len(confirmed)}件を登録しました。")
        if unresolved:
            print(f"未解決の{len(unresolved)}件は登録していません。")
        return 0

    except KeyboardInterrupt:
        conn.rollback()
        print("\n中断しました。")
        return 130
    except Exception as exc:
        conn.rollback()
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
