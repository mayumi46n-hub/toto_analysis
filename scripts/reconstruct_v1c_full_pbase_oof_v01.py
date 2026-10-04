#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import poisson

V1C = Path(
    "data/evaluation/"
    "score_model_v1c_stacked_oof_predictions_2023_2025.csv"
)

REF = Path(
    "data/evaluation/"
    "oof_pbase_composite_stack_walkforward_v01.csv"
)

OUT = Path(
    "data/evaluation/"
    "score_model_v1c_pbase_reconstructed_oof_2023_2025_v01.csv"
)

SUMMARY = Path(
    "data/evaluation/"
    "score_model_v1c_pbase_reconstructed_oof_summary_v01.csv"
)

d = pd.read_csv(V1C, low_memory=False)
r = pd.read_csv(REF, low_memory=False)

print("=== V1C FULL P_BASE RECONSTRUCTION ===")
print("V1C_ROWS =", len(d))
print("REF_ROWS =", len(r))

required = [
    "jleague_match_id",
    "match_date",
    "lambda_home_final",
    "lambda_away_final",
]

missing = [c for c in required if c not in d.columns]
if missing:
    raise RuntimeError(f"missing V1C columns: {missing}")

if d["jleague_match_id"].duplicated().any():
    raise RuntimeError("duplicate jleague_match_id")

lh = pd.to_numeric(
    d["lambda_home_final"],
    errors="coerce"
).to_numpy(dtype=float)

la = pd.to_numeric(
    d["lambda_away_final"],
    errors="coerce"
).to_numpy(dtype=float)

if not np.isfinite(lh).all():
    raise RuntimeError("non-finite lambda_home_final")

if not np.isfinite(la).all():
    raise RuntimeError("non-finite lambda_away_final")

if (lh < 0).any() or (la < 0).any():
    raise RuntimeError("negative lambda detected")

# ------------------------------------------------------------
# Exact validated P_base construction:
# Poisson goals 0..12, aggregate HOME/DRAW/AWAY, renormalize.
# ------------------------------------------------------------
goals = np.arange(13)

p1 = np.empty(len(d), dtype=float)
p0 = np.empty(len(d), dtype=float)
p2 = np.empty(len(d), dtype=float)

for i, (hmu, amu) in enumerate(zip(lh, la)):

    hp = poisson.pmf(goals, hmu)
    ap = poisson.pmf(goals, amu)

    mat = np.outer(hp, ap)

    raw_home = np.tril(mat, -1).sum()
    raw_draw = np.trace(mat)
    raw_away = np.triu(mat, 1).sum()

    s = raw_home + raw_draw + raw_away

    if not np.isfinite(s) or s <= 0:
        raise RuntimeError(
            f"invalid probability sum at row {i}"
        )

    p1[i] = raw_home / s
    p0[i] = raw_draw / s
    p2[i] = raw_away / s

out = d.copy()

out["pbase_p1"] = p1
out["pbase_p0"] = p0
out["pbase_p2"] = p2

out["PBASE_CONSTRUCTION"] = (
    "POISSON_GRID_0_12_RENORMALIZED"
)

out["PBASE_SOURCE_LAMBDA"] = (
    "lambda_home_final|lambda_away_final"
)

out["PBASE_PRODUCTION_MUTATED"] = 0

# ------------------------------------------------------------
# Probability QA
# ------------------------------------------------------------
psum = (
    out["pbase_p1"]
    + out["pbase_p0"]
    + out["pbase_p2"]
)

print(
    "MAX_SUM1_ERROR =",
    float(
        (psum - 1.0)
        .abs()
        .max()
    )
)

if (psum - 1.0).abs().max() > 1e-12:
    raise RuntimeError("probability sum QA failed")

# ------------------------------------------------------------
# Exact identity against historical 1874 reference
# ------------------------------------------------------------
ref_required = [
    "jleague_match_id",
    "pbase_p1",
    "pbase_p0",
    "pbase_p2",
]

for c in ref_required:
    if c not in r.columns:
        raise RuntimeError(f"REF missing {c}")

m = r[ref_required].merge(
    out[
        [
            "jleague_match_id",
            "pbase_p1",
            "pbase_p0",
            "pbase_p2",
        ]
    ],
    on="jleague_match_id",
    how="inner",
    suffixes=("_ref", "_reconstructed"),
    validate="one_to_one",
)

print(
    "REF_ID_INTERSECTION =",
    len(m)
)

if len(m) != len(r):
    raise RuntimeError(
        "reference is not fully contained in reconstructed V1C"
    )

diff = np.column_stack([
    (
        m["pbase_p1_ref"]
        - m["pbase_p1_reconstructed"]
    ).abs(),

    (
        m["pbase_p0_ref"]
        - m["pbase_p0_reconstructed"]
    ).abs(),

    (
        m["pbase_p2_ref"]
        - m["pbase_p2_reconstructed"]
    ).abs(),
])

max_diff = float(
    np.max(diff)
)

exact_rows = int(
    (
        np.max(diff, axis=1)
        < 1e-12
    ).sum()
)

print(
    "REF_MAX_ABS_DIFF =",
    max_diff
)

print(
    "REF_EXACT_ROWS_1E12 =",
    exact_rows
)

if (
    max_diff >= 1e-12
    or exact_rows != len(r)
):
    raise RuntimeError(
        "P_base exact identity failed"
    )

# ------------------------------------------------------------
# Baseline metrics
# actual_result convention already established:
# 1=HOME, 0=DRAW, 2=AWAY
# ------------------------------------------------------------
summary_rows = []

if "actual_result" in out.columns:

    y = pd.to_numeric(
        out["actual_result"],
        errors="coerce"
    )

    out["actual_pbase_prob"] = np.select(
        [
            y.eq(1),
            y.eq(0),
            y.eq(2),
        ],
        [
            out["pbase_p1"],
            out["pbase_p0"],
            out["pbase_p2"],
        ],
        default=np.nan,
    )

    actual = np.column_stack([
        y.eq(1).astype(float),
        y.eq(0).astype(float),
        y.eq(2).astype(float),
    ])

    probs = out[
        [
            "pbase_p1",
            "pbase_p0",
            "pbase_p2",
        ]
    ].to_numpy(dtype=float)

    out["pbase_brier_row"] = np.sum(
        (probs - actual) ** 2,
        axis=1
    )

    years = pd.to_datetime(
        out["match_date"],
        errors="coerce",
        utc=True
    ).dt.year

    scopes = [
        ("ALL_2023_2025", out.index)
    ]

    for year in [2023, 2024, 2025]:
        scopes.append(
            (
                str(year),
                out.index[
                    years.eq(year)
                ],
            )
        )

    for label, idx in scopes:

        z = out.loc[idx].copy()

        valid = (
            z["actual_pbase_prob"]
            .notna()
        )

        zz = z.loc[valid]

        ll = float(
            -np.log(
                np.clip(
                    zz["actual_pbase_prob"]
                    .to_numpy(dtype=float),
                    1e-15,
                    1.0,
                )
            ).mean()
        )

        brier = float(
            zz["pbase_brier_row"]
            .mean()
        )

        summary_rows.append({
            "scope": label,
            "n": len(zz),
            "pbase_logloss": ll,
            "pbase_brier": brier,
        })

summary = pd.DataFrame(
    summary_rows
)

out.to_csv(
    OUT,
    index=False
)

summary.to_csv(
    SUMMARY,
    index=False
)

print()
print(
    "=== RECONSTRUCTED P_BASE BASELINE ==="
)

if len(summary):
    print(
        summary
        .round(9)
        .to_string(index=False)
    )

print()
print("OUTPUT =", OUT)
print("SUMMARY =", SUMMARY)

print(
    "PBASE_CONSTRUCTION = POISSON_GRID_0_12_RENORMALIZED"
)

print(
    "PBASE_FULL_ROWS =",
    len(out)
)

print(
    "PRODUCTION_PBASE_MUTATED = False"
)

print(
    "V1C_FULL_PBASE_RECONSTRUCTION_V01_QA=PASS"
)
