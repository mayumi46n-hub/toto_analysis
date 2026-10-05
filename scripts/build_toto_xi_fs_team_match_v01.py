#!/usr/bin/env python3

from pathlib import Path
import argparse
import unicodedata
import numpy as np
import pandas as pd


AXES = [
    "fs_attack_power",
    "fs_finishing_power",
    "fs_build_up_power",
    "fs_width_carry_power",
    "fs_defensive_power",
]


def posgrp(x):
    if pd.isna(x):
        return None

    s = unicodedata.normalize("NFKC", str(x)).upper().strip()

    if s == "GK" or "GOALKEEPER" in s or "KEEPER" in s:
        return "GK"

    if (
        s == "DF"
        or "DEFENDER" in s
        or "CENTRE BACK" in s
        or "CENTER BACK" in s
        or s in {"CB", "LB", "RB", "LWB", "RWB"}
    ):
        return "DF"

    if (
        s == "FW"
        or "FORWARD" in s
        or "CENTRE FORWARD" in s
        or "CENTER FORWARD" in s
        or "STRIKER" in s
        or s in {"CF", "LW", "RW"}
    ):
        return "FW"

    return "MF"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    args = ap.parse_args()
    rnd = args.round

    player_path = Path(
        f"data/analysis/toto{rnd}_xi_fs_player_frozen_transport_v01.csv"
    )
    fs_path = Path(
        "data/players/footystats_2026_player_strength_full_v02.csv"
    )

    if not player_path.exists():
        raise FileNotFoundError(player_path)
    if not fs_path.exists():
        raise FileNotFoundError(fs_path)

    d = pd.read_csv(player_path, low_memory=False).copy()
    fs = pd.read_csv(fs_path, low_memory=False).copy()

    if len(d) != 286:
        raise RuntimeError(f"player rows expected 286, got {len(d)}")

    groups = d.groupby(["match_no", "side", "team"]).size()
    if len(groups) != 26 or not groups.eq(11).all():
        raise RuntimeError("expected 26 sides x exactly 11 players")

    # ---------------------------------------------------------
    # Baselines: exact recovered 1656 hierarchy.
    # ---------------------------------------------------------
    fs["_posgrp"] = fs["position"].map(posgrp)

    baseline = fs.groupby(
        ["fs_league", "_posgrp"]
    )[AXES].median()

    league_baseline = fs.groupby(
        "fs_league"
    )[AXES].median()

    global_baseline = fs[AXES].median()

    # Team league is learned only from resolved teammates.
    team_league = {}

    for key, g in d.groupby(["match_no", "side", "team"]):
        z = g["fs_league"].dropna()
        if z.empty:
            raise RuntimeError(f"{key}: no observed league")

        mode = z.mode()
        if len(mode) != 1:
            raise RuntimeError(
                f"{key}: ambiguous league {mode.tolist()}"
            )

        team_league[key] = mode.iloc[0]

    # ---------------------------------------------------------
    # Player-level legacy research imputation.
    #
    # Critical 1658 rule:
    # unresolved identity => position remains UNKNOWN.
    # Therefore no league-position baseline is invented.
    # ---------------------------------------------------------
    for a in AXES:
        d[f"{a}_legacy"] = pd.to_numeric(
            d[a], errors="coerce"
        )
        d[f"{a}_imputation_method"] = ""

    d["xi_imputed_axis_count"] = 0

    for idx, r in d.iterrows():
        key = (r["match_no"], r["side"], r["team"])
        league = team_league[key]

        pg = (
            posgrp(r["fs_position"])
            if pd.notna(r["fs_position"])
            else None
        )

        for a in AXES:
            outcol = f"{a}_legacy"

            if pd.notna(d.at[idx, outcol]):
                continue

            value = np.nan
            method = None

            if pg is not None:
                try:
                    value = baseline.loc[(league, pg), a]
                    method = "LEAGUE_POSITION_MEDIAN"
                except Exception:
                    pass

            if pd.isna(value):
                try:
                    value = league_baseline.loc[league, a]
                    method = "LEAGUE_MEDIAN"
                except Exception:
                    pass

            if pd.isna(value):
                value = global_baseline[a]
                method = "GLOBAL_MEDIAN"

            d.at[idx, outcol] = value
            d.at[idx, f"{a}_imputation_method"] = method
            d.at[idx, "xi_imputed_axis_count"] += 1

    legacy_cols = [f"{a}_legacy" for a in AXES]

    if d[legacy_cols].isna().any().any():
        raise RuntimeError("legacy axis missing after imputation")

    # No second reliability weighting.
    d["xi_player_overall_5axis_legacy"] = (
        d[legacy_cols].mean(axis=1)
    )

    # ---------------------------------------------------------
    # Team VALUE / COVERAGE / SENSITIVITY / KEEPER
    # ---------------------------------------------------------
    rows = []

    for key, g in d.groupby(
        ["match_no", "side", "team"], sort=True
    ):
        match_no, side, team_name = key
        league = team_league[key]

        accepted = g["identity_status"].eq("ACCEPTED")
        gk = g["fs_position"].map(posgrp).eq("GK")

        if int(gk.sum()) > 1:
            raise RuntimeError(
                f"{key}: multiple resolved starting GK"
            )

        keeper_known = int(gk.sum()) == 1
        keeper = (
            pd.to_numeric(
                g.loc[gk, "fs_keeper_power"],
                errors="coerce"
            ).iloc[0]
            if keeper_known
            else np.nan
        )

        row = {
            "match_no": match_no,
            "side": side,
            "team": team_name,
            "league": league,
            "formation": g["formation"].iloc[0],
            "starters": 11,
            "observed_players": int(accepted.sum()),
            "unknown_players": int((~accepted).sum()),
            "identity_coverage": float(accepted.mean()),
            "resolved_gk_count": int(gk.sum()),
            "keeper_identity_known": keeper_known,
            "xi_keeper_observed": keeper,
        }

        deltas = []

        for a in AXES:
            obs = pd.to_numeric(
                g[a], errors="coerce"
            ).mean()

            legacy = pd.to_numeric(
                g[f"{a}_legacy"],
                errors="coerce"
            ).mean()

            delta = obs - legacy

            short = a.removeprefix("fs_").removesuffix("_power")

            row[f"xi_{short}_observed"] = obs
            row[f"xi_{short}_legacy"] = legacy
            row[f"xi_{short}_sensitivity_delta"] = delta

            if pd.notna(delta):
                deltas.append(abs(float(delta)))

        row["max_abs_sensitivity_delta"] = (
            max(deltas) if deltas else np.nan
        )

        row["imputed_axis_count"] = int(
            d.loc[g.index, "xi_imputed_axis_count"].sum()
        )

        row["xi_overall_5axis_legacy"] = float(
            g["xi_player_overall_5axis_legacy"].mean()
        )

        row["xi_mean_reliability_observed"] = pd.to_numeric(
            g["fs_reliability"], errors="coerce"
        ).mean()

        rows.append(row)

    team = pd.DataFrame(rows)

    if len(team) != 26:
        raise RuntimeError(f"team rows expected 26, got {len(team)}")

    if int(team["keeper_identity_known"].sum()) != 24:
        raise RuntimeError(
            "expected exactly 24 sides with resolved GK"
        )

    missing_gk = set(
        team.loc[
            ~team["keeper_identity_known"], "team"
        ]
    )

    if rnd == 1658 and missing_gk != {"柏", "磐田"}:
        raise RuntimeError(
            f"1658 missing GK changed: {missing_gk}"
        )

    # ---------------------------------------------------------
    # Match layer.
    # No external card/result file is read.
    # HOME/AWAY pairing comes only from frozen XI artifact.
    # ---------------------------------------------------------
    mrows = []

    for match_no, g in team.groupby("match_no", sort=True):
        h = g[g["side"].eq("home")]
        a = g[g["side"].eq("away")]

        if len(h) != 1 or len(a) != 1:
            raise RuntimeError(
                f"match {match_no}: HOME/AWAY pairing failure"
            )

        h = h.iloc[0]
        a = a.iloc[0]

        r = {
            "match_no": int(match_no),
            "home_team": h["team"],
            "away_team": a["team"],
            "home_formation": h["formation"],
            "away_formation": a["formation"],
            "home_identity_coverage": h["identity_coverage"],
            "away_identity_coverage": a["identity_coverage"],
            "home_max_abs_sensitivity_delta":
                h["max_abs_sensitivity_delta"],
            "away_max_abs_sensitivity_delta":
                a["max_abs_sensitivity_delta"],
            "home_keeper_identity_known":
                h["keeper_identity_known"],
            "away_keeper_identity_known":
                a["keeper_identity_known"],
        }

        for short in [
            "attack",
            "finishing",
            "build_up",
            "width_carry",
            "defensive",
        ]:
            hv = h[f"xi_{short}_legacy"]
            av = a[f"xi_{short}_legacy"]

            r[f"home_xi_{short}"] = hv
            r[f"away_xi_{short}"] = av
            r[f"gap_xi_{short}"] = hv - av

        r["home_xi_keeper"] = h["xi_keeper_observed"]
        r["away_xi_keeper"] = a["xi_keeper_observed"]

        if (
            pd.notna(r["home_xi_keeper"])
            and pd.notna(r["away_xi_keeper"])
        ):
            r["gap_xi_keeper"] = (
                r["home_xi_keeper"]
                - r["away_xi_keeper"]
            )
        else:
            r["gap_xi_keeper"] = np.nan

        r["home_xi_overall_5axis"] = (
            h["xi_overall_5axis_legacy"]
        )
        r["away_xi_overall_5axis"] = (
            a["xi_overall_5axis_legacy"]
        )
        r["gap_xi_overall_5axis"] = (
            r["home_xi_overall_5axis"]
            - r["away_xi_overall_5axis"]
        )

        # Recovered 1656 functional channels.
        # Positive = HOME structural advantage.
        r["XI_ATTACK_VS_DEF_GAP"] = (
            (r["home_xi_attack"] - r["away_xi_defensive"])
            - (r["away_xi_attack"] - r["home_xi_defensive"])
        )

        r["XI_BUILD_VS_DEF_GAP"] = (
            (r["home_xi_build_up"] - r["away_xi_defensive"])
            - (r["away_xi_build_up"] - r["home_xi_defensive"])
        )

        r["XI_WIDTH_VS_DEF_GAP"] = (
            (r["home_xi_width_carry"] - r["away_xi_defensive"])
            - (r["away_xi_width_carry"] - r["home_xi_defensive"])
        )

        # Never invent an unidentified GK.
        if (
            pd.notna(r["home_xi_keeper"])
            and pd.notna(r["away_xi_keeper"])
        ):
            r["XI_FINISH_VS_KEEPER_GAP"] = (
                (r["home_xi_finishing"] - r["away_xi_keeper"])
                - (r["away_xi_finishing"] - r["home_xi_keeper"])
            )
            r["XI_FINISH_VS_KEEPER_STATUS"] = "AVAILABLE"
        else:
            r["XI_FINISH_VS_KEEPER_GAP"] = np.nan
            r["XI_FINISH_VS_KEEPER_STATUS"] = (
                "BLOCKED_UNKNOWN_GK"
            )

        r["XI_HOME_STRENGTH"] = r["home_xi_overall_5axis"]
        r["XI_AWAY_STRENGTH"] = r["away_xi_overall_5axis"]
        r["XI_STRENGTH_GAP"] = r["gap_xi_overall_5axis"]

        r["XI_DIRECT_GOAL_HAZARD_TRANSPORT"] = 0
        r["XI_PRODUCTION_BETA"] = 0.0
        r["production_player_coefficient"] = 0.0
        r["XI_TRANSPORT_STATUS"] = (
            "RESEARCH_ONLY_UNCALIBRATED"
        )

        mrows.append(r)

    match = pd.DataFrame(mrows)

    if len(match) != 13:
        raise RuntimeError(
            f"match rows expected 13, got {len(match)}"
        )

    blocked = match[
        "XI_FINISH_VS_KEEPER_STATUS"
    ].eq("BLOCKED_UNKNOWN_GK")

    if rnd == 1658:
        blocked_matches = set(
            match.loc[blocked, "match_no"].astype(int)
        )
        if blocked_matches != {2, 9}:
            raise RuntimeError(
                f"blocked GK matches changed: {blocked_matches}"
            )

    # ---------------------------------------------------------
    # Freeze artifacts
    # ---------------------------------------------------------
    outdir = Path("data/analysis")
    player_out = outdir / (
        f"toto{rnd}_xi_fs_player_legacy_imputed_v01.csv"
    )
    team_out = outdir / (
        f"toto{rnd}_xi_fs_team_value_coverage_sensitivity_v01.csv"
    )
    match_out = outdir / (
        f"toto{rnd}_xi_fs_match_research_channels_v01.csv"
    )

    d.to_csv(player_out, index=False)
    team.to_csv(team_out, index=False)
    match.to_csv(match_out, index=False)

    print("=== TOTO XI FS TEAM/MATCH V01 ===")
    print("ROUND =", rnd)
    print("PLAYER_INPUT =", player_path)
    print("PLAYER_ROWS =", len(d))
    print("TEAM_ROWS =", len(team))
    print("MATCH_ROWS =", len(match))
    print("RESOLVED_GK_SIDES =", int(team["keeper_identity_known"].sum()))
    print(
        "BLOCKED_FINISH_VS_KEEPER_MATCHES =",
        match.loc[
            blocked, "match_no"
        ].astype(int).tolist()
    )

    print()
    print("=== SENSITIVITY ===")
    print(
        team[
            [
                "match_no",
                "side",
                "team",
                "observed_players",
                "unknown_players",
                "identity_coverage",
                "max_abs_sensitivity_delta",
                "keeper_identity_known",
            ]
        ]
        .sort_values(
            "max_abs_sensitivity_delta",
            ascending=False
        )
        .to_string(index=False)
    )

    print()
    print("PLAYER_OUT =", player_out)
    print("TEAM_OUT =", team_out)
    print("MATCH_OUT =", match_out)

    print()
    print("UNKNOWN_POSITION_INVENTED = NO")
    print("UNKNOWN_GK_IMPUTED = NO")
    print("SECOND_RELIABILITY_WEIGHT = NO")
    print("NEW_ROLE_WEIGHTS = NONE")
    print("RESULT_COLUMNS_USED = NONE")
    print("P_BASE_MUTATED = NO")
    print("XI_DIRECT_GOAL_HAZARD_TRANSPORT = 0")
    print("XI_PRODUCTION_BETA = 0.0")
    print("PRODUCTION_PLAYER_COEFFICIENT = 0.0")
    print("XI_TRANSPORT_STATUS = RESEARCH_ONLY_UNCALIBRATED")
    print("TEAM_MATCH_FROZEN_QA = PASS")


if __name__ == "__main__":
    main()
