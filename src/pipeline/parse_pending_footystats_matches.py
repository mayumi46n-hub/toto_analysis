# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

PARSER_PATH = (
    PROJECT_ROOT
    / "src/parsers/parse_footystats_match.py"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "ダウンロード済み・未解析のFootyStats試合HTMLを"
            "順番にJSONへ変換します。"
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
        default=1,
        help="今回処理する最大件数。初期値: 1",
    )

    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="parse_status='error'も再試行する",
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
        parse_status
    FROM footystats_match_urls
    WHERE season = ?
      AND download_status = 'downloaded'
      AND parse_status IN ({placeholders})
    ORDER BY footystats_match_url_id
    LIMIT ?
    """

    parameters = (
        season,
        *statuses,
        limit,
    )

    return con.execute(
        sql,
        parameters,
    ).fetchall()


def resolve_project_path(
    value: str,
) -> Path:
    path = Path(value)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def output_json_path(
    season: int,
    match_slug: str,
) -> Path:
    return (
        PROJECT_ROOT
        / "data/parsed/footystats/matches"
        / str(season)
        / f"{match_slug}.json"
    )


def relative_path(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(PROJECT_ROOT)
        )
    except ValueError:
        return str(path)


def validate_parser() -> None:
    if not PARSER_PATH.exists():
        raise FileNotFoundError(
            f"パーサーが見つかりません: {PARSER_PATH}"
        )


def validate_json_output(
    json_path: Path,
) -> tuple[bool, str]:
    if not json_path.exists():
        return (
            False,
            "JSONファイルが生成されていません",
        )

    if not json_path.is_file():
        return (
            False,
            "JSON出力先がファイルではありません",
        )

    try:
        import json

        data = json.loads(
            json_path.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        return (
            False,
            f"JSON読込エラー: {exc}",
        )

    if not isinstance(data, dict):
        return (
            False,
            "JSONルートが辞書ではありません",
        )

    table_count = data.get(
        "table_count"
    )

    metric_row_count = data.get(
        "metric_row_count"
    )

    if not isinstance(
        table_count,
        int,
    ):
        return (
            False,
            "table_countが整数ではありません",
        )

    if not isinstance(
        metric_row_count,
        int,
    ):
        return (
            False,
            "metric_row_countが整数ではありません",
        )

    if table_count <= 0:
        return (
            False,
            f"table_count={table_count}",
        )

    if metric_row_count <= 0:
        return (
            False,
            f"metric_row_count={metric_row_count}",
        )

    return (
        True,
        (
            f"table_count={table_count}, "
            f"metric_row_count={metric_row_count}"
        ),
    )


def mark_parsed(
    con: sqlite3.Connection,
    url_id: int,
    json_path: Path,
) -> None:
    con.execute(
        """
        UPDATE footystats_match_urls
        SET
            json_path = ?,
            parse_status = 'parsed',
            last_error = NULL,
            parsed_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE footystats_match_url_id = ?
        """,
        (
            relative_path(json_path),
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
            parse_status = 'error',
            last_error = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE footystats_match_url_id = ?
        """,
        (
            message[:2000],
            url_id,
        ),
    )


def run_parser(
    html_path: Path,
    json_path: Path,
) -> subprocess.CompletedProcess[str]:
    json_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        sys.executable,
        str(PARSER_PATH),
        str(html_path),
        "--output",
        str(json_path),
    ]

    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def process_target(
    con: sqlite3.Connection,
    target: sqlite3.Row,
) -> str:
    url_id = int(
        target["footystats_match_url_id"]
    )

    season = int(
        target["season"]
    )

    match_slug = str(
        target["match_slug"]
    )

    html_path_value = target[
        "html_path"
    ]

    if not html_path_value:
        message = (
            "html_pathが登録されていません"
        )

        mark_error(
            con=con,
            url_id=url_id,
            message=message,
        )

        con.commit()

        print(f"結果    : error")
        print(f"理由    : {message}")

        return "error"

    html_path = resolve_project_path(
        str(html_path_value)
    )

    json_path = output_json_path(
        season=season,
        match_slug=match_slug,
    )

    print("-" * 110)
    print(f"ID      : {url_id}")
    print(
        f"HTML    : {relative_path(html_path)}"
    )
    print(
        f"JSON    : {relative_path(json_path)}"
    )

    if not html_path.exists():
        message = (
            f"HTMLが見つかりません: "
            f"{relative_path(html_path)}"
        )

        mark_error(
            con=con,
            url_id=url_id,
            message=message,
        )

        con.commit()

        print("結果    : error")
        print(f"理由    : {message}")

        return "error"

    result = run_parser(
        html_path=html_path,
        json_path=json_path,
    )

    if result.returncode != 0:
        error_text = (
            result.stderr.strip()
            or result.stdout.strip()
            or (
                "パーサーが非ゼロ終了しました: "
                f"returncode={result.returncode}"
            )
        )

        mark_error(
            con=con,
            url_id=url_id,
            message=error_text,
        )

        con.commit()

        print("結果    : error")
        print(
            f"理由    : {error_text[:500]}"
        )

        return "error"

    valid, reason = validate_json_output(
        json_path
    )

    if not valid:
        mark_error(
            con=con,
            url_id=url_id,
            message=reason,
        )

        con.commit()

        print("結果    : error")
        print(f"理由    : {reason}")

        return "error"

    mark_parsed(
        con=con,
        url_id=url_id,
        json_path=json_path,
    )

    con.commit()

    print("結果    : parsed")
    print(f"検証    : {reason}")

    return "parsed"


def print_database_summary(
    con: sqlite3.Connection,
    season: int,
) -> None:
    rows = con.execute(
        """
        SELECT
            parse_status,
            COUNT(*) AS count
        FROM footystats_match_urls
        WHERE season = ?
        GROUP BY parse_status
        ORDER BY parse_status
        """,
        (season,),
    ).fetchall()

    print()
    print("DATABASE STATUS")
    print("-" * 110)

    for row in rows:
        print(
            f"{row['parse_status']:<15}"
            f": {row['count']}"
        )


def main() -> None:
    args = parse_args()

    validate_parser()

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
            "FootyStats Pending Match Parser"
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
            f"retry errors     : "
            f"{args.retry_errors}"
        )

        if not targets:
            print()
            print(
                "解析対象はありません。"
            )

            print_database_summary(
                con=con,
                season=args.season,
            )

            return

        parsed = 0
        errors = 0

        for index, target in enumerate(
            targets,
            start=1,
        ):
            print()
            print(
                f"[{index}/{len(targets)}]"
            )

            status = process_target(
                con=con,
                target=target,
            )

            if status == "parsed":
                parsed += 1
            else:
                errors += 1

        print()
        print("RUN SUMMARY")
        print("-" * 110)
        print(
            f"parsed           : {parsed}"
        )
        print(
            f"errors           : {errors}"
        )

        print_database_summary(
            con=con,
            season=args.season,
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()
