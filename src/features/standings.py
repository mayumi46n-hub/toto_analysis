def load_standings(con, season):
    rows = con.execute("""
        SELECT
            round_no,
            league,
            team,
            rank,
            points,
            goal_diff
        FROM round_standings
        WHERE season = ?
          AND league IN ('J1', 'J2')
    """, (season,)).fetchall()

    return {
        (round_no, league, team): {
            "rank": rank,
            "points": points,
            "goal_diff": goal_diff,
        }
        for (
            round_no,
            league,
            team,
            rank,
            points,
            goal_diff,
        ) in rows
    }


def get_standing_features(
    standings,
    pre_round,
    home_team,
    away_team,
):
    for league in ("J1", "J2"):
        home = standings.get(
            (pre_round, league, home_team)
        )
        away = standings.get(
            (pre_round, league, away_team)
        )

        if home is None or away is None:
            continue

        return {
            "league": league,
            "home_rank": home["rank"],
            "away_rank": away["rank"],
            "rank_diff": away["rank"] - home["rank"],

            "home_points": home["points"],
            "away_points": away["points"],
            "points_diff": home["points"] - away["points"],

            "home_goal_diff": home["goal_diff"],
            "away_goal_diff": away["goal_diff"],
            "goal_diff_diff": (
                home["goal_diff"] - away["goal_diff"]
            ),
        }

    return None