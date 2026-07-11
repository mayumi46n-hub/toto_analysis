from collections import defaultdict


def build_team_histories(matches):
    histories = defaultdict(list)

    for (
        round_no,
        match_no,
        home_team,
        away_team,
        home_score,
        away_score,
    ) in matches:
        if home_score > away_score:
            home_points = 3
            away_points = 0
        elif home_score < away_score:
            home_points = 0
            away_points = 3
        else:
            home_points = 1
            away_points = 1

        histories[home_team].append({
            "round_no": round_no,
            "match_no": match_no,
            "venue": "H",
            "points": home_points,
            "goals_for": home_score,
            "goals_against": away_score,
        })

        histories[away_team].append({
            "round_no": round_no,
            "match_no": match_no,
            "venue": "A",
            "points": away_points,
            "goals_for": away_score,
            "goals_against": home_score,
        })

    return histories


def get_recent_matches(
    histories,
    team,
    before_round,
    window=5,
    venue=None,
):
    history = histories.get(team, [])

    eligible = [
        match
        for match in history
        if match["round_no"] < before_round
        and (venue is None or match["venue"] == venue)
    ]

    return eligible[-window:]


def get_form_points(
    histories,
    team,
    before_round,
    window=5,
    venue=None,
):
    recent = get_recent_matches(
        histories=histories,
        team=team,
        before_round=before_round,
        window=window,
        venue=venue,
    )

    return sum(match["points"] for match in recent)