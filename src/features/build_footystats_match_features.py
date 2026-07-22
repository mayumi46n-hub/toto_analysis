# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import math
import re
import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data/toto.db"
FEATURE_TABLE = "footystats_match_features"

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {FEATURE_TABLE} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jleague_match_id INTEGER NOT NULL,
    footystats_page_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    table_index INTEGER NOT NULL,
    row_index INTEGER,
    value_position INTEGER NOT NULL,
    feature_key TEXT NOT NULL,
    feature_value REAL,
    raw_value TEXT,
    unit TEXT,
    section_title TEXT,
    table_title TEXT,
    metric_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (footystats_page_id, metric_id, value_position)
)
"""

INDEX_SQLS = (
    f"CREATE INDEX IF NOT EXISTS idx_{FEATURE_TABLE}_match ON {FEATURE_TABLE}(jleague_match_id)",
    f"CREATE INDEX IF NOT EXISTS idx_{FEATURE_TABLE}_page ON {FEATURE_TABLE}(footystats_page_id)",
    f"CREATE INDEX IF NOT EXISTS idx_{FEATURE_TABLE}_key ON {FEATURE_TABLE}(feature_key)",
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FootyStats試合指標をAI向け数値特徴量へ変換します。"
    )
    parser.add_argument("--season", type=int)
    parser.add_argument("--page-id", type=int)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--include-null", action="store_true")
    return parser.parse_args()

def connect_database() -> sqlite3.Connection:
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"DBが見つかりません: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def table_columns(con: sqlite3.Connection, name: str) -> set[str]:
    return {str(row["name"]) for row in con.execute(f"PRAGMA table_info({name})")}

def validate_source_tables(con: sqlite3.Connection) -> None:
    required = {
        "footystats_match_pages",
        "footystats_match_tables",
        "footystats_match_metrics",
    }
    existing = {
        str(row["name"])
        for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    missing = sorted(required - existing)
    if missing:
        raise RuntimeError("必要なテーブルがありません: " + ", ".join(missing))

def create_or_migrate_feature_store(con: sqlite3.Connection) -> None:
    con.execute(CREATE_TABLE_SQL)
    columns = table_columns(con, FEATURE_TABLE)
    if "row_index" not in columns:
        con.execute(f"ALTER TABLE {FEATURE_TABLE} ADD COLUMN row_index INTEGER")
    for sql in INDEX_SQLS:
        con.execute(sql)

def normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())

def slugify(value: str | None) -> str:
    text = normalize_text(value).lower()
    text = re.sub(r"[／/]+", "_", text)
    text = re.sub(r"[^\wぁ-んァ-ヶ一-龠ー]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"

def build_feature_key(
    table_index: int,
    row_index: int,
    section_title: str | None,
    table_title: str | None,
    metric_name: str,
    value_position: int,
) -> str:
    return "__".join(
        (
            f"t{table_index:02d}",
            f"r{row_index:03d}",
            slugify(section_title),
            slugify(table_title),
            slugify(metric_name),
            f"v{value_position}",
        )
    )

def parse_numeric_value(raw_value: Any) -> tuple[float | None, str | None]:
    if raw_value is None:
        return None, None
    text = normalize_text(str(raw_value))
    if not text:
        return None, None
    lowered = text.lower()
    if lowered in {"locked", "premium", "ロック", "非公開", "n/a", "na", "-", "—"}:
        return None, "locked"
    if text.endswith("%"):
        try:
            value = float(text[:-1].strip().replace(",", "")) / 100.0
        except ValueError:
            return None, "percent"
        return (value, "ratio") if math.isfinite(value) else (None, "percent")
    cleaned = text.replace(",", "")
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", cleaned):
        value = float(cleaned)
        return (value, "number") if math.isfinite(value) else (None, "number")
    match = re.search(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", cleaned)
    if match is None:
        return None, "text"
    value = float(match.group(0))
    return (value, "number") if math.isfinite(value) else (None, "number")

def load_pages(
    con: sqlite3.Connection,
    season: int | None,
    page_id: int | None,
) -> list[sqlite3.Row]:
    clauses = ["p.jleague_match_id IS NOT NULL"]
    params: list[Any] = []
    if season is not None:
        clauses.append("p.season = ?")
        params.append(season)
    if page_id is not None:
        clauses.append("p.id = ?")
        params.append(page_id)
    return con.execute(
        f"""
        SELECT
            p.id AS page_id,
            p.jleague_match_id,
            p.season,
            p.match_date,
            p.home_team_name,
            p.away_team_name
        FROM footystats_match_pages AS p
        WHERE {' AND '.join(clauses)}
        ORDER BY p.id
        """,
        tuple(params),
    ).fetchall()

def load_metrics_for_page(con: sqlite3.Connection, page_id: int) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT
            m.id AS metric_id,
            m.table_id,
            m.metric_name,
            m.value1,
            m.value2,
            m.value3,
            t.table_index,
            t.section_title,
            t.table_title
        FROM footystats_match_metrics AS m
        JOIN footystats_match_tables AS t
          ON t.id = m.table_id
        WHERE t.page_id = ?
        ORDER BY t.table_index, m.id
        """,
        (page_id,),
    ).fetchall()

def delete_existing_features(
    con: sqlite3.Connection,
    page_ids: list[int],
) -> int:
    if not page_ids:
        return 0
    placeholders = ", ".join("?" for _ in page_ids)
    cursor = con.execute(
        f"DELETE FROM {FEATURE_TABLE} WHERE footystats_page_id IN ({placeholders})",
        tuple(page_ids),
    )
    return int(cursor.rowcount)

def build_feature_rows(
    page: sqlite3.Row,
    metrics: list[sqlite3.Row],
    include_null: bool,
) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    table_row_counts: dict[int, int] = {}

    for metric in metrics:
        table_id = int(metric["table_id"])
        row_index = table_row_counts.get(table_id, 0) + 1
        table_row_counts[table_id] = row_index

        metric_name = normalize_text(metric["metric_name"])
        if not metric_name:
            continue

        for value_position in (1, 2, 3):
            raw_value = metric[f"value{value_position}"]
            numeric_value, unit = parse_numeric_value(raw_value)
            if numeric_value is None and not include_null:
                continue

            feature_key = build_feature_key(
                table_index=int(metric["table_index"]),
                row_index=row_index,
                section_title=metric["section_title"],
                table_title=metric["table_title"],
                metric_name=metric_name,
                value_position=value_position,
            )

            rows.append(
                (
                    int(page["jleague_match_id"]),
                    int(page["page_id"]),
                    table_id,
                    int(metric["metric_id"]),
                    int(metric["table_index"]),
                    row_index,
                    value_position,
                    feature_key,
                    numeric_value,
                    None if raw_value is None else str(raw_value),
                    unit,
                    normalize_text(metric["section_title"]),
                    normalize_text(metric["table_title"]),
                    metric_name,
                )
            )
    return rows

def save_feature_rows(con: sqlite3.Connection, rows: list[tuple[Any, ...]]) -> int:
    if not rows:
        return 0
    con.executemany(
        f"""
        INSERT INTO {FEATURE_TABLE} (
            jleague_match_id,
            footystats_page_id,
            table_id,
            metric_id,
            table_index,
            row_index,
            value_position,
            feature_key,
            feature_value,
            raw_value,
            unit,
            section_title,
            table_title,
            metric_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (footystats_page_id, metric_id, value_position)
        DO UPDATE SET
            jleague_match_id = excluded.jleague_match_id,
            table_id = excluded.table_id,
            table_index = excluded.table_index,
            row_index = excluded.row_index,
            feature_key = excluded.feature_key,
            feature_value = excluded.feature_value,
            raw_value = excluded.raw_value,
            unit = excluded.unit,
            section_title = excluded.section_title,
            table_title = excluded.table_title,
            metric_name = excluded.metric_name,
            updated_at = CURRENT_TIMESTAMP
        """,
        rows,
    )
    return len(rows)

def print_summary(
    con: sqlite3.Connection,
    page_count: int,
    source_metric_count: int,
    saved_count: int,
    deleted_count: int,
) -> None:
    total_count = int(con.execute(f"SELECT COUNT(*) FROM {FEATURE_TABLE}").fetchone()[0])
    distinct_matches = int(
        con.execute(
            f"SELECT COUNT(DISTINCT jleague_match_id) FROM {FEATURE_TABLE}"
        ).fetchone()[0]
    )
    distinct_keys = int(
        con.execute(
            f"SELECT COUNT(DISTINCT feature_key) FROM {FEATURE_TABLE}"
        ).fetchone()[0]
    )

    print("=" * 110)
    print("FootyStats Match Feature Store")
    print("=" * 110)
    print(f"pages processed      : {page_count}")
    print(f"source metrics       : {source_metric_count}")
    print(f"features saved       : {saved_count}")
    print(f"existing deleted     : {deleted_count}")
    print(f"total feature rows   : {total_count}")
    print(f"distinct matches     : {distinct_matches}")
    print(f"distinct feature keys: {distinct_keys}")
    print()
    print("SAMPLE")
    print("-" * 110)

    for row in con.execute(
        f"""
        SELECT jleague_match_id, feature_key, feature_value, raw_value, unit
        FROM {FEATURE_TABLE}
        ORDER BY id
        LIMIT 15
        """
    ):
        print(
            (
                row["jleague_match_id"],
                row["feature_key"],
                row["feature_value"],
                row["raw_value"],
                row["unit"],
            )
        )

def main() -> None:
    args = parse_args()
    con = connect_database()

    try:
        validate_source_tables(con)
        create_or_migrate_feature_store(con)

        pages = load_pages(
            con=con,
            season=args.season,
            page_id=args.page_id,
        )

        page_ids = [int(page["page_id"]) for page in pages]
        deleted_count = (
            delete_existing_features(con, page_ids)
            if args.rebuild
            else 0
        )

        total_source_metrics = 0
        total_saved = 0

        for index, page in enumerate(pages, start=1):
            metrics = load_metrics_for_page(
                con,
                int(page["page_id"]),
            )
            total_source_metrics += len(metrics)

            feature_rows = build_feature_rows(
                page=page,
                metrics=metrics,
                include_null=args.include_null,
            )

            saved_count = save_feature_rows(
                con,
                feature_rows,
            )
            total_saved += saved_count

            print(
                f"[{index}/{len(pages)}] "
                f"page_id={page['page_id']} "
                f"jleague_match_id={page['jleague_match_id']} "
                f"metrics={len(metrics)} "
                f"features={saved_count}"
            )

        con.commit()
        print()
        print_summary(
            con=con,
            page_count=len(pages),
            source_metric_count=total_source_metrics,
            saved_count=total_saved,
            deleted_count=deleted_count,
        )

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

if __name__ == "__main__":
    main()
