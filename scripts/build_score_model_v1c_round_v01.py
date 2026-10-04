#!/usr/bin/env python3

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson
from sklearn.impute import SimpleImputer
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "jl_home_season_matches",
    "jl_home_season_ppg",
    "jl_home_season_gf_per_match",
    "jl_home_season_ga_per_match",
    "jl_away_season_matches",
    "jl_away_season_ppg",
    "jl_away_season_gf_per_match",
    "jl_away_season_ga_per_match",
    "jl_home_season_venue_matches",
    "jl_home_season_venue_ppg",
    "jl_home_season_venue_gf_per_match",
    "jl_home_season_venue_ga_per_match",
    "jl_away_season_venue_matches",
    "jl_away_season_venue_ppg",
    "jl_away_season_venue_gf_per_match",
    "jl_away_season_venue_ga_per_match",
    "jl_home_recent5_matches",
    "jl_home_recent5_ppg",
    "jl_home_recent5_gf_per_match",
    "jl_home_recent5_ga_per_match",
    "jl_away_recent5_matches",
    "jl_away_recent5_ppg",
    "jl_away_recent5_gf_per_match",
    "jl_away_recent5_ga_per_match",
    "jl_home_rest_days",
    "jl_away_rest_days",
    "jl_home_matches_last7_days",
    "jl_away_matches_last7_days",
    "jl_home_matches_last14_days",
    "jl_away_matches_last14_days",
    "fs_csv_home_team_pre_match_xg",
    "fs_csv_away_team_pre_match_xg",
]

META_HOME_INTERCEPT = 0.02114971325203815
META_HOME_COEF = np.array([
    0.35383403609678693,
    0.4561876384370998,
   -0.11076783232877811,
])

META_AWAY_INTERCEPT = 0.06613697596141004
META_AWAY_COEF = np.array([
    0.47879950558174084,
   -0.17400639879996502,
    0.3386047860389035,
])


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--training",
                   default="data/features/score_training_v1b.csv")
    p.add_argument("--jleague", required=True)
    p.add_argument("--footystats",
                   default="data/features/"
                           "footystats_csv_prediction_features_2026_redownload_v2.csv")
    p.add_argument("--multisource", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args()


def main():
    a = parse_args()

    train = pd.read_csv(a.training)
    jl = pd.read_csv(a.jleague)
    fs = pd.read_csv(a.footystats)
    ms = pd.read_csv(a.multisource)

    ids = ms["jleague_match_id"].astype(int).tolist()
    if len(ids) != 13 or len(set(ids)) != 13:
        raise ValueError("multisource target must contain 13 unique IDs")

    jl_target = (
        jl[jl["jleague_match_id"].astype(int).isin(ids)]
        .drop_duplicates("jleague_match_id")
        .copy()
    )

    if len(jl_target) != 13:
        raise ValueError(f"J.League target rows={len(jl_target)}")

    fs_keep = [
        "jleague_match_id",
        "fs_csv_home_team_pre_match_xg",
        "fs_csv_away_team_pre_match_xg",
    ]
    fs_target = (
        fs[fs["jleague_match_id"].astype(int).isin(ids)][fs_keep]
        .drop_duplicates("jleague_match_id")
    )

    if len(fs_target) != 13:
        raise ValueError(f"FootyStats target rows={len(fs_target)}")

    target = (
        ms.merge(
            jl_target,
            on="jleague_match_id",
            how="left",
            suffixes=("", "_jl"),
        )
        .merge(
            fs_target,
            on="jleague_match_id",
            how="left",
            suffixes=("", "_fs"),
        )
    )

    # Ensure the explicit FootyStats redownload values are the Stage1 inputs.
    for c in [
        "fs_csv_home_team_pre_match_xg",
        "fs_csv_away_team_pre_match_xg",
    ]:
        alt = c + "_fs"
        if alt in target.columns:
            target[c] = target[alt]

    if target[FEATURES].isna().any().any():
        missing = target[FEATURES].isna().sum()
        bad = missing[missing > 0]
        raise ValueError(f"target feature missing:\n{bad}")

    x_train = train[FEATURES].copy()
    x_target = target[FEATURES].copy()

    for c in ["jl_home_rest_days", "jl_away_rest_days"]:
        x_train[c] = x_train[c].clip(upper=30)
        x_target[c] = x_target[c].clip(upper=30)

    home_model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PoissonRegressor(
            alpha=0.20,
            tol=1e-8,
            max_iter=5000,
        ),
    )
    away_model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PoissonRegressor(
            alpha=0.20,
            tol=1e-8,
            max_iter=5000,
        ),
    )

    home_model.fit(x_train, train["home_score"])
    away_model.fit(x_train, train["away_score"])

    lambda_home_base = home_model.predict(x_target)
    lambda_away_base = away_model.predict(x_target)

    ms_home = target["prob_home_win"].to_numpy()
    ms_draw = target["prob_draw"].to_numpy()
    ms_away = target["prob_away_win"].to_numpy()

    xh = np.log(ms_home / ms_draw)
    xa = np.log(ms_away / ms_draw)

    lambda_home_final = np.exp(
        META_HOME_INTERCEPT
        + META_HOME_COEF[0] * np.log(lambda_home_base)
        + META_HOME_COEF[1] * xh
        + META_HOME_COEF[2] * xa
    )

    lambda_away_final = np.exp(
        META_AWAY_INTERCEPT
        + META_AWAY_COEF[0] * np.log(lambda_away_base)
        + META_AWAY_COEF[1] * xh
        + META_AWAY_COEF[2] * xa
    )

    rows = []

    for i, r in target.reset_index(drop=True).iterrows():
        lh = lambda_home_final[i]
        la = lambda_away_final[i]

        g = np.arange(9)
        matrix = np.outer(
            poisson.pmf(g, lh),
            poisson.pmf(g, la),
        )
        matrix /= matrix.sum()

        p_home = np.tril(matrix, -1).sum()
        p_draw = np.trace(matrix)
        p_away = np.triu(matrix, 1).sum()

        ranked = sorted(
            [
                (matrix[h, aw], h, aw)
                for h in range(9)
                for aw in range(9)
            ],
            key=lambda z: (-z[0], z[1], z[2]),
        )[:10]

        rec = {
            "toto_no": i + 1,
            "jleague_match_id": int(r["jleague_match_id"]),
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "fs_home_xg": r["fs_csv_home_team_pre_match_xg"],
            "fs_away_xg": r["fs_csv_away_team_pre_match_xg"],
            "ms_p_home": ms_home[i],
            "ms_p_draw": ms_draw[i],
            "ms_p_away": ms_away[i],
            "lambda_home_base": lambda_home_base[i],
            "lambda_away_base": lambda_away_base[i],
            "lambda_home_final": lh,
            "lambda_away_final": la,
            "lambda_total_final": lh + la,
            "score_p_home": p_home,
            "score_p_draw": p_draw,
            "score_p_away": p_away,
            "top_score": f"{ranked[0][1]}-{ranked[0][2]}",
            "top_score_prob": ranked[0][0],
        }

        for k, (prob, h, aw) in enumerate(ranked, 1):
            rec[f"score_rank{k}"] = f"{h}-{aw}"
            rec[f"score_rank{k}_prob"] = prob

        rows.append(rec)

    out = pd.DataFrame(rows)

    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output, index=False)

    print("ROUND", a.round)
    print("ROWS", len(out))
    print("FS_XG_NONZERO",
          int((out.fs_home_xg != 0).sum()),
          int((out.fs_away_xg != 0).sum()))
    print("PROB_SUM_MAXERR",
          float(
              (
                  out[["score_p_home","score_p_draw","score_p_away"]]
                  .sum(axis=1) - 1
              ).abs().max()
          ))

    print("\n=== P_BASE ===")
    print(
        out[[
            "toto_no","home_team","away_team",
            "score_p_home","score_p_draw","score_p_away",
            "lambda_home_final","lambda_away_final",
            "top_score"
        ]].round(4).to_string(index=False)
    )

    print(f"\nOUTPUT {a.output}")
    print("STEP 23k SCORE MODEL V1C BUILD: PASS")


if __name__ == "__main__":
    main()
