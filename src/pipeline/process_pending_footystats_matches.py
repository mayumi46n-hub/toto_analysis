# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"

ENRICH_SCRIPT = (
    PROJECT_ROOT
    / "src/pipeline/enrich_footystats_match.py"
)

IMPORT_SCRIPT = (
    PROJECT_ROOT
    / "src/pipeline/import_footystats_match.py"
)

LINK_SCRIPT = (
    PROJECT_ROOT
    / "src/database/link_footystats_jleague_match.py"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "解析済みFootyStats試合JSONを補完・取込し、"
            "Jリーグ公式試合へリンクします。"
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="対象シーズン",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="最大処理件数。初期値: 1",
    )

    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="import_status='error'も再試行する",
    )

    return parser.parse_args()


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    return con


def project_path(value: str | Path) -> Path:
    path = Path(value)

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def validate_scripts() -> None:
    scripts = (
        ENRICH_SCRIPT,
        IMPORT_SCRIPT,
        LINK_SCRIPT,
    )

    missing = [
        str(path)
        for path in scripts
        if not path.is_file()
    ]

    if missing:
        raise FileNotFoundError(
            "必要なスクリプトがありません:\n"
            + "\n".join(missing)
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
        json_path,
        import_status,
        link_status
    FROM footystats_match_urls
    WHERE season = ?
      AND download_status = 'downloaded'
      AND parse_status = 'parsed'
      AND import_status IN ({placeholders})
    ORDER BY footystats_match_url_id
    LIMIT ?
    """

    parameters: tuple[Any, ...] = (
        season,
        *statuses,
        limit,
    )

    return con.execute(
        sql,
        parameters,
    ).fetchall()


def run_command(
    command: list[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def command_error(
    result: subprocess.CompletedProcess[str],
) -> str:
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()

    if stderr:
        return stderr

    if stdout:
        return stdout

    return (
        "コマンドが非ゼロ終了しました: "
        f"returncode={result.returncode}"
    )


def load_json(
    json_path: Path,
) -> dict[str, Any]:
    if not json_path.is_file():
        raise FileNotFoundError(
            f"JSONが見つかりません: {json_path}"
        )

    data = json.loads(
        json_path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "JSONルートが辞書ではありません"
        )

    return data


def page_columns(
    con: sqlite3.Connection,
) -> set[str]:
    return {
        str(row[1])
        for row in con.execute(
            """
            PRAGMA table_info(
                footystats_match_pages
            )
            """
        ).fetchall()
    }


def find_imported_page(
    con: sqlite3.Connection,
    json_path: Path,
    data: dict[str, Any],
) -> sqlite3.Row | None:
    columns = page_columns(con)

    json_file = relative_path(json_path)

    if "json_file" in columns:
        row = con.execute(
            """
            SELECT
                id,
                jleague_match_id
            FROM footystats_match_pages
            WHERE json_file = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (json_file,),
        ).fetchone()

        if row is not None:
            return row

    required_columns = {
        "match_date",
        "home_external_team_id",
        "away_external_team_id",
    }

    if required_columns.issubset(
        columns
    ):
        row = con.execute(
            """
            SELECT
                id,
                jleague_match_id
            FROM footystats_match_pages
            WHERE match_date = ?
              AND CAST(
                    home_external_team_id AS TEXT
                  ) = ?
              AND CAST(
                    away_external_team_id AS TEXT
                  ) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                str(data["match_date"]),
                str(
                    data[
                        "home_external_team_id"
                    ]
                ),
                str(
                    data[
                        "away_external_team_id"
                    ]
                ),
            ),
        ).fetchone()

        if row is not None:
            return row

    if {
        "match_date",
        "home_team_id",
        "away_team_id",
    }.issubset(columns):
        home_team_id = resolve_team_id(
            con=con,
            external_team_id=str(
                data["home_external_team_id"]
            ),
        )

        away_team_id = resolve_team_id(
            con=con,
            external_team_id=str(
                data["away_external_team_id"]
            ),
        )

        if (
            home_team_id is not None
            and away_team_id is not None
        ):
            return con.execute(
                """
                SELECT
                    id,
                    jleague_match_id
                FROM footystats_match_pages
                WHERE match_date = ?
                  AND home_team_id = ?
                  AND away_team_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    str(data["match_date"]),
                    home_team_id,
                    away_team_id,
                ),
            ).fetchone()

    return None


def resolve_team_id(
    con: sqlite3.Connection,
    external_team_id: str,
) -> int | None:
    row = con.execute(
        """
        SELECT team_id
        FROM team_source_map
        WHERE source_name = 'footystats'
          AND CAST(external_team_id AS TEXT) = ?
        ORDER BY is_primary DESC,
                 team_source_map_id
        LIMIT 1
        """,
        (external_team_id,),
    ).fetchone()

    if row is None:
        return None

    return int(row["team_id"])


def mark_imported(
    con: sqlite3.Connection,
    url_id: int,
    page_id: int,
) -> None:
    con.execute(
        """
        UPDATE footystats_match_urls
        SET
            import_status = 'imported',
            footystats_page_id = ?,
            last_error = NULL,
            imported_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE footystats_match_url_id = ?
        """,
        (
            page_id,
            url_id,
        ),
    )


def mark_import_error(
    con: sqlite3.Connection,
    url_id: int,
    message: str,
) -> None:
    con.execute(
        """
        UPDATE footystats_match_urls
        SET
            import_status = 'error',
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
) -> bool:
    url_id = int(
        target["footystats_match_url_id"]
    )

    html_value = target["html_path"]
    json_value = target["json_path"]

    print("-" * 110)
    print(f"URL ID  : {url_id}")
    print(f"SLUG    : {target['match_slug']}")

    if not html_value:
        message = "html_pathが空です"

        mark_import_error(
            con,
            url_id,
            message,
        )

        con.commit()

        print("結果    : error")
        print(f"理由    : {message}")

        return False

    if not json_value:
        message = "json_pathが空です"

        mark_import_error(
            con,
            url_id,
            message,
        )

        con.commit()

        print("結果    : error")
        print(f"理由    : {message}")

        return False

    html_path = project_path(
        str(html_value)
    )

    json_path = project_path(
        str(json_value)
    )

    print(
        f"HTML    : "
        f"{relative_path(html_path)}"
    )
    print(
        f"JSON    : "
        f"{relative_path(json_path)}"
    )

    try:
        enrich_command = [
            sys.executable,
            str(ENRICH_SCRIPT),
            "--html",
            str(html_path),
            "--json",
            str(json_path),
        ]

        enrich_result = run_command(
            enrich_command
        )

        if enrich_result.returncode != 0:
            raise RuntimeError(
                "Enrich失敗:\n"
                + command_error(
                    enrich_result
                )
            )

        data = load_json(
            json_path
        )

        import_command = [
            sys.executable,
            str(IMPORT_SCRIPT),
            "--json",
            str(json_path),
        ]

        import_result = run_command(
            import_command
        )

        if import_result.returncode != 0:
            raise RuntimeError(
                "Import失敗:\n"
                + command_error(
                    import_result
                )
            )

        page = find_imported_page(
            con=con,
            json_path=json_path,
            data=data,
        )

        if page is None:
            raise RuntimeError(
                "インポート後の"
                "footystats_match_pagesを"
                "特定できません"
            )

        page_id = int(
            page["id"]
        )

        mark_imported(
            con=con,
            url_id=url_id,
            page_id=page_id,
        )

        con.commit()

        print("結果    : imported")
        print(
            f"page_id : {page_id}"
        )

        return True

    except Exception as exc:
        message = (
            f"{type(exc).__name__}: {exc}"
        )

        mark_import_error(
            con=con,
            url_id=url_id,
            message=message,
        )

        con.commit()

        print("結果    : error")
        print(
            f"理由    : {message[:800]}"
        )

        return False


def run_linker() -> None:
    result = run_command(
        [
            sys.executable,
            str(LINK_SCRIPT),
        ]
    )

    if result.stdout.strip():
        print(
            result.stdout.strip()
        )

    if result.returncode != 0:
        raise RuntimeError(
            "公式試合リンカー失敗:\n"
            + command_error(result)
        )


def refresh_link_statuses(
    con: sqlite3.Connection,
    season: int,
) -> tuple[int, int]:
    rows = con.execute(
        """
        SELECT
            u.footystats_match_url_id,
            u.footystats_page_id,
            p.jleague_match_id
        FROM footystats_match_urls AS u
        LEFT JOIN footystats_match_pages AS p
          ON p.id = u.footystats_page_id
        WHERE u.season = ?
          AND u.import_status = 'imported'
        ORDER BY u.footystats_match_url_id
        """,
        (season,),
    ).fetchall()

    linked = 0
    not_found = 0

    for row in rows:
        url_id = int(
            row["footystats_match_url_id"]
        )

        jleague_match_id = row[
            "jleague_match_id"
        ]

        if jleague_match_id is None:
            con.execute(
                """
                UPDATE footystats_match_urls
                SET
                    link_status = 'not_found',
                    jleague_match_id = NULL,
                    last_error = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE footystats_match_url_id = ?
                """,
                (
                    "Jリーグ公式試合との"
                    "一致が見つかりません",
                    url_id,
                ),
            )

            not_found += 1
            continue

        con.execute(
            """
            UPDATE footystats_match_urls
            SET
                link_status = 'linked',
                jleague_match_id = ?,
                last_error = NULL,
                linked_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE footystats_match_url_id = ?
            """,
            (
                int(jleague_match_id),
                url_id,
            ),
        )

        linked += 1

    con.commit()

    return linked, not_found


def print_database_summary(
    con: sqlite3.Connection,
    season: int,
) -> None:
    rows = con.execute(
        """
        SELECT
            download_status,
            parse_status,
            import_status,
            link_status,
            COUNT(*) AS count
        FROM footystats_match_urls
        WHERE season = ?
        GROUP BY
            download_status,
            parse_status,
            import_status,
            link_status
        ORDER BY 1, 2, 3, 4
        """,
        (season,),
    ).fetchall()

    print()
    print("DATABASE STATUS")
    print("-" * 110)

    for row in rows:
        print(
            (
                row["download_status"],
                row["parse_status"],
                row["import_status"],
                row["link_status"],
                row["count"],
            )
        )


def main() -> None:
    args = parse_args()

    validate_scripts()

    con = connect_database()

    try:
        targets = load_targets(
            con=con,
            season=args.season,
            limit=args.limit,
            retry_errors=(
                args.retry_errors
            ),
        )

        print("=" * 110)
        print(
            "FootyStats Parsed Match Processor"
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

        imported = 0
        errors = 0

        for index, target in enumerate(
            targets,
            start=1,
        ):
            print()
            print(
                f"[{index}/{len(targets)}]"
            )

            success = process_target(
                con=con,
                target=target,
            )

            if success:
                imported += 1
            else:
                errors += 1

        linked = 0
        not_found = 0

        if imported > 0:
            print()
            print("=" * 110)
            print(
                "J.League Match Linking"
            )
            print("=" * 110)

            run_linker()

            linked, not_found = (
                refresh_link_statuses(
                    con=con,
                    season=args.season,
                )
            )

        print()
        print("RUN SUMMARY")
        print("-" * 110)
        print(
            f"imported         : {imported}"
        )
        print(
            f"import errors    : {errors}"
        )
        print(
            f"linked           : {linked}"
        )
        print(
            f"link not found   : {not_found}"
        )

        print_database_summary(
            con=con,
            season=args.season,
        )

    finally:
        con.close()


if __name__ == "__main__":
    main()