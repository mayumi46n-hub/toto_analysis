#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import re
import unicodedata
import numpy as np
import pandas as pd

# ============================================================
# INPUTS
# ============================================================
XI_FILES = sorted(
    Path("data/players").glob(
        "fomelabo_toto1656_*_predicted_lineups_*_v1.csv"
    )
)

MATCHED = Path(
    "data/analysis/"
    "toto1656_fomelabo_xi_player_strength_join_v01.csv"
)

JL_FULL = Path(
    "data/jleague/2026_27/"
    "j123_players_stats_v1.csv"
)

FS_STRENGTH = Path(
    "data/players/"
    "footystats_2026_player_strength_full_v02.csv"
)

FETCHER = Path(
    "scripts/fetch_fomelabo_lineups_v1.py"
)

if len(XI_FILES) != 3:
    raise RuntimeError(
        f"expected 3 Fomelabo XI files, got {len(XI_FILES)}"
    )

# ============================================================
# HELPERS
# ============================================================
def norm_jp(x):
    if pd.isna(x):
        return ""
    s = unicodedata.normalize("NFKC", str(x)).lower()
    return re.sub(r"[^0-9a-zぁ-んァ-ヶ一-龯]", "", s)

def norm_en(x):
    if pd.isna(x):
        return ""
    s = unicodedata.normalize("NFKD", str(x))
    s = "".join(
        c for c in s
        if not unicodedata.combining(c)
    )
    s = s.lower()
    return re.sub(r"[^0-9a-z]", "", s)

def posgrp(x):
    if pd.isna(x):
        return None

    s = unicodedata.normalize(
        "NFKC", str(x)
    ).upper().strip()

    if (
        "GK" in s
        or "GOALKEEPER" in s
        or "KEEPER" in s
    ):
        return "GK"

    if (
        s == "DF"
        or "DEFENDER" in s
        or "CENTRE BACK" in s
        or "CENTER BACK" in s
        or s in {"CB","LB","RB"}
    ):
        return "DF"

    if (
        "FW" in s
        or "FORWARD" in s
        or "STRIKER" in s
        or s in {"CF","LW","RW"}
    ):
        return "FW"

    if (
        "MF" in s
        or "MIDFIELDER" in s
        or "MIDFIELD" in s
        or s in {
            "DM","CM","AM","LM","RM",
            "DMF","CMF","AMF"
        }
    ):
        return "MF"

    return None

TEAM_MAP = {
    "山形":"山形",
    "鳥栖":"鳥栖",
    "富山":"富山",
    "横浜FC":"横浜FC",
    "徳島":"徳島",
    "栃木C":"栃木C",
    "大宮":"大宮",
    "甲府":"甲府",
    "宮崎":"宮崎",
    "札幌":"札幌",
    "秋田":"秋田",
    "新潟":"新潟",
    "いわき":"いわき",
    "仙台":"仙台",
    "磐田":"磐田",
    "八戸":"八戸",
    "今治":"今治",
    "湘南":"湘南",
    "大分":"大分",
    "藤枝":"藤枝",
    "群馬":"群馬",
    "熊本":"熊本",
    "福島":"福島",
    "長野":"長野",
    "栃木":"栃木SC",
    "松本":"松本",
}

TARGET = set(TEAM_MAP)

# ============================================================
# 1. CANONICAL 286 XI
# ============================================================
xi = pd.concat(
    [pd.read_csv(p) for p in XI_FILES],
    ignore_index=True
)

xi = xi[
    xi["short_name"].astype(str).isin(TARGET)
].copy()

xi["toto_team"] = xi["short_name"].map(TEAM_MAP)

KEY = [
    "toto_team",
    "player_id",
    "lineup_order",
]

if len(xi) != 286:
    raise RuntimeError(
        f"XI expected 286 rows, got {len(xi)}"
    )

if xi[KEY].drop_duplicates().shape[0] != 286:
    raise RuntimeError("XI key duplicate")

# ============================================================
# 2. EXISTING SAFE 275
# ============================================================
matched = pd.read_csv(MATCHED)

strength_cols = [
    "jleague_player_id",
    "jleague_player_name",
    "jleague_uniform_no",
    "jleague_position",
    "fs_full_name",
    "fs_position",
    "fs_club",
    "fs_minutes",
    "fs_reliability",
    "fs_attack_power",
    "fs_finishing_power",
    "fs_build_up_power",
    "fs_width_carry_power",
    "fs_defensive_power",
    "fs_keeper_power",
    "crosswalk_method",
    "crosswalk_confidence",
    "match_method",
]

take = KEY + [
    c for c in strength_cols
    if c in matched.columns
]

safe = (
    matched[take]
    .drop_duplicates(KEY)
    .copy()
)

d = xi.merge(
    safe,
    on=KEY,
    how="left"
)

d["xi_identity_method"] = np.where(
    d["jleague_player_id"].notna(),
    "EXISTING_SHIRT_POSITION_JPNAME_EXACT",
    "UNRESOLVED"
)

d["xi_fs_strength_method"] = np.where(
    d["fs_attack_power"].notna(),
    "EXISTING_PLAYER_MASTER_V03",
    "UNRESOLVED"
)

# ============================================================
# 3. GET FOMELABO 8042 PLAYER MASTER
# ============================================================
spec = importlib.util.spec_from_file_location(
    "fomelabo_fetcher",
    FETCHER
)

fm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fm)

chunk_url, js = fm.find_data_chunk("j2")

if (
    '"league":"J2"' not in js
    or '"players":[' not in js
    or "playerIds:[" not in js
):
    raise RuntimeError(
        "selected Fomelabo chunk is not the player-data chunk"
    )

print("FOMELABO_CHUNK =", chunk_url)
print("FOMELABO_CHUNK_BYTES =", len(js))

# Flat Fomelabo player objects.
pat = re.compile(
    r'\{"id":"([^"]+)",'
    r'"name":"((?:\\.|[^"])*)",'
    r'"_en":"((?:\\.|[^"])*)",'
    r'"team":"([^"]+)",'
    r'"position":"([^"]+)"'
    r'([^{}]*?)\}'
)

meta = {}

for m in pat.finditer(js):

    pid = m.group(1)
    tail = m.group(6)

    number_m = re.search(
        r'"number":([0-9]+)',
        tail
    )

    birthday_m = re.search(
        r'"birthday":"([^"]*)"',
        tail
    )

    meta[pid] = {
        "fm_player_name": fm.js_string_decode(
            m.group(2)
        ),
        "fm_english_name": fm.js_string_decode(
            m.group(3)
        ),
        "fm_team_slug": m.group(4),
        "fm_position": m.group(5),
        "fm_number": (
            int(number_m.group(1))
            if number_m
            else pd.NA
        ),
        "fm_birthday": (
            birthday_m.group(1)
            if birthday_m
            else ""
        ),
    }

print("FOMELABO_PLAYER_MASTER_ROWS =", len(meta))

fmmeta = (
    pd.DataFrame.from_dict(
        meta,
        orient="index"
    )
    .rename_axis("player_id")
    .reset_index()
)

d = d.merge(
    fmmeta,
    on="player_id",
    how="left"
)

print(
    "FOMELABO_METADATA_COVERAGE =",
    int(d["fm_english_name"].notna().sum()),
    "/",
    len(d)
)

# Guard against website changing between XI snapshot and rescue.
name_consistent = (
    d["fm_player_name"]
    .fillna("")
    .map(norm_jp)
    ==
    d["player_name"]
    .fillna("")
    .map(norm_jp)
)

if not name_consistent.all():
    bad = d.loc[
        ~name_consistent,
        [
            "toto_team",
            "player_id",
            "player_name",
            "fm_player_name",
        ]
    ]

    print(bad.to_string(index=False))

    raise RuntimeError(
        "Fomelabo live metadata differs from saved XI snapshot"
    )

# ============================================================
# 4. JLEAGUE GLOBAL IDENTITY
# ============================================================
jl = pd.read_csv(
    JL_FULL,
    low_memory=False
).copy()

jl["_jp_norm"] = (
    jl["player_name"].map(norm_jp)
)

# ============================================================
# 5. FOOTYSTATS FULL STRENGTH IDENTITY
# ============================================================
fs = pd.read_csv(
    FS_STRENGTH,
    low_memory=False
).copy()

fs["_en_norm"] = fs["full_name"].map(norm_en)
fs["_posgrp"] = fs["position"].map(posgrp)

fs["_birth_dt"] = pd.to_datetime(
    pd.to_numeric(
        fs["birthday"],
        errors="coerce"
    ),
    unit="s",
    utc=True,
    errors="coerce"
)

# ============================================================
# 6. RESCUE ONLY CURRENT 11
# ============================================================
unresolved_idx = d.index[
    d["jleague_player_id"].isna()
].tolist()

print()
print("=== STRICT XI RESCUE ===")
print("START_UNRESOLVED =", len(unresolved_idx))

audit = []

for idx in unresolved_idx:

    r = d.loc[idx]

    team = r["toto_team"]
    jpname = r["player_name"]
    enname = r["fm_english_name"]
    fmpos = r["fm_position"]
    birthday = r["fm_birthday"]

    print()
    print("=" * 88)
    print(
        f"{team} | {jpname} | "
        f"{enname} | "
        f"birthday={birthday}"
    )

    # --------------------------------------------
    # JLeague ID:
    # exact Japanese name, collapse historical rows by ID
    # --------------------------------------------
    jc = jl[
        jl["_jp_norm"].eq(
            norm_jp(jpname)
        )
    ].copy()

    unique_ids = (
        pd.to_numeric(
            jc["jleague_player_id"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    jl_status = "UNRESOLVED"

    if len(unique_ids) == 1:

        jid = int(unique_ids[0])

        jr = (
            jc[
                pd.to_numeric(
                    jc["jleague_player_id"],
                    errors="coerce"
                ).eq(jid)
            ]
            .iloc[-1]
        )

        d.loc[idx, "jleague_player_id"] = jid
        d.loc[idx, "jleague_player_name"] = jpname
        d.loc[idx, "jleague_uniform_no"] = r["fm_number"]
        d.loc[idx, "jleague_position"] = r["fm_position"]

        jl_status = "FOMELABO_JPNAME_GLOBAL_UNIQUE_JL_ID"

        d.loc[idx, "xi_identity_method"] = jl_status

    # --------------------------------------------
    # FootyStats:
    # English exact + position + birthday ±1 day
    # --------------------------------------------
    fm_birth = pd.to_datetime(
        birthday,
        utc=True,
        errors="coerce"
    )

    fc = fs[
        fs["_en_norm"].eq(
            norm_en(enname)
        )
        & fs["_posgrp"].eq(
            posgrp(fmpos)
        )
    ].copy()

    if pd.notna(fm_birth):
        fc["_birth_delta_days"] = (
            (
                fc["_birth_dt"].dt.normalize()
                - fm_birth.normalize()
            )
            .abs()
            .dt.days
        )

        strict = fc[
            fc["_birth_delta_days"] <= 1
        ].copy()
    else:
        strict = fc.iloc[0:0].copy()

    print(
        "JL_UNIQUE_IDS =",
        list(unique_ids)
    )

    print(
        "FS_EN_POS_CANDIDATES =",
        len(fc)
    )

    print(
        "FS_STRICT_BIRTH_CANDIDATES =",
        len(strict)
    )

    rescue_status = "FS_UNRESOLVED"

    if len(strict) == 1:

        z = strict.iloc[0]

        value_map = {
            "fs_full_name":
                "full_name",
            "fs_position":
                "position",
            "fs_club":
                "Current Club",
            "fs_minutes":
                "minutes_played_overall",
            "fs_reliability":
                "fs_reliability",
            "fs_attack_power":
                "fs_attack_power",
            "fs_finishing_power":
                "fs_finishing_power",
            "fs_build_up_power":
                "fs_build_up_power",
            "fs_width_carry_power":
                "fs_width_carry_power",
            "fs_defensive_power":
                "fs_defensive_power",
            "fs_keeper_power":
                "fs_keeper_power",
        }

        for dst, src in value_map.items():
            if dst not in d.columns:
                d[dst] = pd.NA

            d.loc[idx, dst] = z[src]

        d.loc[
            idx,
            "crosswalk_method"
        ] = (
            "FOMELABO_EN_BIRTHDAY_POSITION_EXACT"
        )

        d.loc[
            idx,
            "crosswalk_confidence"
        ] = "HIGH"

        d.loc[
            idx,
            "xi_fs_strength_method"
        ] = (
            "FOMELABO_EN_BIRTHDAY_POSITION_EXACT"
        )

        rescue_status = "STRICT_RESCUED"

        print(
            "RESCUED_FS =",
            z["Current Club"],
            "|",
            z["full_name"],
            "|",
            z["position"],
            "|",
            z["birthday"],
        )

    else:

        if len(fc):
            show = [
                c for c in [
                    "Current Club",
                    "full_name",
                    "position",
                    "birthday",
                    "minutes_played_overall",
                    "_birth_delta_days",
                ]
                if c in fc.columns
            ]

            print(
                fc[show]
                .to_string(index=False)
            )

    audit.append({
        "toto_team": team,
        "player_id": r["player_id"],
        "player_name": jpname,
        "fm_english_name": enname,
        "fm_birthday": birthday,
        "jl_unique_id_count": len(unique_ids),
        "jl_status": jl_status,
        "fs_en_pos_candidates": len(fc),
        "fs_strict_candidates": len(strict),
        "fs_rescue_status": rescue_status,
    })

# ============================================================
# 7. FINAL STATUS
# ============================================================
d["production_player_coefficient"] = 0.0

d["xi_strength_available"] = (
    d["fs_attack_power"].notna()
    & d["fs_finishing_power"].notna()
    & d["fs_build_up_power"].notna()
    & d["fs_width_carry_power"].notna()
    & d["fs_defensive_power"].notna()
)

print()
print("=== FINAL XI CANONICAL QA ===")

print("ROWS =", len(d))

print(
    "UNIQUE_XI_KEYS =",
    d[KEY].drop_duplicates().shape[0]
)

print(
    "JL_ID_COVERAGE =",
    int(d["jleague_player_id"].notna().sum()),
    "/ 286"
)

print(
    "FS_STRENGTH_COVERAGE =",
    int(d["xi_strength_available"].sum()),
    "/ 286"
)

print(
    "FS_STRENGTH_MISSING =",
    int((~d["xi_strength_available"]).sum())
)

print()
print("=== MISSING FS STRENGTH ===")

miss = d[
    ~d["xi_strength_available"]
].copy()

if len(miss):
    print(
        miss[
            [
                "toto_team",
                "player_id",
                "player_name",
                "fm_english_name",
                "fm_birthday",
                "registered_position",
            ]
        ].to_string(index=False)
    )
else:
    print("NONE")

print()
print("=== TEAM STRENGTH COVERAGE ===")

cov = (
    d.groupby("toto_team")
    .agg(
        starters=("player_id", "size"),
        strength_n=(
            "xi_strength_available",
            "sum"
        ),
    )
    .reset_index()
)

missing_names = (
    d[
        ~d["xi_strength_available"]
    ]
    .groupby("toto_team")["player_name"]
    .apply(
        lambda s: " / ".join(
            s.astype(str)
        )
    )
)

cov["missing_players"] = (
    cov["toto_team"]
    .map(missing_names)
    .fillna("")
)

print(
    cov.sort_values("toto_team")
    .to_string(index=False)
)

# ============================================================
# 8. SAVE
# ============================================================
OUT = Path(
    "data/analysis/"
    "toto1656_fomelabo_xi_canonical_v01.csv"
)

AUDIT = Path(
    "data/analysis/"
    "toto1656_fomelabo_xi_rescue_audit_v01.csv"
)

COV = Path(
    "data/analysis/"
    "toto1656_fomelabo_xi_strength_coverage_v01.csv"
)

d.to_csv(
    OUT,
    index=False
)

pd.DataFrame(audit).to_csv(
    AUDIT,
    index=False
)

cov.to_csv(
    COV,
    index=False
)

print()
print("OUTPUT_CANONICAL =", OUT)
print("OUTPUT_RESCUE_AUDIT =", AUDIT)
print("OUTPUT_COVERAGE =", COV)
print("PRODUCTION_PLAYER_COEFFICIENT = 0")

print(
    "TOTO1656_XI_CANONICAL_RESCUE_QA=PASS"
)
