# -*- coding: utf-8 -*-

"""
FootyStats Match Page Downloader

footystats_match_urls の download_status='pending' のURLを取得し、
HTMLファイルとして保存する。

主な仕様:
- 初期値では1件だけ取得する
- 取得成功時は download_status='downloaded'
- 失敗時は download_status='error'
- html_path、downloaded_at、last_errorを更新
- 既存HTMLが正常なら再ダウンロードせずDB状態だけ修復可能
- サーバー負荷を避けるため、取得間隔を設定する
- ログイン回避やアクセス制限回避は行わない
"""

from __future__ import annotations

import argparse
import random
import sqlite3
import ssl
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

DEFAULT_LIMIT = 1
DEFAULT_DELAY = 5.0
DEFAULT_TIMEOUT = 60

USER_AGENT = (
    "Mozilla/5.0 "
    "(Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "footystats_match_urlsの未取得URLを"
            "HTMLとして保存します。"
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        default=2026,
        help="対象シーズン。初期値: 2026",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="今回取得する最大件数。初期値: 1",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="取得間隔の秒数。初期値: 5.0",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTPタイムアウト秒数。初期値: 60",
    )

    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="download_status='error'も再試行対象にする",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="既存HTMLがあっても再取得する",
    )

    return parser.parse_args()


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    return con


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def output_path_for(
    season: int,
    match_slug: str,
) -> Path:
    return (
        PROJECT_ROOT
        / "data/raw/footystats/matches"
        / str(season)
        / f"{match_slug}.html"
    )


def load_targets(
    con: sqlite3.Connection,
    season: int,
    limit: int,
    retry_errors: bool,
) -> list[sqlite3.Row]:
    if limit <= 0:
        raise ValueError(
            "--limitは1以上で指定してください"
        )

    statuses = ["pending"]

    if retry_errors:
        statuses.append("error")

    placeholders = ", ".join(
        "?"
        for _ in statuses
    )

    sql = f"""
        SELECT
            footystats_match_url_id,
            season,
            match_slug,
            source_url,
            html_path,
            download_status
        FROM footystats_match_urls
        WHERE season = ?
          AND download_status IN ({placeholders})
        ORDER BY footystats_match_url_id
        LIMIT ?
    """

    parameters: list[Any] = [
        season,
        *statuses,
        limit,
    ]

    return con.execute(
        sql,
        tuple(parameters),
    ).fetchall()


def looks_like_valid_footystats_html(
    body: bytes,
) -> tuple[bool, str]:
    if len(body) < 10_000:
        return (
            False,
            f"HTMLサイズが小さすぎます: {len(body):,} bytes",
        )

    text = body.decode(
        "utf-8",
        errors="replace",
    )

    lowered = text.lower()

    required_any = (
        "footystats",
        "-h2h-stats",
        "comparison-table-table",
        "stat-group",
    )

    if not any(
        marker in lowered
        for marker in required_any
    ):
        return (
            False,
            "FootyStats試合ページらしい内容を確認できません",
        )

    blocked_markers = (
        "captcha",
        "access denied",
        "cloudflare challenge",
        "verify you are human",
    )

    for marker in blocked_markers:
        if marker in lowered:
            return (
                False,
                f"アクセス確認ページの可能性があります: {marker}",
            )

    return True, "ok"


def read_existing_file(
    path: Path,
) -> tuple[bool, str]:
    if not path.exists():
        return False, "file_not_found"

    if not path.is_file():
        return False, "not_a_file"

    try:
        body = path.read_bytes()
    except OSError as exc:
        return False, str(exc)

    return looks_like_valid_footystats_html(
        body
    )


def download_html(
    url: str,
    timeout: int,
) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": (
                "ja,en-US;q=0.9,en;q=0.8"
            ),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )

    context = ssl.create_default_context()

    with urlopen(
        request,
        context=context,
        timeout=timeout,
    ) as response:
        status = getattr(
            response,
            "status",
            None,
        )

        if status is not None and status != 200:
            raise RuntimeError(
                f"HTTP status={status}"
            )

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if (
            content_type
            and "text/html" not in content_type.lower()
            and "application/xhtml+xml"
            not in content_type.lower()
        ):
            raise RuntimeError(
                "HTML以外のContent-Typeです: "
                f"{content_type}"
            )

        return response.read()


def write_html_atomically(
    output_path: Path,
    body: bytes,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = output_path.with_suffix(
        ".html.tmp"
    )

    temporary_path.write_bytes(
        body
    )

    temporary_path.replace(
        output_path
    )


def mark_downloaded(
    con: sqlite3.Connection,
    url_id: int,
    html_path: Path,
) -> None:
    con.execute(
        """
        UPDATE footystats_match_urls
        SET
            html_path = ?,
            download_status = 'downloaded',
            last_error = NULL,
            downloaded_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE footystats_match_url_id = ?
        """,
        (
            relative_path(html_path),
            url_id,
        ),
    )


def mark_error(
    con: sqlite3.Connection,
    url_id: int,
    message: str,
) -> None:
    con.execute(
        """
        UPDATE footystats_match_urls
        SET
            download_status = 'error',
            last_error = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE footystats_match_url_id = ?
        """,
        (
            message[:2000],
            url_id,
        ),
    )


def process_target(
    con: sqlite3.Connection,
    target: sqlite3.Row,
    timeout: int,
    overwrite: bool,
) -> tuple[str, int]:
    url_id = int(
        target["footystats_match_url_id"]
    )

    season = int(
        target["season"]
    )

    match_slug = str(
        target["match_slug"]
    )

    source_url = str(
        target["source_url"]
    )

    output_path = output_path_for(
        season=season,
        match_slug=match_slug,
    )

    print("-" * 110)
    print(f"ID      : {url_id}")
    print(f"URL     : {source_url}")
    print(
        f"保存先  : {relative_path(output_path)}"
    )

    if not overwrite:
        existing_valid, existing_reason = (
            read_existing_file(
                output_path
            )
        )

        if existing_valid:
            mark_downloaded(
                con=con,
                url_id=url_id,
                html_path=output_path,
            )

            con.commit()

            size = output_path.stat().st_size

            print(
                "結果    : 既存の正常HTMLを使用"
            )
            print(
                f"サイズ  : {size:,} bytes"
            )

            return "existing", size

        if output_path.exists():
            print(
                "既存HTML: 無効 "
                f"({existing_reason})"
            )

    try:
        body = download_html(
            url=source_url,
            timeout=timeout,
        )

        valid, reason = (
            looks_like_valid_footystats_html(
                body
            )
        )

        if not valid:
            raise RuntimeError(reason)

        write_html_atomically(
            output_path=output_path,
            body=body,
        )

        mark_downloaded(
            con=con,
            url_id=url_id,
            html_path=output_path,
        )

        con.commit()

        print("結果    : downloaded")
        print(
            f"サイズ  : {len(body):,} bytes"
        )

        return "downloaded", len(body)

    except HTTPError as exc:
        message = (
            f"HTTPError: status={exc.code}, "
            f"reason={exc.reason}"
        )

    except URLError as exc:
        message = (
            f"URLError: {exc.reason}"
        )

    except TimeoutError:
        message = "TimeoutError"

    except Exception as exc:
        message = (
            f"{type(exc).__name__}: {exc}"
        )

    mark_error(
        con=con,
        url_id=url_id,
        message=message,
    )

    con.commit()

    print(f"結果    : error")
    print(f"理由    : {message}")

    return "error", 0


def print_database_summary(
    con: sqlite3.Connection,
    season: int,
) -> None:
    rows = con.execute(
        """
        SELECT
            download_status,
            COUNT(*) AS count
        FROM footystats_match_urls
        WHERE season = ?
        GROUP BY download_status
        ORDER BY download_status
        """,
        (season,),
    ).fetchall()

    print()
    print("DATABASE STATUS")
    print("-" * 110)

    for row in rows:
        print(
            f"{row['download_status']:<15} "
            f": {row['count']}"
        )


def main() -> None:
    args = parse_args()

    if args.delay < 0:
        raise ValueError(
            "--delayは0以上で指定してください"
        )

    con = connect_database()

    try:
        targets = load_targets(
            con=con,
            season=args.season,
            limit=args.limit,
            retry_errors=args.retry_errors,
        )

        print("=" * 110)
        print(
            "FootyStats Match Page Downloader"
        )
        print("=" * 110)
        print(
            f"season          : {args.season}"
        )
        print(
            f"target count     : {len(targets)}"
        )
        print(
            f"limit            : {args.limit}"
        )
        print(
            f"delay            : {args.delay} sec"
        )
        print(
            f"retry errors     : {args.retry_errors}"
        )
        print(
            f"overwrite        : {args.overwrite}"
        )

        if not targets:
            print()
            print(
                "取得対象はありません。"
            )
            print_database_summary(
                con=con,
                season=args.season,
            )
            return

        downloaded = 0
        existing = 0
        errors = 0
        total_bytes = 0

        for index, target in enumerate(
            targets,
            start=1,
        ):
            print()
            print(
                f"[{index}/{len(targets)}]"
            )

            status, size = process_target(
                con=con,
                target=target,
                timeout=args.timeout,
                overwrite=args.overwrite,
            )

            total_bytes += size

            if status == "downloaded":
                downloaded += 1
            elif status == "existing":
                existing += 1
            else:
                errors += 1

            if (
                index < len(targets)
                and args.delay > 0
            ):
                wait_seconds = (
                    args.delay
                    + random.uniform(0.0, 1.0)
                )

                print(
                    f"待機    : "
                    f"{wait_seconds:.1f}秒"
                )

                time.sleep(
                    wait_seconds
                )

        print()
        print("RUN SUMMARY")
        print("-" * 110)
        print(
            f"downloaded       : {downloaded}"
        )
        print(
            f"existing         : {existing}"
        )
        print(
            f"errors            : {errors}"
        )
        print(
            f"total bytes       : "
            f"{total_bytes:,}"
        )

        print_database_summary(
            con=con,
            season=args.season,
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()