#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import math
import re

import numpy as np
import pandas as pd


def num(x):
    if x is None:
        return np.nan

    s = str(x).strip()
    if not s:
        return np.nan

    s = (
        s.replace(",", "")
         .replace("%", "")
         .replace("−", "-")
         .replace("–", "-")
    )

    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return np.nan

    try:
        return float(m.group())
    except ValueError:
        return np.nan


def pct_fraction(x):
    v = num(x)
    if pd.isna(v):
        return np.nan
    return v / 100.0


def side(x, threshold):
    if pd.isna(x):
        return "NA"
    if x >= threshold:
        return "HOME"
    if x <= -threshold:
        return "AWAY"
    return "NEUTRAL"


def semantic_two_side(a, athr, b, bthr):
    sa = side(a, athr)
    sb = side(b, bthr)

    directional = {"HOME", "AWAY"}

    if sa in directional and sb in directional:
        if sa == sb:
            return sa
        return "SPLIT"

    if sa in directional:
        return sa

    if sb in directional:
        return sb

    if sa == "NA" and sb == "NA":
        return "NA"

    return "NEUTRAL"


def find_table(page, title):
    title_l = str(title).strip().lower()

    for t in page.get("tables", []):
        tt = str(t.get("title", "")).strip()
        if tt.lower() == title_l:
            return t

    return None


def table_by_index(page, idx):
    for t in page.get("tables", []):
        if t.get("table_index") == idx:
            return t
    return None


def table_row_map(table):
    out = {}

    if not table:
        return out

    for row in table.get("rows", []):
        if not row:
            continue

        key = str(row[0]).strip()
        if key:
            out[key] = row

    return out


def cell(row, idx):
    if row is None:
        return np.nan
    if len(row) <= idx:
        return np.nan
    return num(row[idx])


def extract_compact_form(page, venue):
    """
    Japanese compact team page.

    Expected row:
    ホーム/アウェイ | games | wins | draws | losses | recent | PPG
    """
    t = table_by_index(page, 2)

    if not t:
        return None

    wanted = "ホーム" if venue == "home" else "アウェイ"

    for row in t.get("rows", []):
        if not row:
            continue

        if str(row[0]).strip() != wanted:
            continue

        if len(row) < 6:
            continue

        return {
            "games": num(row[1]) if len(row) > 1 else np.nan,
            "wins": num(row[2]) if len(row) > 2 else np.nan,
            "draws": num(row[3]) if len(row) > 3 else np.nan,
            "losses": num(row[4]) if len(row) > 4 else np.nan,
            "ppg": num(row[-1]),
            "source": "COMPACT_EXACT_PPG",
        }

    return None


def extract_expanded_venue(page, venue):
    """
    Expanded English team page.

    Table structure:
      metric | Overall | At Home | At Away

    home page -> At Home index 2
    away page -> At Away index 3
    """
    idx = 2 if venue == "home" else 3

    stats = find_table(page, "Stats")
    shots = find_table(page, "Team Shots")

    if not stats:
        return {
            "available": False,
            "source": "NO_EXPLICIT_VENUE_TABLE",
        }

    sm = table_row_map(stats)
    tm = table_row_map(shots)

    wins = cell(sm.get("Wins"), idx)
    draws = cell(sm.get("Draws"), idx)
    losses = cell(sm.get("Losses"), idx)

    if not pd.isna(wins):
        wins_frac = wins / 100.0
    else:
        wins_frac = np.nan

    if not pd.isna(draws):
        draws_frac = draws / 100.0
    else:
        draws_frac = np.nan

    if not pd.isna(losses):
        losses_frac = losses / 100.0
    else:
        losses_frac = np.nan

    if not pd.isna(wins_frac) and not pd.isna(draws_frac):
        form_ppg_est = 3.0 * wins_frac + draws_frac
    else:
        form_ppg_est = np.nan

    def metric(name):
        return cell(sm.get(name), idx)

    def shot_metric(name):
        if not shots:
            return np.nan
        return cell(tm.get(name), idx)

    return {
        "available": True,
        "source": "EXPANDED_EXPLICIT_VENUE",
        "win_pct": wins,
        "draw_pct": draws,
        "loss_pct": losses,
        "form_ppg_est": form_ppg_est,
        "xg": metric("xG For / Match"),
        "xga": metric("xG Against / Match"),
        "possession": metric("Possession AVG"),
        "shots": shot_metric("Shots / Match"),
        "sot": shot_metric("Shots On Target / Match"),
        "conversion": shot_metric("Shots Conversion Rate"),
        "shots_per_goal": shot_metric("Shots Per Goal Scored"),
    }


def get_form(page, venue):
    exact = extract_compact_form(page, venue)

    if exact is not None:
        return exact["ppg"], exact["source"]

    expanded = extract_expanded_venue(page, venue)

    if expanded.get("available"):
        return (
            expanded.get("form_ppg_est", np.nan),
            "EXPANDED_PCT_EST_PPG",
        )

    return np.nan, "MISSING"


def opposite_direction(a, b):
    if a not in {"HOME", "AWAY"}:
        return False
    if b not in {"HOME", "AWAY"}:
        return False
    return a != b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--normalized", default=None)
    ap.add_argument("--blocks", default=None)
    ap.add_argument("--raw-root", default=None)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    norm_path = Path(
        args.normalized
        or f"data/analysis/footystats_toto{args.round}_normalized_v04.csv"
    )

    block_path = Path(
        args.blocks
        or f"data/analysis/footystats_toto{args.round}_feature_blocks_v02.csv"
    )

    raw_root = Path(
        args.raw_root
        or f"data/parsed/footystats/toto{args.round}_full_v01"
    )

    out_path = Path(
        args.output
        or f"data/analysis/footystats_toto{args.round}_feature_semantic_v04.csv"
    )

    for p in [norm_path, block_path, raw_root]:
        if not p.exists():
            raise SystemExit(f"STOP: missing {p}")

    norm = pd.read_csv(norm_path)
    blocks = pd.read_csv(block_path)

    if len(norm) != 13:
        raise SystemExit(
            f"STOP: normalized rows={len(norm)}"
        )

    if len(blocks) != 13:
        raise SystemExit(
            f"STOP: block rows={len(blocks)}"
        )

    rows = []

    for _, n in norm.sort_values("match_no").iterrows():
        no = int(n["match_no"])

        candidates = sorted(
            raw_root.glob(
                f"toto{args.round}_{no:02d}_full_v*.json"
            )
        )

        if len(candidates) != 1:
            raise SystemExit(
                f"STOP: FULL RAW candidates No{no:02d}="
                f"{len(candidates)} {[x.name for x in candidates]}"
            )

        full_path = candidates[0]

        obj = json.loads(
            full_path.read_text(encoding="utf-8")
        )

        pages = obj["pages"]

        home_page = pages["home"]
        away_page = pages["away"]

        home_exp = extract_expanded_venue(
            home_page,
            "home"
        )

        away_exp = extract_expanded_venue(
            away_page,
            "away"
        )

        home_form_ppg, home_form_source = get_form(
            home_page,
            "home"
        )

        away_form_ppg, away_form_source = get_form(
            away_page,
            "away"
        )

        bmatch = blocks.loc[
            blocks["match_no"] == no
        ]

        if len(bmatch) != 1:
            raise SystemExit(
                f"STOP: block row No{no:02d} count={len(bmatch)}"
            )

        b = bmatch.iloc[0]

        # ====================================================
        # A. VENUE BASE
        # ====================================================

        venue_xg_edge = (
            n["home_xg_venue"]
            - n["away_xg_venue"]
        )

        # positive = HOME defensive edge
        venue_xga_def_edge = (
            n["away_xga_venue"]
            - n["home_xga_venue"]
        )

        if (
            not pd.isna(home_form_ppg)
            and not pd.isna(away_form_ppg)
        ):
            venue_form_edge = (
                home_form_ppg
                - away_form_ppg
            )
        else:
            venue_form_edge = np.nan

        # ====================================================
        # B. MATCH PAGE CONTEXT
        #
        # These come from the match/H2H comparison page.
        # Do NOT label them venue-specific.
        # ====================================================

        ctx_shots_edge = (
            n["shots_home"]
            - n["shots_away"]
        )

        ctx_sot_edge = (
            n["sot_home"]
            - n["sot_away"]
        )

        ctx_conversion_edge = (
            n["shot_conversion_home"]
            - n["shot_conversion_away"]
        )

        # fewer shots per goal = better
        ctx_spg_edge = (
            n["shots_per_goal_away"]
            - n["shots_per_goal_home"]
        )

        ctx_possession_edge = (
            n["possession_home"]
            - n["possession_away"]
        )

        ctx_finishing_side = semantic_two_side(
            ctx_conversion_edge,
            3.0,
            ctx_spg_edge,
            2.0,
        )

        # ====================================================
        # C. EXPLICIT VENUE DETAIL
        #
        # Only use when BOTH pages expose explicit
        # Overall / At Home / At Away tables.
        # Never fill from another semantic source.
        # ====================================================

        explicit_pair = bool(
            home_exp.get("available")
            and away_exp.get("available")
        )

        if explicit_pair:
            venue_detail_shots_edge = (
                home_exp["shots"]
                - away_exp["shots"]
            )

            venue_detail_sot_edge = (
                home_exp["sot"]
                - away_exp["sot"]
            )

            venue_detail_conversion_edge = (
                home_exp["conversion"]
                - away_exp["conversion"]
            )

            venue_detail_spg_edge = (
                away_exp["shots_per_goal"]
                - home_exp["shots_per_goal"]
            )

            venue_detail_possession_edge = (
                home_exp["possession"]
                - away_exp["possession"]
            )

            venue_finishing_side = semantic_two_side(
                venue_detail_conversion_edge,
                3.0,
                venue_detail_spg_edge,
                2.0,
            )

            venue_shot_volume_side = semantic_two_side(
                venue_detail_shots_edge,
                2.0,
                venue_detail_sot_edge,
                1.0,
            )

            venue_possession_side = side(
                venue_detail_possession_edge,
                3.0,
            )
        else:
            venue_detail_shots_edge = np.nan
            venue_detail_sot_edge = np.nan
            venue_detail_conversion_edge = np.nan
            venue_detail_spg_edge = np.nan
            venue_detail_possession_edge = np.nan
            venue_finishing_side = "NA"
            venue_shot_volume_side = "NA"
            venue_possession_side = "NA"

        ctx_shot_volume_side = semantic_two_side(
            ctx_shots_edge,
            2.0,
            ctx_sot_edge,
            1.0,
        )

        ctx_possession_side = side(
            ctx_possession_edge,
            3.0,
        )

        finishing_semantic_split = (
            opposite_direction(
                ctx_finishing_side,
                venue_finishing_side,
            )
        )

        shot_volume_semantic_split = (
            opposite_direction(
                ctx_shot_volume_side,
                venue_shot_volume_side,
            )
        )

        possession_semantic_split = (
            opposite_direction(
                ctx_possession_side,
                venue_possession_side,
            )
        )

        # ====================================================
        # D. Cross-check normalized venue xG against explicit
        # venue table where available.
        # ====================================================

        xg_crosscheck = "NOT_AVAILABLE"

        if explicit_pair:
            diffs = []

            pairs = [
                (
                    n["home_xg_venue"],
                    home_exp.get("xg"),
                ),
                (
                    n["away_xg_venue"],
                    away_exp.get("xg"),
                ),
                (
                    n["home_xga_venue"],
                    home_exp.get("xga"),
                ),
                (
                    n["away_xga_venue"],
                    away_exp.get("xga"),
                ),
            ]

            usable = True

            for a, c in pairs:
                if pd.isna(a) or pd.isna(c):
                    usable = False
                    break
                diffs.append(abs(float(a) - float(c)))

            if usable:
                if max(diffs) <= 0.011:
                    xg_crosscheck = "PASS"
                else:
                    xg_crosscheck = "MISMATCH"
            else:
                xg_crosscheck = "PARTIAL"

        flags = []

        if finishing_semantic_split:
            flags.append("FINISHING_SEMANTIC_SPLIT")

        if shot_volume_semantic_split:
            flags.append("SHOT_VOLUME_SEMANTIC_SPLIT")

        if possession_semantic_split:
            flags.append("POSSESSION_SEMANTIC_SPLIT")

        if xg_crosscheck == "MISMATCH":
            flags.append("XG_CROSSCHECK_MISMATCH")

        if not explicit_pair:
            flags.append("VENUE_DETAIL_UNAVAILABLE")

        semantic_flags = (
            "|".join(flags)
            if flags
            else "OK"
        )

        rows.append({
            "round": args.round,
            "match_no": no,
            "home_team": n["home_team"],
            "away_team": n["away_team"],

            # -----------------------------------------------
            # VENUE BASE
            # -----------------------------------------------
            "venue_home_xg": n["home_xg_venue"],
            "venue_away_xg": n["away_xg_venue"],
            "venue_xg_edge": venue_xg_edge,
            "venue_xg_side": side(
                venue_xg_edge,
                0.20,
            ),

            "venue_home_xga": n["home_xga_venue"],
            "venue_away_xga": n["away_xga_venue"],
            "venue_xga_def_edge": venue_xga_def_edge,
            "venue_xga_def_side": side(
                venue_xga_def_edge,
                0.20,
            ),

            "home_form_ppg": home_form_ppg,
            "away_form_ppg": away_form_ppg,
            "venue_form_edge": venue_form_edge,
            "venue_form_side": side(
                venue_form_edge,
                0.50,
            ),
            "home_form_source": home_form_source,
            "away_form_source": away_form_source,

            # -----------------------------------------------
            # MATCH PAGE CONTEXT
            # -----------------------------------------------
            "ctx_home_shots": n["shots_home"],
            "ctx_away_shots": n["shots_away"],
            "ctx_shots_edge": ctx_shots_edge,

            "ctx_home_sot": n["sot_home"],
            "ctx_away_sot": n["sot_away"],
            "ctx_sot_edge": ctx_sot_edge,

            "ctx_shot_volume_side": ctx_shot_volume_side,

            "ctx_home_conversion": n["shot_conversion_home"],
            "ctx_away_conversion": n["shot_conversion_away"],
            "ctx_conversion_edge": ctx_conversion_edge,

            "ctx_home_spg": n["shots_per_goal_home"],
            "ctx_away_spg": n["shots_per_goal_away"],
            "ctx_spg_edge": ctx_spg_edge,

            "ctx_finishing_side": ctx_finishing_side,

            "ctx_home_possession": n["possession_home"],
            "ctx_away_possession": n["possession_away"],
            "ctx_possession_edge": ctx_possession_edge,
            "ctx_possession_side": ctx_possession_side,

            # -----------------------------------------------
            # EXPLICIT VENUE DETAIL
            # -----------------------------------------------
            "explicit_venue_detail_pair": explicit_pair,

            "venue_detail_home_shots":
                home_exp.get("shots", np.nan),

            "venue_detail_away_shots":
                away_exp.get("shots", np.nan),

            "venue_detail_shots_edge":
                venue_detail_shots_edge,

            "venue_detail_home_sot":
                home_exp.get("sot", np.nan),

            "venue_detail_away_sot":
                away_exp.get("sot", np.nan),

            "venue_detail_sot_edge":
                venue_detail_sot_edge,

            "venue_shot_volume_side":
                venue_shot_volume_side,

            "venue_detail_home_conversion":
                home_exp.get("conversion", np.nan),

            "venue_detail_away_conversion":
                away_exp.get("conversion", np.nan),

            "venue_detail_conversion_edge":
                venue_detail_conversion_edge,

            "venue_detail_home_spg":
                home_exp.get("shots_per_goal", np.nan),

            "venue_detail_away_spg":
                away_exp.get("shots_per_goal", np.nan),

            "venue_detail_spg_edge":
                venue_detail_spg_edge,

            "venue_finishing_side":
                venue_finishing_side,

            "venue_detail_home_possession":
                home_exp.get("possession", np.nan),

            "venue_detail_away_possession":
                away_exp.get("possession", np.nan),

            "venue_detail_possession_edge":
                venue_detail_possession_edge,

            "venue_possession_side":
                venue_possession_side,

            # -----------------------------------------------
            # SEMANTIC SPLIT FLAGS
            # -----------------------------------------------
            "finishing_semantic_split":
                finishing_semantic_split,

            "shot_volume_semantic_split":
                shot_volume_semantic_split,

            "possession_semantic_split":
                possession_semantic_split,

            # -----------------------------------------------
            # Existing separate layers
            # -----------------------------------------------
            "matchup_xg_home":
                b["matchup_xg_home"],

            "matchup_xg_away":
                b["matchup_xg_away"],

            "matchup_xg_edge":
                b["matchup_xg_edge"],

            "matchup_xg_side":
                b["matchup_xg_side"],

            "market_p1":
                b["market_p1"],

            "market_p0":
                b["market_p0"],

            "market_p2":
                b["market_p2"],

            "market_top":
                b["market_top"],

            "market_gap":
                b["market_gap"],

            # -----------------------------------------------
            # QA
            # -----------------------------------------------
            "xg_crosscheck":
                xg_crosscheck,

            "semantic_flags":
                semantic_flags,
        })

    result = pd.DataFrame(rows)

    if len(result) != 13:
        raise SystemExit(
            f"STOP: result rows={len(result)}"
        )

    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        out_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("ROWS:", len(result))
    print("COLS:", len(result.columns))
    print("SAVED:", out_path)

    print("\n=== SEMANTIC V03 SUMMARY ===")

    show = [
        "match_no",
        "home_team",
        "away_team",
        "venue_xg_side",
        "venue_xga_def_side",
        "venue_form_side",
        "ctx_shot_volume_side",
        "ctx_finishing_side",
        "ctx_possession_side",
        "venue_shot_volume_side",
        "venue_finishing_side",
        "venue_possession_side",
        "matchup_xg_side",
        "market_top",
        "market_gap",
        "semantic_flags",
    ]

    print(
        result[show]
        .round(4)
        .to_string(index=False)
    )

    print("\n=== EXPLICIT VENUE DETAIL ===")
    print(
        result[
            [
                "match_no",
                "home_team",
                "away_team",
                "explicit_venue_detail_pair",
                "xg_crosscheck",
            ]
        ].to_string(index=False)
    )

    print("\n=== SEMANTIC SPLITS ===")

    split_cols = [
        "finishing_semantic_split",
        "shot_volume_semantic_split",
        "possession_semantic_split",
    ]

    split_mask = result[split_cols].any(axis=1)

    if split_mask.any():
        print(
            result.loc[
                split_mask,
                [
                    "match_no",
                    "home_team",
                    "away_team",
                    "ctx_shot_volume_side",
                    "venue_shot_volume_side",
                    "ctx_finishing_side",
                    "venue_finishing_side",
                    "ctx_possession_side",
                    "venue_possession_side",
                    "semantic_flags",
                ],
            ].to_string(index=False)
        )
    else:
        print("NONE")

    print("\n=== IMPORTANT NULL / QA ===")

    print(
        "venue base xG NULL:",
        int(
            result[
                [
                    "venue_home_xg",
                    "venue_away_xg",
                    "venue_home_xga",
                    "venue_away_xga",
                ]
            ].isna().sum().sum()
        ),
    )

    print(
        "form PPG NULL:",
        int(
            result[
                ["home_form_ppg", "away_form_ppg"]
            ].isna().sum().sum()
        ),
    )

    print(
        "explicit venue pair:",
        int(
            result[
                "explicit_venue_detail_pair"
            ].sum()
        ),
        "/ 13",
    )

    print(
        "xG crosscheck mismatch:",
        int(
            (
                result["xg_crosscheck"]
                == "MISMATCH"
            ).sum()
        ),
    )

    print(
        "\nNOTE:"
        " V03 separates semantic sources."
        " Threshold-based SIDE labels are diagnostic only,"
        " not validated probabilities or production weights."
    )


if __name__ == "__main__":
    main()
