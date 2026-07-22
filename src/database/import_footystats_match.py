# -*- coding: utf-8 -*-

"""
Project AKAMURASAKI

File:
    import_footystats_match.py

Purpose:
    parse_footystats_match.pyで生成し、
    enrich_footystats_match_sides.pyでホーム・アウェイ情報を
    追加したFootyStats試合JSONをdata/toto.dbへ登録する。

Processing:
    1. JSONを検証
    2. FootyStats外部IDから内部team_idを解決
    3. team_source_mapに未登録の場合はteam_alias_v2から補完
    4. jleague_matchesと試合日・対戦チームで照合
    5. 既存の同一JSONデータを削除
    6. footystats_match_pagesへ登録
    7. 32比較テーブルを登録
    8. 204指標を登録
    9. 登録件数を検証
    10. 全処理成功時のみcommit

Target tables:
    team_master
    team_alias_v2
    team_source_map
    jleague_matches
    footystats_match_pages
    footystats_match_tables
    footystats_match_metrics

Notes:
    - 再実行可能。
    - 途中で失敗した場合は全処理をrollbackする。
    - Premiumロック値はNULLとして保存する。
    - 現在のmatch_metricsテーブルはTEXT列なので、
      JSON value辞書内のraw値を保存する。
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data/toto.db"
)

JSON_PATH = (
    PROJECT_ROOT
    / "data/parsed/footystats/matches/2026/"
    "kataller_toyama_vs_vanraure_hachinohe.json"
)

SOURCE_NAME = "footystats"


REQUIRED_TABLES = {
    "team_master",
    "team_alias_v2",
    "team_source_map",
    "jleague_matches",
    "footystats_match_pages",
    "footystats_match_tables",
    "footystats_match_metrics",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"JSONが見つかりません: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"JSONパスがファイルではありません: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "JSONのルートが辞書ではありません"
        )

    required_fields = {
        "page_title",
        "league_name",
        "season_year",
        "match_date",
        "source_file",
        "home_team_name",
        "away_team_name",
        "home_external_team_id",
        "away_external_team_id",
        "tables",
    }

    missing_fields = {
        field
        for field in required_fields
        if field not in data
    }

    if missing_fields:
        raise ValueError(
            "JSONの必須項目が不足しています: "
            + ", ".join(
                sorted(missing_fields)
            )
            + "\n"
            + "先に次を実行してください:\n"
            + "python "
            + "src/parsers/enrich_footystats_match_sides.py"
        )

    if not isinstance(
        data["tables"],
        list,
    ):
        raise ValueError(
            "JSONのtablesが配列ではありません"
        )

    if not data["match_date"]:
        raise ValueError(
            "JSONのmatch_dateが空です"
        )

    home_external_id = data[
        "home_external_team_id"
    ]

    away_external_id = data[
        "away_external_team_id"
    ]

    try:
        home_external_id = int(
            home_external_id
        )
        away_external_id = int(
            away_external_id
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "ホームまたはアウェイの外部IDが"
            "整数ではありません"
        ) from exc

    if home_external_id == away_external_id:
        raise ValueError(
            "ホームとアウェイの外部IDが同じです"
        )

    data["home_external_team_id"] = (
        home_external_id
    )

    data["away_external_team_id"] = (
        away_external_id
    )

    return data


def connect_database() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DBが見つかりません: {DB_PATH}"
        )

    con = sqlite3.connect(
        DB_PATH
    )

    con.row_factory = sqlite3.Row

    con.execute(
        "PRAGMA foreign_keys = ON"
    )

    return con


def quote_identifier(
    value: str,
) -> str:
    if not re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*",
        value,
    ):
        raise ValueError(
            f"不正なSQL識別子です: {value}"
        )

    return f'"{value}"'


def table_exists(
    con: sqlite3.Connection,
    table_name: str,
) -> bool:
    row = con.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def get_table_columns(
    con: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    safe_table = quote_identifier(
        table_name
    )

    rows = con.execute(
        f"PRAGMA table_info({safe_table})"
    ).fetchall()

    return {
        str(row["name"])
        for row in rows
    }


def validate_database_schema(
    con: sqlite3.Connection,
) -> None:
    missing_tables = {
        table_name
        for table_name in REQUIRED_TABLES
        if not table_exists(
            con,
            table_name,
        )
    }

    if missing_tables:
        raise RuntimeError(
            "必要なテーブルがありません: "
            + ", ".join(
                sorted(missing_tables)
            )
        )

    page_columns = get_table_columns(
        con,
        "footystats_match_pages",
    )

    required_page_columns = {
        "id",
        "page_title",
        "league",
        "season",
        "source_file",
        "json_file",
        "match_date",
        "home_team_name",
        "away_team_name",
        "home_external_team_id",
        "away_external_team_id",
        "home_team_id",
        "away_team_id",
        "jleague_match_id",
        "updated_at",
    }

    missing_page_columns = (
        required_page_columns
        - page_columns
    )

    if missing_page_columns:
        raise RuntimeError(
            "footystats_match_pagesの列が不足しています: "
            + ", ".join(
                sorted(
                    missing_page_columns
                )
            )
            + "\n先に次を実行してください:\n"
            + "python "
            + "src/database/"
            + "migrate_footystats_match_pages_v2.py"
        )


def normalize_team_name(
    value: str | None,
) -> str:
    if value is None:
        return ""

    normalized = value.strip()

    normalized = re.sub(
        r"\s+",
        "",
        normalized,
    )

    normalized = normalized.replace(
        "・",
        "",
    )

    normalized = normalized.replace(
        "．",
        "",
    )

    normalized = normalized.replace(
        ".",
        "",
    )

    normalized = normalized.replace(
        "－",
        "",
    )

    normalized = normalized.replace(
        "-",
        "",
    )

    normalized = normalized.casefold()

    return normalized


def get_team_by_source_map(
    con: sqlite3.Connection,
    external_team_id: int,
) -> tuple[int, str] | None:
    row = con.execute(
        """
        SELECT
            tm.team_id,
            tm.short_name
        FROM team_source_map AS tsm
        JOIN team_master AS tm
          ON tm.team_id = tsm.team_id
        WHERE tsm.source_name = ?
          AND CAST(
                tsm.external_team_id AS TEXT
              ) = ?
        LIMIT 1
        """,
        (
            SOURCE_NAME,
            str(external_team_id),
        ),
    ).fetchone()

    if row is None:
        return None

    return (
        int(row["team_id"]),
        str(row["short_name"]),
    )


def get_team_by_alias_exact(
    con: sqlite3.Connection,
    team_name: str,
) -> tuple[int, str] | None:
    row = con.execute(
        """
        SELECT
            tm.team_id,
            tm.short_name
        FROM team_alias_v2 AS tav
        JOIN team_master AS tm
          ON tm.team_id = tav.team_id
        WHERE tav.alias_name = ?
        LIMIT 1
        """,
        (team_name,),
    ).fetchone()

    if row is None:
        return None

    return (
        int(row["team_id"]),
        str(row["short_name"]),
    )


def get_team_by_master_name(
    con: sqlite3.Connection,
    team_name: str,
) -> tuple[int, str] | None:
    master_columns = get_table_columns(
        con,
        "team_master",
    )

    searchable_columns = [
        column
        for column in (
            "short_name",
            "full_name",
            "team_name",
            "official_name",
        )
        if column in master_columns
    ]

    for column in searchable_columns:
        safe_column = quote_identifier(
            column
        )

        row = con.execute(
            f"""
            SELECT
                team_id,
                short_name
            FROM team_master
            WHERE {safe_column} = ?
            LIMIT 1
            """,
            (team_name,),
        ).fetchone()

        if row is not None:
            return (
                int(row["team_id"]),
                str(row["short_name"]),
            )

    return None


def get_team_by_normalized_alias(
    con: sqlite3.Connection,
    team_name: str,
) -> tuple[int, str] | None:
    target = normalize_team_name(
        team_name
    )

    rows = con.execute(
        """
        SELECT
            tav.alias_name,
            tm.team_id,
            tm.short_name
        FROM team_alias_v2 AS tav
        JOIN team_master AS tm
          ON tm.team_id = tav.team_id
        """
    ).fetchall()

    matches: list[
        tuple[int, str]
    ] = []

    for row in rows:
        alias_name = str(
            row["alias_name"]
        )

        if (
            normalize_team_name(
                alias_name
            )
            == target
        ):
            matches.append(
                (
                    int(row["team_id"]),
                    str(row["short_name"]),
                )
            )

    unique_matches = list(
        dict.fromkeys(matches)
    )

    if len(unique_matches) == 1:
        return unique_matches[0]

    if len(unique_matches) > 1:
        raise ValueError(
            "正規化後のチーム名が複数team_idへ"
            "対応しています: "
            f"{team_name} -> {unique_matches}"
        )

    return None


def resolve_internal_team(
    con: sqlite3.Connection,
    external_team_id: int,
    external_team_name: str,
    source_url: str | None,
) -> tuple[int, str, str]:
    source_result = get_team_by_source_map(
        con,
        external_team_id,
    )

    if source_result is not None:
        team_id, short_name = (
            source_result
        )

        return (
            team_id,
            short_name,
            "team_source_map",
        )

    resolution_candidates = (
        (
            "team_alias_v2_exact",
            get_team_by_alias_exact(
                con,
                external_team_name,
            ),
        ),
        (
            "team_master_exact",
            get_team_by_master_name(
                con,
                external_team_name,
            ),
        ),
        (
            "team_alias_v2_normalized",
            get_team_by_normalized_alias(
                con,
                external_team_name,
            ),
        ),
    )

    for method, result in resolution_candidates:
        if result is None:
            continue

        team_id, short_name = result

        insert_team_source_map(
            con=con,
            team_id=team_id,
            external_team_id=external_team_id,
            external_team_name=(
                external_team_name
            ),
            source_url=source_url,
        )

        return (
            team_id,
            short_name,
            method,
        )

    raise ValueError(
        "内部team_idを解決できません: "
        f"name={external_team_name}, "
        f"external_id={external_team_id}\n"
        "team_alias_v2またはteam_masterへ"
        "チーム名を登録してください。"
    )


def insert_team_source_map(
    con: sqlite3.Connection,
    team_id: int,
    external_team_id: int,
    external_team_name: str,
    source_url: str | None,
) -> None:
    columns = get_table_columns(
        con,
        "team_source_map",
    )

    existing = con.execute(
        """
        SELECT
            team_id
        FROM team_source_map
        WHERE source_name = ?
          AND CAST(
                external_team_id AS TEXT
              ) = ?
        LIMIT 1
        """,
        (
            SOURCE_NAME,
            str(external_team_id),
        ),
    ).fetchone()

    if existing is not None:
        existing_team_id = int(
            existing["team_id"]
        )

        if existing_team_id != team_id:
            raise ValueError(
                "team_source_mapの既存対応が矛盾しています: "
                f"external_id={external_team_id}, "
                f"existing_team_id={existing_team_id}, "
                f"resolved_team_id={team_id}"
            )

        return

    insert_columns = [
        "team_id",
        "source_name",
        "external_team_id",
        "external_name",
    ]

    values: list[Any] = [
        team_id,
        SOURCE_NAME,
        str(external_team_id),
        external_team_name,
    ]

    if "source_url" in columns:
        insert_columns.append(
            "source_url"
        )
        values.append(
            source_url
        )

    if "is_primary" in columns:
        insert_columns.append(
            "is_primary"
        )
        values.append(1)

    column_sql = ", ".join(
        quote_identifier(column)
        for column in insert_columns
    )

    placeholders = ", ".join(
        "?"
        for _ in insert_columns
    )

    con.execute(
        f"""
        INSERT INTO team_source_map (
            {column_sql}
        )
        VALUES (
            {placeholders}
        )
        """,
        tuple(values),
    )


def detect_first_column(
    columns: set[str],
    candidates: tuple[str, ...],
) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate

    return None


def find_jleague_match(
    con: sqlite3.Connection,
    match_date: str,
    home_team_id: int,
    away_team_id: int,
    home_short_name: str,
    away_short_name: str,
) -> tuple[int | None, str]:
    columns = get_table_columns(
        con,
        "jleague_matches",
    )

    id_column = detect_first_column(
        columns,
        (
            "jleague_match_id",
            "match_id",
            "id",
        ),
    )

    date_column = detect_first_column(
        columns,
        (
            "match_date",
            "date",
            "match_day",
            "scheduled_date",
            "scheduled_at",
            "kickoff_at",
            "kickoff_datetime",
        ),
    )

    home_id_column = detect_first_column(
        columns,
        (
            "home_team_id",
            "home_id",
        ),
    )

    away_id_column = detect_first_column(
        columns,
        (
            "away_team_id",
            "away_id",
        ),
    )

    home_name_column = detect_first_column(
        columns,
        (
            "home_team",
            "home_team_name",
            "home",
        ),
    )

    away_name_column = detect_first_column(
        columns,
        (
            "away_team",
            "away_team_name",
            "away",
        ),
    )

    if id_column is None:
        return (
            None,
            "jleague_matchesにID列がありません",
        )

    if date_column is None:
        return (
            None,
            "jleague_matchesに日付列がありません",
        )

    safe_id = quote_identifier(
        id_column
    )

    safe_date = quote_identifier(
        date_column
    )

    rows: list[sqlite3.Row]

    if (
        home_id_column is not None
        and away_id_column is not None
    ):
        safe_home = quote_identifier(
            home_id_column
        )
        safe_away = quote_identifier(
            away_id_column
        )

        rows = con.execute(
            f"""
            SELECT
                {safe_id} AS official_match_id
            FROM jleague_matches
            WHERE substr(
                CAST({safe_date} AS TEXT),
                1,
                10
            ) = ?
              AND {safe_home} = ?
              AND {safe_away} = ?
            """,
            (
                match_date,
                home_team_id,
                away_team_id,
            ),
        ).fetchall()

        method = (
            f"{date_column}"
            f"+{home_id_column}"
            f"+{away_id_column}"
        )

    elif (
        home_name_column is not None
        and away_name_column is not None
    ):
        safe_home = quote_identifier(
            home_name_column
        )
        safe_away = quote_identifier(
            away_name_column
        )

        rows = con.execute(
            f"""
            SELECT
                {safe_id} AS official_match_id
            FROM jleague_matches
            WHERE substr(
                CAST({safe_date} AS TEXT),
                1,
                10
            ) = ?
              AND {safe_home} = ?
              AND {safe_away} = ?
            """,
            (
                match_date,
                home_short_name,
                away_short_name,
            ),
        ).fetchall()

        method = (
            f"{date_column}"
            f"+{home_name_column}"
            f"+{away_name_column}"
        )

    else:
        return (
            None,
            "jleague_matchesに対戦チーム列がありません",
        )

    if len(rows) == 1:
        value = rows[0][
            "official_match_id"
        ]

        if value is None:
            return (
                None,
                "公式試合IDがNULLです",
            )

        return (
            int(value),
            method,
        )

    if len(rows) == 0:
        return (
            None,
            "一致する公式試合なし"
            f" ({method})",
        )

    raise ValueError(
        "jleague_matchesに同一日・同一対戦の"
        "候補が複数あります: "
        f"date={match_date}, "
        f"home={home_short_name}, "
        f"away={away_short_name}, "
        f"count={len(rows)}"
    )


def relative_path(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
    except ValueError:
        return str(path)


def delete_existing_page(
    con: sqlite3.Connection,
    json_file: str,
) -> int:
    rows = con.execute(
        """
        SELECT id
        FROM footystats_match_pages
        WHERE json_file = ?
        """,
        (json_file,),
    ).fetchall()

    page_ids = [
        int(row["id"])
        for row in rows
    ]

    for page_id in page_ids:
        table_rows = con.execute(
            """
            SELECT id
            FROM footystats_match_tables
            WHERE page_id = ?
            """,
            (page_id,),
        ).fetchall()

        table_ids = [
            int(row["id"])
            for row in table_rows
        ]

        for table_id in table_ids:
            con.execute(
                """
                DELETE FROM footystats_match_metrics
                WHERE table_id = ?
                """,
                (table_id,),
            )

        con.execute(
            """
            DELETE FROM footystats_match_tables
            WHERE page_id = ?
            """,
            (page_id,),
        )

        con.execute(
            """
            DELETE FROM footystats_match_pages
            WHERE id = ?
            """,
            (page_id,),
        )

    return len(page_ids)


def insert_page(
    con: sqlite3.Connection,
    data: dict[str, Any],
    json_file: str,
    home_team_id: int,
    away_team_id: int,
    jleague_match_id: int | None,
) -> int:
    cursor = con.execute(
        """
        INSERT INTO footystats_match_pages (
            page_title,
            league,
            season,
            source_file,
            json_file,
            match_date,
            home_team_name,
            away_team_name,
            home_external_team_id,
            away_external_team_id,
            home_team_id,
            away_team_id,
            jleague_match_id,
            updated_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP
        )
        """,
        (
            data.get("page_title"),
            data.get("league_name"),
            data.get("season_year"),
            data.get("source_file"),
            json_file,
            data.get("match_date"),
            data.get("home_team_name"),
            data.get("away_team_name"),
            data.get(
                "home_external_team_id"
            ),
            data.get(
                "away_external_team_id"
            ),
            home_team_id,
            away_team_id,
            jleague_match_id,
        ),
    )

    if cursor.lastrowid is None:
        raise RuntimeError(
            "page_idを取得できませんでした"
        )

    return int(
        cursor.lastrowid
    )


def insert_table(
    con: sqlite3.Connection,
    page_id: int,
    table: dict[str, Any],
    fallback_index: int,
) -> int:
    table_index = table.get(
        "table_index",
        fallback_index,
    )

    cursor = con.execute(
        """
        INSERT INTO footystats_match_tables (
            page_id,
            table_index,
            section_title,
            table_title
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            page_id,
            table_index,
            table.get("section_title"),
            table.get("table_title"),
        ),
    )

    if cursor.lastrowid is None:
        raise RuntimeError(
            "table_idを取得できませんでした"
        )

    return int(
        cursor.lastrowid
    )


def extract_raw_value(
    value: Any,
) -> str | None:
    if value is None:
        return None

    if isinstance(value, dict):
        if bool(
            value.get("locked")
        ):
            return None

        raw = value.get("raw")

        if raw is None:
            return None

        return str(raw)

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return str(value)

    return json.dumps(
        value,
        ensure_ascii=False,
    )


def insert_metric(
    con: sqlite3.Connection,
    table_id: int,
    row: dict[str, Any],
) -> None:
    source_values = row.get(
        "values",
        [],
    )

    if not isinstance(
        source_values,
        list,
    ):
        raise ValueError(
            "row.valuesが配列ではありません: "
            f"{row.get('metric')}"
        )

    values = [
        extract_raw_value(value)
        for value in source_values
    ]

    while len(values) < 3:
        values.append(None)

    con.execute(
        """
        INSERT INTO footystats_match_metrics (
            table_id,
            metric_name,
            value1,
            value2,
            value3
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            table_id,
            row.get("metric"),
            values[0],
            values[1],
            values[2],
        ),
    )


def import_tables_and_metrics(
    con: sqlite3.Connection,
    page_id: int,
    tables: list[Any],
) -> tuple[int, int]:
    table_count = 0
    metric_count = 0

    for fallback_index, table in enumerate(
        tables,
        start=1,
    ):
        if not isinstance(
            table,
            dict,
        ):
            raise ValueError(
                "tables内に辞書でない要素があります"
            )

        table_id = insert_table(
            con=con,
            page_id=page_id,
            table=table,
            fallback_index=fallback_index,
        )

        table_count += 1

        rows = table.get(
            "rows",
            [],
        )

        if not isinstance(rows, list):
            raise ValueError(
                "table.rowsが配列ではありません: "
                f"table_index={fallback_index}"
            )

        for row in rows:
            if not isinstance(
                row,
                dict,
            ):
                raise ValueError(
                    "rows内に辞書でない要素があります"
                )

            insert_metric(
                con=con,
                table_id=table_id,
                row=row,
            )

            metric_count += 1

    return (
        table_count,
        metric_count,
    )


def verify_import(
    con: sqlite3.Connection,
    page_id: int,
    expected_tables: int,
    expected_metrics: int,
    expected_home_team_id: int,
    expected_away_team_id: int,
) -> None:
    page = con.execute(
        """
        SELECT
            home_team_id,
            away_team_id,
            match_date
        FROM footystats_match_pages
        WHERE id = ?
        """,
        (page_id,),
    ).fetchone()

    if page is None:
        raise RuntimeError(
            "登録したページを取得できません"
        )

    if (
        int(page["home_team_id"])
        != expected_home_team_id
    ):
        raise RuntimeError(
            "home_team_idが一致しません"
        )

    if (
        int(page["away_team_id"])
        != expected_away_team_id
    ):
        raise RuntimeError(
            "away_team_idが一致しません"
        )

    actual_tables = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_tables
            WHERE page_id = ?
            """,
            (page_id,),
        ).fetchone()[0]
    )

    actual_metrics = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM footystats_match_metrics AS m
            JOIN footystats_match_tables AS t
              ON t.id = m.table_id
            WHERE t.page_id = ?
            """,
            (page_id,),
        ).fetchone()[0]
    )

    if actual_tables != expected_tables:
        raise RuntimeError(
            "登録テーブル件数が一致しません: "
            f"expected={expected_tables}, "
            f"actual={actual_tables}"
        )

    if actual_metrics != expected_metrics:
        raise RuntimeError(
            "登録指標件数が一致しません: "
            f"expected={expected_metrics}, "
            f"actual={actual_metrics}"
        )


def print_summary(
    *,
    page_id: int,
    deleted_pages: int,
    table_count: int,
    metric_count: int,
    data: dict[str, Any],
    home_team_id: int,
    home_short_name: str,
    home_resolution: str,
    away_team_id: int,
    away_short_name: str,
    away_resolution: str,
    jleague_match_id: int | None,
    jleague_resolution: str,
) -> None:
    print("=" * 110)
    print(
        "FootyStats Match Import V2"
    )
    print("=" * 110)

    print(
        f"page_id                 : "
        f"{page_id}"
    )
    print(
        f"existing pages deleted  : "
        f"{deleted_pages}"
    )
    print(
        f"match_date              : "
        f"{data.get('match_date')}"
    )
    print(
        f"league                  : "
        f"{data.get('league_name')}"
    )
    print()

    print(
        f"home external           : "
        f"{data.get('home_team_name')} "
        f"(ID={data.get('home_external_team_id')})"
    )
    print(
        f"home internal           : "
        f"team_id={home_team_id} "
        f"{home_short_name}"
    )
    print(
        f"home resolution         : "
        f"{home_resolution}"
    )
    print()

    print(
        f"away external           : "
        f"{data.get('away_team_name')} "
        f"(ID={data.get('away_external_team_id')})"
    )
    print(
        f"away internal           : "
        f"team_id={away_team_id} "
        f"{away_short_name}"
    )
    print(
        f"away resolution         : "
        f"{away_resolution}"
    )
    print()

    print(
        f"jleague_match_id        : "
        f"{jleague_match_id}"
    )
    print(
        f"jleague resolution      : "
        f"{jleague_resolution}"
    )
    print(
        f"tables imported         : "
        f"{table_count}"
    )
    print(
        f"metrics imported        : "
        f"{metric_count}"
    )
    print(
        f"database                : "
        f"{relative_path(DB_PATH)}"
    )
    print(
        f"json source             : "
        f"{relative_path(JSON_PATH)}"
    )

    if jleague_match_id is None:
        print()
        print(
            "Note: Jリーグ公式試合との照合は"
            "まだ成立していません。"
        )
        print(
            "FootyStatsページ・内部team_id・"
            "32テーブル・204指標は保存済みです。"
        )


def main() -> None:
    data = load_json(
        JSON_PATH
    )

    expected_tables = len(
        data["tables"]
    )

    expected_metrics = sum(
        len(table.get("rows", []))
        for table in data["tables"]
        if isinstance(table, dict)
    )

    con = connect_database()

    try:
        validate_database_schema(
            con
        )

        home_team_id, home_short_name, (
            home_resolution
        ) = resolve_internal_team(
            con=con,
            external_team_id=int(
                data[
                    "home_external_team_id"
                ]
            ),
            external_team_name=str(
                data["home_team_name"]
            ),
            source_url=data.get(
                "home_source_url"
            ),
        )

        away_team_id, away_short_name, (
            away_resolution
        ) = resolve_internal_team(
            con=con,
            external_team_id=int(
                data[
                    "away_external_team_id"
                ]
            ),
            external_team_name=str(
                data["away_team_name"]
            ),
            source_url=data.get(
                "away_source_url"
            ),
        )

        if home_team_id == away_team_id:
            raise ValueError(
                "ホームとアウェイが同一の"
                "内部team_idです"
            )

        (
            jleague_match_id,
            jleague_resolution,
        ) = find_jleague_match(
            con=con,
            match_date=str(
                data["match_date"]
            ),
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_short_name=home_short_name,
            away_short_name=away_short_name,
        )

        json_file = relative_path(
            JSON_PATH
        )

        deleted_pages = delete_existing_page(
            con=con,
            json_file=json_file,
        )

        page_id = insert_page(
            con=con,
            data=data,
            json_file=json_file,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            jleague_match_id=(
                jleague_match_id
            ),
        )

        (
            table_count,
            metric_count,
        ) = import_tables_and_metrics(
            con=con,
            page_id=page_id,
            tables=data["tables"],
        )

        verify_import(
            con=con,
            page_id=page_id,
            expected_tables=expected_tables,
            expected_metrics=expected_metrics,
            expected_home_team_id=(
                home_team_id
            ),
            expected_away_team_id=(
                away_team_id
            ),
        )

        con.commit()

        print_summary(
            page_id=page_id,
            deleted_pages=deleted_pages,
            table_count=table_count,
            metric_count=metric_count,
            data=data,
            home_team_id=home_team_id,
            home_short_name=home_short_name,
            home_resolution=(
                home_resolution
            ),
            away_team_id=away_team_id,
            away_short_name=away_short_name,
            away_resolution=(
                away_resolution
            ),
            jleague_match_id=(
                jleague_match_id
            ),
            jleague_resolution=(
                jleague_resolution
            ),
        )

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()