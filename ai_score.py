from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIScoreResult:
    total: int
    stars: str
    recommendation: str
    breakdown: dict[str, int]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def calculate_ai_score(
    *,
    market_value: float,
    form_diff: float,
    goal_diff: float,
    shot_diff: float,
    h2h_edge: float,
    similar_edge: float,
    footy_ppg_diff: float | None = None,
    footy_xg_diff: float | None = None,
    footy_xga_edge: float | None = None,
) -> AIScoreResult:
    """
    本命候補の信頼度を100点満点で評価するルールベースv1。

    各引数は、本命側が優勢なら正の値にする。
    """

    market_score = round(
        clamp((market_value + 10.0) / 20.0 * 20.0, 0.0, 20.0)
    )

    form_score = round(
        clamp((form_diff + 1.0) / 2.0 * 20.0, 0.0, 20.0)
    )

    goal_score = round(
        clamp((goal_diff + 1.0) / 2.0 * 10.0, 0.0, 10.0)
    )

    shot_score = round(
        clamp((shot_diff + 4.0) / 8.0 * 10.0, 0.0, 10.0)
    )

    h2h_score = round(
        clamp((h2h_edge + 1.0) / 2.0 * 10.0, 0.0, 10.0)
    )

    similar_score = round(
        clamp((similar_edge + 15.0) / 30.0 * 10.0, 0.0, 10.0)
    )

    footy_components = []

    if footy_ppg_diff is not None:
        footy_components.append(
            clamp((footy_ppg_diff + 1.0) / 2.0, 0.0, 1.0)
        )

    if footy_xg_diff is not None:
        footy_components.append(
            clamp((footy_xg_diff + 1.0) / 2.0, 0.0, 1.0)
        )

    if footy_xga_edge is not None:
        footy_components.append(
            clamp((footy_xga_edge + 1.0) / 2.0, 0.0, 1.0)
        )

    if footy_components:
        footy_score = round(
            sum(footy_components)
            / len(footy_components)
            * 20.0
        )
    else:
        footy_score = 10

    breakdown = {
        "市場差": market_score,
        "フォーム": form_score,
        "得失点差": goal_score,
        "SH差": shot_score,
        "直接対戦": h2h_score,
        "類似投票率": similar_score,
        "FootyStats": footy_score,
    }

    total = sum(breakdown.values())

    if total >= 90:
        stars = "★★★★★"
        recommendation = "シングル"
    elif total >= 80:
        stars = "★★★★☆"
        recommendation = "シングル候補"
    elif total >= 65:
        stars = "★★★☆☆"
        recommendation = "ダブル"
    else:
        stars = "★★☆☆☆"
        recommendation = "トリプル候補"

    return AIScoreResult(
        total=total,
        stars=stars,
        recommendation=recommendation,
        breakdown=breakdown,
    )
