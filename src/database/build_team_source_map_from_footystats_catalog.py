#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

LOGGER = logging.getLogger("build_team_source_map_2025")
SOURCE_NAME = "footystats"

# team_master.short_name -> footystats_team_catalog.team_slug
SLUGS = {
    "FC東京": ("fc-tokyo",),
    "いわき": ("iwaki-sc", "iwaki", "iwaki-fc"),
    "京都": ("kyoto-sanga-fc",),
    "今治": ("fc-imabari", "imabari"),
    "仙台": ("vegalta-sendai",),
    "八戸": ("vanraure-hachinohe",),
    "北九州": ("giravanz-kitakyushu",),
    "千葉": ("jef-united-ichihara-chiba",),
    "名古屋": ("nagoya-grampus",),
    "大分": ("oita-trinita",),
    "大宮": ("omiya-ardija", "rb-omiya-ardija"),
    "宮崎": ("tegevajaro-miyazaki",),
    "富山": ("kataller-toyama",),
    "山口": ("renofa-yamaguchi",),
    "山形": ("montedio-yamagata",),
    "岐阜": ("fc-gifu",),
    "岡山": ("fagiano-okayama",),
    "岩手": ("grulla-morioka", "iwate-grulla-morioka"),
    "川崎Ｆ": ("kawasaki-frontale",),
    "広島": ("sanfrecce-hiroshima",),
    "徳島": ("tokushima-vortis",),
    "愛媛": ("ehime-fc",),
    "新潟": ("albirex-niigata",),
    "札幌": ("consadole-sapporo", "hokkaido-consadole-sapporo"),
    "東京Ｖ": ("tokyo-verdy",),
    "松本": ("matsumoto-yamaga",),
    "柏": ("kashiwa-reysol",),
    "栃木": ("tochigi-sc", "tochigi"),
    "横浜FC": ("yokohama-fc",),
    "横浜FM": ("yokohama-f-marinos",),
    "水戸": ("mito-hollyhock",),
    "浦和": ("urawa-red-diamonds",),
    "清水": ("shimizu-s-pulse",),
    "湘南": ("shonan-bellmare",),
    "熊本": ("roasso-kumamoto",),
    "琉球": ("fc-ryukyu", "ryukyu"),
    "甲府": ("ventforet-kofu",),
    "町田": ("fc-machida-zelvia",),
    "相模原": ("sc-sagamihara",),
    "磐田": ("jubilo-iwata",),
    "神戸": ("vissel-kobe",),
    "福岡": ("avispa-fukuoka",),
    "秋田": ("afc-blaublitz-akita", "blaublitz-akita"),
    "群馬": ("thespa-kusatsu-gunma", "thespakusatsu-gunma", "thespa-gunma"),
    "藤枝": ("fujieda-myfc", "fujieda-my-fc"),
    "讃岐": ("kamatamare-sanuki",),
    "金沢": ("zweigen-kanazawa",),
    "長崎": ("v-varen-nagasaki",),
    "鳥取": ("gainare-tottori",),
    "鳥栖": ("sagan-tosu",),
    "鹿児島": ("kagoshima-united", "kagoshima-united-fc"),
    "鹿島": ("kashima-antlers",),
    "Ｃ大阪": ("cerezo-osaka",),
    "Ｇ大阪": ("gamba-osaka",),
    "長野": ("ac-nagano-parceiro", "nagano-parceiro"),
    "奈良": ("nara-club",),
    "沼津": ("azul-claro-numazu", "azul-claro"),
    "福島": ("fukushima-united", "fukushima-united-fc"),
    "高知": ("kochi-united", "kochi-united-sc"),
}


@dataclass(frozen=True)
class CatalogTeam:
    team_name: str
    team_slug: str
    external_team_id: str
    team_url: str


@dataclass(frozen=True)
class Decision:
    team_id: int
    short_name: str
    status: str
    method: str
    catalog: CatalogTeam | None
    note: str | None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_season_teams(con: sqlite3.Connection, season: int) -> list[sqlite3.Row]:
    return con.execute(
        """
        WITH season_teams AS (
            SELECT ta.team_id
            FROM jleague_matches jm
            JOIN team_alias_v2 ta ON ta.alias_name = jm.home_team
            WHERE jm.season = ?
            UNION
            SELECT ta.team_id
            FROM jleague_matches jm
            JOIN team_alias_v2 ta ON ta.alias_name = jm.away_team
            WHERE jm.season = ?
        )
        SELECT tm.team_id, tm.short_name, tm.full_name
        FROM season_teams st
        JOIN team_master tm ON tm.team_id = st.team_id
        ORDER BY tm.team_id
        """,
        (season, season),
    ).fetchall()


def load_catalog(con: sqlite3.Connection, season: int) -> dict[str, CatalogTeam]:
    result: dict[str, CatalogTeam] = {}
    for row in con.execute(
        """
        SELECT team_name, team_slug, footystats_team_id, team_url
        FROM footystats_team_catalog
        WHERE season = ? AND is_excluded = 0
        """,
        (season,),
    ):
        result[str(row["team_slug"]).lower()] = CatalogTeam(
            team_name=str(row["team_name"]),
            team_slug=str(row["team_slug"]).lower(),
            external_team_id=str(row["footystats_team_id"]),
            team_url=str(row["team_url"]),
        )
    return result


def existing_team_ids(con: sqlite3.Connection) -> set[int]:
    return {
        int(row[0])
        for row in con.execute(
            """
            SELECT team_id
            FROM team_source_map
            WHERE lower(source_name) = lower(?)
            """,
            (SOURCE_NAME,),
        )
    }


def build_decisions(
    teams: Sequence[sqlite3.Row],
    catalog: dict[str, CatalogTeam],
    existing: set[int],
) -> list[Decision]:
    decisions: list[Decision] = []
    for team in teams:
        team_id = int(team["team_id"])
        short_name = str(team["short_name"])

        if team_id in existing:
            decisions.append(
                Decision(team_id, short_name, "CONFIRMED",
                         "existing_mapping", None, None)
            )
            continue

        candidate_slugs = SLUGS.get(short_name, ())
        matches = {
            catalog[slug].external_team_id: catalog[slug]
            for slug in candidate_slugs
            if slug in catalog
        }

        if len(matches) == 1:
            decisions.append(
                Decision(
                    team_id, short_name, "CONFIRMED",
                    "slug_exact", next(iter(matches.values())), None
                )
            )
        elif not candidate_slugs:
            decisions.append(
                Decision(
                    team_id, short_name, "UNRESOLVED",
                    "missing_dictionary", None, "slug辞書なし"
                )
            )
        elif not matches:
            decisions.append(
                Decision(
                    team_id, short_name, "UNRESOLVED",
                    "slug_not_found", None,
                    " / ".join(candidate_slugs)
                )
            )
        else:
            decisions.append(
                Decision(
                    team_id, short_name, "UNRESOLVED",
                    "multiple_matches", None,
                    ", ".join(sorted(matches))
                )
            )
    return decisions


def validate_conflicts(
    con: sqlite3.Connection,
    decisions: Sequence[Decision],
) -> None:
    for d in decisions:
        if d.catalog is None:
            continue
        conflict = con.execute(
            """
            SELECT team_id
            FROM team_source_map
            WHERE lower(source_name) = lower(?)
              AND external_team_id = ?
              AND team_id <> ?
            """,
            (SOURCE_NAME, d.catalog.external_team_id, d.team_id),
        ).fetchone()
        if conflict:
            raise RuntimeError(
                f"external_team_id={d.catalog.external_team_id} は "
                f"team_id={conflict['team_id']} に登録済み"
            )


def insert_new(con: sqlite3.Connection, decisions: Sequence[Decision]) -> int:
    timestamp = now_iso()
    count = 0
    for d in decisions:
        if d.status != "CONFIRMED" or d.catalog is None:
            continue
        con.execute(
            """
            INSERT INTO team_source_map (
                team_id, source_name, external_team_id, external_name,
                source_url, is_primary, created_at, updated_at
            )
            SELECT ?, ?, ?, ?, ?, 1, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM team_source_map
                WHERE team_id = ?
                  AND lower(source_name) = lower(?)
            )
            """,
            (
                d.team_id, SOURCE_NAME, d.catalog.external_team_id,
                d.catalog.team_name, d.catalog.team_url,
                timestamp, timestamp, d.team_id, SOURCE_NAME,
            ),
        )
        count += con.execute("SELECT changes()").fetchone()[0]
    return count


def write_report(path: Path, season: int, decisions: Sequence[Decision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "season": season,
        "confirmed": sum(d.status == "CONFIRMED" for d in decisions),
        "unresolved": sum(d.status == "UNRESOLVED" for d in decisions),
        "decisions": [asdict(d) for d in decisions],
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/toto.db"))
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/interim/team_source_map_2025.json"),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        con = sqlite3.connect(args.db)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA busy_timeout = 30000")

        teams = load_season_teams(con, args.season)
        catalog = load_catalog(con, args.season)
        existing = existing_team_ids(con)
        LOGGER.info(
            "Loaded season_teams=%d catalog=%d existing=%d",
            len(teams), len(catalog), len(existing),
        )

        decisions = build_decisions(teams, catalog, existing)
        validate_conflicts(con, decisions)
        write_report(args.report, args.season, decisions)

        print(f"CONFIRMED : {sum(d.status == 'CONFIRMED' for d in decisions)}")
        print(f"UNRESOLVED: {sum(d.status == 'UNRESOLVED' for d in decisions)}")

        for d in decisions:
            if d.catalog:
                print(
                    f"{d.team_id:>4} {d.short_name:<10} -> "
                    f"{d.catalog.team_name} id={d.catalog.external_team_id}"
                )
            elif d.status == "UNRESOLVED":
                print(
                    f"{d.team_id:>4} {d.short_name:<10} "
                    f"{d.method}: {d.note}"
                )

        changed = 0
        if not args.dry_run:
            with con:
                changed = insert_new(con, decisions)
            LOGGER.info("Inserted mappings=%d", changed)

        print(json.dumps({
            "season": args.season,
            "season_team_count": len(teams),
            "catalog_count": len(catalog),
            "confirmed": sum(d.status == "CONFIRMED" for d in decisions),
            "unresolved": sum(d.status == "UNRESOLVED" for d in decisions),
            "inserted": changed,
            "dry_run": args.dry_run,
        }, ensure_ascii=False, indent=2))

        return 0
    except Exception:
        LOGGER.exception("Fatal error")
        return 2
    finally:
        if "con" in locals():
            con.close()


if __name__ == "__main__":
    sys.exit(main())
