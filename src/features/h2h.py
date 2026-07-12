from collections import defaultdict


def build_h2h_histories(matches):
    histories = defaultdict(list)

    for (
        round_no,
        match_no,
        home_team,
        away_team,
        home_score,
        away_score,
    ) in matches:
        pair_key = tuple(sorted((home_team, away_team)))

        histories[pair_key].append({
            "round_no": round_no,
            "match_no": match_no,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
        })

    return histories


def _team_points(match, team):
    if team == match["home_team"]:
        goals_for = match["home_score"]
        goals_against = match["away_score"]
    else:
        goals_for = match["away_score"]
        goals_against = match["home_score"]

    if goals_for > goals_against:
        return 3

    if goals_for == goals_against:
        return 1

    return 0


def _summarize(matches, home_team, away_team):
    home_points = sum(
        _team_points(match, home_team)
        for match in matches
    )

    away_points = sum(
        _team_points(match, away_team)
        for match in matches
    )

    return {
        "matches": len(matches),
        "home_points": home_points,
        "away_points": away_points,
        "diff": home_points - away_points,
    }


def get_h2h_features(
    histories,
    home_team,
    away_team,
    before_round,
):
    pair_key = tuple(sorted((home_team, away_team)))

    eligible = [
        match
        for match in histories.get(pair_key, [])
        if match["round_no"] < before_round
    ]

    same_venue = [
        match
        for match in eligible
        if match["home_team"] == home_team
        and match["away_team"] == away_team
    ]

    last5 = _summarize(
        eligible[-5:],
        home_team,
        away_team,
    )

    last10 = _summarize(
        eligible[-10:],
        home_team,
        away_team,
    )

    all_matches = _summarize(
        eligible,
        home_team,
        away_team,
    )

    same_venue_last5 = _summarize(
        same_venue[-5:],
        home_team,
        away_team,
    )

    return {
        "h2h_last5_matches": last5["matches"],
        "h2h_last5_home_points": last5["home_points"],
        "h2h_last5_away_points": last5["away_points"],
        "h2h_last5_diff": last5["diff"],

        "h2h_last10_matches": last10["matches"],
        "h2h_last10_home_points": last10["home_points"],
        "h2h_last10_away_points": last10["away_points"],
        "h2h_last10_diff": last10["diff"],

        "h2h_all_matches": all_matches["matches"],
        "h2h_all_home_points": all_matches["home_points"],
        "h2h_all_away_points": all_matches["away_points"],
        "h2h_all_diff": all_matches["diff"],

        "h2h_same_venue_last5_matches": (
            same_venue_last5["matches"]
        ),
        "h2h_same_venue_last5_home_points": (
            same_venue_last5["home_points"]
        ),
        "h2h_same_venue_last5_away_points": (
            same_venue_last5["away_points"]
        ),
        "h2h_same_venue_last5_diff": (
            same_venue_last5["diff"]
        ),
    }