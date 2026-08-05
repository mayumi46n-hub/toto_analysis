from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


DEFAULT_FILE = Path(
    "data/raw/footystats/csv/2025/j1/"
    "japan-j1-league-teams-2025-to-2025-stats.csv"
)


TEAM_ALIASES = {
# J1・共通
    "kyotosanga": "京都",
    "shimizuspulse": "清水",
    "mitohollyhock": "水戸",
    "jefunited": "千葉",
    "fagianookayama": "岡山",
    "cerezoosaka": "Ｃ大阪",
    "tokyoverdy": "東京Ｖ",
    "machidazelvia": "町田",
    "vvarennagasaki": "長崎",
    "avispafukuoka": "福岡",
    "nagoyagrampus": "名古屋",
    "yokohamafmarinos": "横浜FM",
    "urawareds": "浦和",
    "gambaosaka": "Ｇ大阪",
    "kashimaantlers": "鹿島",
    "sanfreccehiroshima": "広島",
    "visselkobe": "神戸",
    "tokyo": "FC東京",
    "kashiwareysol": "柏",
    "kawasakifrontale": "川崎Ｆ",
    "yokohama": "横浜FC",
    "yokohamafc": "横浜FC",
    "shonanbellmare": "湘南",
    "albirexniigata": "新潟",

    # J2
    "blaublitzakita": "秋田",
    "consadolesapporo": "札幌",
    "ehime": "愛媛",
    "fujiedamyfc": "藤枝",
    "imabari": "今治",
    "iwaki": "いわき",
    "katallertoyama": "富山",
    "montedioyamagata": "山形",
    "oitatrinita": "大分",
    "omiyaardija": "大宮",
    "renofayamaguchi": "山口",
    "roassokumamoto": "熊本",
    "sagantosu": "鳥栖",
    "tokushimavortis": "徳島",
    "vegaltasendai": "仙台",
    "ventforetkofu": "甲府",

    # J3
    "azulclaronumazu": "沼津",
    "biwakoshiga": "滋賀",
    "fukushimaunited": "福島",
    "gainaretottori": "鳥取",
    "gifu": "岐阜",
    "giravanzkitakyushu": "北九州",
    "kagoshimaunited": "鹿児島",
    "kamatamaresanuki": "讃岐",
    "kochiunited": "高知",
    "matsumotoyamaga": "松本",
    "naraclub": "奈良",
    "osaka": "FC大阪",
    "parceironagano": "長野",
    "sagamihara": "相模原",
    "tegevajaromiyazaki": "宮崎",
    "thespakusatsugunma": "群馬",
    "tochigi": "栃木SC",
    "tochigicity": "栃木Ｃ",
    "vanraurehachinohe": "八戸",
    "zweigenkanazawa": "金沢",
    "jubiloiwata": "磐田",
    "ryukyu": "琉球",
    "ryky": "琉球",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""

    text = unicodedata.normalize(
        "NFKC",
        str(value),
    ).lower()

    return re.sub(
        r"[^a-z0-9ぁ-んァ-ヶ一-龠]+",
        "",
        text,
    )

def normalize_team(value: object) -> str:
    key = normalize_text(value)
    return TEAM_ALIASES.get(
        key,
        str(value).strip(),
    )


def load_footystats(
    file_path: str | Path = DEFAULT_FILE,
) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"FootyStats CSVがありません: {path}"
        )

    df = pd.read_csv(
        path,
        low_memory=False,
    )
    df = df.copy()
    
    required = {
        "common_name",
        "matches_played",
        "points_per_game",
        "points_per_game_home",
        "points_per_game_away",
        "xg_for_avg_overall",
        "xg_for_avg_home",
        "xg_for_avg_away",
        "xg_against_avg_overall",
        "xg_against_avg_home",
        "xg_against_avg_away",
        "btts_percentage",
        "btts_percentage_home",
        "btts_percentage_away",
        "clean_sheet_percentage",
        "clean_sheet_percentage_home",
        "clean_sheet_percentage_away",
        "over25_percentage",
        "over25_percentage_home",
        "over25_percentage_away",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "FootyStats CSVに必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    numeric_columns = [
        col
        for col in required
        if col != "common_name"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    df["team_norm"] = df["common_name"].map(
        normalize_team
    )

    df["footystats_available"] = (
        df["matches_played"].fillna(0) > 0
    )

    return df


def get_team_stats(
    df: pd.DataFrame,
    team_name: str,
) -> pd.Series | None:
    normalized = normalize_team(team_name)

    target = df[
        df["team_norm"] == normalized
    ]

    if target.empty:
        return None

    return target.iloc[0]


def main() -> None:
    df = load_footystats()

    print("チーム数:", len(df))
    print(
        "利用可能チーム数:",
        int(df["footystats_available"].sum()),
    )

    cols = [
        "common_name",
        "team_norm",
        "matches_played",
        "xg_for_avg_overall",
        "xg_against_avg_overall",
        "footystats_available",
    ]

    print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
