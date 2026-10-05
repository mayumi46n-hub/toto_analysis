#!/usr/bin/env python3

from pathlib import Path
import argparse
import glob
import re
import unicodedata
from collections import defaultdict
import pandas as pd
import numpy as np


def resolve_one(pattern: str) -> Path:
    hits = sorted(Path(x) for x in glob.glob(pattern))
    if len(hits) != 1:
        raise RuntimeError(
            f"expected exactly 1 file for {pattern!r}, got {len(hits)}: "
            f"{[str(x) for x in hits]}"
        )
    return hits[0]


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Round-generic frozen FootyStats predicted-XI transport. "
            "Research-only; never modifies P_base."
        )
    )
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rnd = args.round

    xi = resolve_one(
        f"data/players/totoone_toto{rnd}_predicted_lineups_*_v1.csv"
    )

    old_master = Path(
        "data/players/toto1656_player_strength_master_v04.csv"
    )
    fs_master = Path(
        "data/players/footystats_2026_player_master_v01.csv"
    )
    fs_strength = Path(
        "data/players/footystats_2026_player_strength_full_v02.csv"
    )

    fixed = {
        "OLD_MASTER": old_master,
        "FS_MASTER": fs_master,
        "FS_STRENGTH": fs_strength,
    }

    for label, path in fixed.items():
        if not path.exists():
            raise FileNotFoundError(f"{label}: {path}")

    print("=== TOTO XI FS FROZEN TRANSPORT V01 ===")
    print("ROUND =", rnd)
    print("XI =", xi)
    for label, path in fixed.items():
        print(f"{label} =", path)

    print()
    print("=== GOVERNANCE CONTRACT ===")
    print("RESULT_INPUT = NONE")
    print("P_BASE_INPUT = NONE")
    print("P_BASE_MUTATION = NO")
    print("SECOND_RELIABILITY_WEIGHT = NO")
    print("PRODUCTION_PLAYER_COEFFICIENT = 0.0")
    print("TRANSPORT_STATUS = RESEARCH_ONLY_UNCALIBRATED")

    if args.dry_run:
        print()
        print("DRY_RUN = PASS")
        return

    # ------------------------------------------------------------
    # Identity helpers
    # ------------------------------------------------------------
    def norm(v):
        if pd.isna(v):
            return ""
        z = unicodedata.normalize("NFKC", str(v)).casefold()
        z = re.sub(r"\s+", "", z)
        return re.sub(r"[・･\.\-_'’`]", "", z)

    def shirt(v):
        z = pd.to_numeric(pd.Series([v]), errors="coerce").iloc[0]
        return None if pd.isna(z) else int(z)

    def stable_strength_key(name, club, position, birthday):
        b = pd.to_numeric(
            pd.Series([birthday]), errors="coerce"
        ).iloc[0]
        b = None if pd.isna(b) else int(b)
        return (
            norm(name),
            norm(club),
            norm(position),
            b,
        )

    xi_df = pd.read_csv(xi, low_memory=False)
    old = pd.read_csv(old_master, low_memory=False)
    fm = pd.read_csv(fs_master, low_memory=False)
    strength_df = pd.read_csv(fs_strength, low_memory=False)

    if len(xi_df) != 286:
        raise RuntimeError(
            f"expected 286 predicted-XI rows, got {len(xi_df)}"
        )

    # ------------------------------------------------------------
    # Frozen old-canonical lookup.
    # Shirt number is an explicit guard, not merely name matching.
    # ------------------------------------------------------------
    old_lookup = defaultdict(list)

    for _, r in old.iterrows():
        old_lookup[
            (
                str(r["toto_team"]),
                norm(r["jleague_player_name"]),
            )
        ].append(r)

    # ------------------------------------------------------------
    # FootyStats current identity layer: club + shirt.
    # ------------------------------------------------------------
    clubshirt = defaultdict(list)

    for _, r in fm.iterrows():
        clubshirt[
            (
                norm(r["Current Club"]),
                shirt(r["shirt_number"]),
            )
        ].append(r)

    # Stable identity -> strength.
    strength_lookup = {}

    for _, r in strength_df.iterrows():
        k = stable_strength_key(
            r["full_name"],
            r["Current Club"],
            r["position"],
            r["birthday"],
        )
        if k in strength_lookup:
            raise RuntimeError(
                f"duplicate FS strength identity key: {k}"
            )
        strength_lookup[k] = r

    # Recover historical toto-team -> FS-club aliases where unique.
    alias_sets = defaultdict(set)

    for _, r in old.iterrows():
        if pd.notna(r["fs_club"]):
            alias_sets[str(r["toto_team"])].add(
                str(r["fs_club"])
            )

    team_alias = {
        k: next(iter(v))
        for k, v in alias_sets.items()
        if len(v) == 1
    }

    # Round1658 new clubs validated during frozen transport research.
    # Keep explicit rather than fuzzy club matching.
    if rnd == 1658:
        team_alias.update({
            "G大阪": "Gamba Osaka",
            "京都": "Kyoto Sanga",
            "柏": "Kashiwa Reysol",
            "町田": "Machida Zelvia",
            "讃岐": "Kamatamare Sanuki",
            "琉球": "Ryūkyū",
            "金沢": "Zweigen Kanazawa",
        })

    axes = [
        "fs_attack_power",
        "fs_finishing_power",
        "fs_build_up_power",
        "fs_width_carry_power",
        "fs_defensive_power",
        "fs_keeper_power",
    ]

    resolved = []

    for _, r in xi_df.iterrows():
        z = r.to_dict()

        team = str(r["team"])
        pname = r["player_name"]
        pshirt = shirt(r["shirt_number"])

        # Known frozen conflict discovered during 1658 audit.
        known_conflict = (
            rnd == 1658
            and team == "新潟"
            and norm(pname) == norm("関口正大")
        )

        candidates = old_lookup.get(
            (team, norm(pname)), []
        )

        # Old canonical reuse requires unique identity AND shirt match.
        old_hit = None
        if len(candidates) == 1:
            c = candidates[0]
            old_shirt = shirt(c["jleague_uniform_no"])
            if old_shirt == pshirt:
                old_hit = c

        if old_hit is not None:
            z["identity_method"] = "OLD_MASTER_CANONICAL"
            z["identity_status"] = "ACCEPTED"
            z["fs_full_name"] = old_hit["fs_full_name"]
            z["fs_club"] = old_hit["fs_club"]
            z["fs_position"] = old_hit["fs_position"]
            z["fs_league"] = old_hit["fs_league"]
            z["fs_identity_key"] = old_hit["fs_identity_key"]
            z["fs_minutes"] = old_hit["minutes_played_overall"]
            z["fs_reliability"] = old_hit["fs_reliability"]
            for c in axes:
                z[c] = old_hit[c]

        elif known_conflict:
            z["identity_method"] = "IDENTITY_CONFLICT"
            z["identity_status"] = "REJECTED"
            z["fs_full_name"] = np.nan
            z["fs_club"] = np.nan
            z["fs_position"] = np.nan
            z["fs_league"] = np.nan
            z["fs_identity_key"] = np.nan
            z["fs_minutes"] = np.nan
            z["fs_reliability"] = np.nan
            for c in axes:
                z[c] = np.nan

        else:
            alias = team_alias.get(team)
            hits = (
                clubshirt.get(
                    (norm(alias), pshirt), []
                )
                if alias is not None
                else []
            )

            if len(hits) == 1:
                c = hits[0]
                k = stable_strength_key(
                    c["full_name"],
                    c["Current Club"],
                    c["position"],
                    c["birthday"],
                )
                sr = strength_lookup.get(k)

                if sr is None:
                    raise RuntimeError(
                        "validated FS identity has no strength: "
                        f"{team} {pname}"
                    )

                z["identity_method"] = (
                    "FS_CLUB_SHIRT_VALIDATED"
                )
                z["identity_status"] = "ACCEPTED"
                z["fs_full_name"] = c["full_name"]
                z["fs_club"] = c["Current Club"]
                z["fs_position"] = c["position"]
                z["fs_league"] = c["fs_league"]
                z["fs_identity_key"] = c["fs_identity_key"]
                z["fs_minutes"] = sr["minutes_played_overall"]
                z["fs_reliability"] = sr["fs_reliability"]
                for col in axes:
                    z[col] = sr[col]

            else:
                z["identity_method"] = "UNRESOLVED"
                z["identity_status"] = "UNKNOWN"
                z["fs_full_name"] = np.nan
                z["fs_club"] = np.nan
                z["fs_position"] = np.nan
                z["fs_league"] = np.nan
                z["fs_identity_key"] = np.nan
                z["fs_minutes"] = np.nan
                z["fs_reliability"] = np.nan
                for col in axes:
                    z[col] = np.nan

        z["production_player_coefficient"] = 0.0
        z["transport_status"] = (
            "RESEARCH_ONLY_UNCALIBRATED"
        )
        resolved.append(z)

    out = pd.DataFrame(resolved)

    counts = (
        out["identity_method"]
        .value_counts()
        .to_dict()
    )

    expected_1658 = {
        "OLD_MASTER_CANONICAL": 193,
        "FS_CLUB_SHIRT_VALIDATED": 72,
        "UNRESOLVED": 20,
        "IDENTITY_CONFLICT": 1,
    }

    accepted = out["identity_status"].eq("ACCEPTED")
    strength_reached = (
        out.loc[accepted, "fs_attack_power"]
        .notna()
        .sum()
    )

    print()
    print("=== IDENTITY TRANSPORT QA ===")
    print("XI_ROWS =", len(out))
    for k in [
        "OLD_MASTER_CANONICAL",
        "FS_CLUB_SHIRT_VALIDATED",
        "UNRESOLVED",
        "IDENTITY_CONFLICT",
    ]:
        print(k, "=", counts.get(k, 0))

    print("ACCEPTED_IDENTITY =", int(accepted.sum()))
    print(
        "IDENTITY_COVERAGE =",
        f"{accepted.mean()*100:.2f}%"
    )
    print("STRENGTH_RECORD_REACHED =", strength_reached)

    side_counts = (
        out.groupby(
            ["match_no", "side", "team"],
            dropna=False
        )
        .agg(
            xi_players=("player_name", "size"),
            accepted=("identity_status",
                      lambda x: (x == "ACCEPTED").sum()),
        )
        .reset_index()
    )

    print()
    print("=== SIDE COVERAGE ===")
    print(side_counts.to_string(index=False))

    unresolved = out.loc[
        ~accepted,
        [
            "match_no",
            "side",
            "team",
            "shirt_number",
            "player_name",
            "identity_method",
        ],
    ]

    print()
    print("=== UNRESOLVED / CONFLICT ===")
    print(unresolved.to_string(index=False))

    if rnd == 1658:
        if counts != expected_1658:
            raise RuntimeError(
                "1658 frozen identity counts changed: "
                f"actual={counts}, expected={expected_1658}"
            )
        if int(accepted.sum()) != 265:
            raise RuntimeError(
                f"1658 accepted identity expected 265, "
                f"got {int(accepted.sum())}"
            )
        if strength_reached != 265:
            raise RuntimeError(
                f"1658 strength reached expected 265, "
                f"got {strength_reached}"
            )

    if not side_counts["xi_players"].eq(11).all():
        raise RuntimeError(
            "not all match/side groups contain exactly 11 XI players"
        )

    # ------------------------------------------------------------
    # Freeze reproducible player-level research artifacts
    # ------------------------------------------------------------
    out_dir = Path("data/analysis")
    out_dir.mkdir(parents=True, exist_ok=True)

    player_out = out_dir / (
        f"toto{rnd}_xi_fs_player_frozen_transport_v01.csv"
    )
    unresolved_out = out_dir / (
        f"toto{rnd}_xi_fs_unresolved_audit_v01.csv"
    )
    coverage_out = out_dir / (
        f"toto{rnd}_xi_fs_side_coverage_v01.csv"
    )

    # Preserve exact source lineage inside the frozen player artifact.
    out["source_totoone_xi"] = str(xi)
    out["source_old_master"] = str(old_master)
    out["source_fs_master"] = str(fs_master)
    out["source_fs_strength"] = str(fs_strength)
    out["result_input_used"] = 0
    out["p_base_mutated"] = 0
    out["second_reliability_weight"] = 0

    out.to_csv(player_out, index=False)
    unresolved.to_csv(unresolved_out, index=False)
    side_counts.to_csv(coverage_out, index=False)

    # Read-back QA: freeze must reproduce what was in memory.
    frozen = pd.read_csv(player_out, low_memory=False)

    if len(frozen) != len(out):
        raise RuntimeError(
            "frozen player artifact row count changed"
        )

    frozen_counts = (
        frozen["identity_method"]
        .value_counts()
        .to_dict()
    )

    if frozen_counts != counts:
        raise RuntimeError(
            "frozen identity counts differ from in-memory QA"
        )

    if not frozen["production_player_coefficient"].eq(0.0).all():
        raise RuntimeError(
            "non-zero production player coefficient in frozen artifact"
        )

    print()
    print("=== FROZEN ARTIFACTS ===")
    print("PLAYER =", player_out)
    print("UNRESOLVED_AUDIT =", unresolved_out)
    print("SIDE_COVERAGE =", coverage_out)
    print("PLAYER_ROWS_READBACK =", len(frozen))
    print("FROZEN_IDENTITY_COUNTS =", frozen_counts)

    print()
    print("RESULT_COLUMNS_USED = NONE")
    print("P_BASE_MUTATED = NO")
    print("SECOND_RELIABILITY_WEIGHT = NO")
    print("PRODUCTION_PLAYER_COEFFICIENT = 0.0")
    print("IDENTITY_TRANSPORT_QA = PASS")
    print("PLAYER_FROZEN_ARTIFACT_QA = PASS")


if __name__ == "__main__":
    main()
