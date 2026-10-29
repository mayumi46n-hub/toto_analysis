import argparse
import unicodedata
from pathlib import Path
import pandas as pd
from scipy.stats import skellam

def norm(s):
    return unicodedata.normalize("NFKC", str(s)).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--round", type=int, required=True)
    rnd = p.parse_args().round
    root = Path("data/analysis")
    base = pd.read_csv(root / f"toto{rnd}_goal_lambda_baseline_v01.csv")
    team = pd.read_csv(root / f"toto{rnd}_xi_fs_team_value_coverage_sensitivity_v01.csv")
    print(f"第{rnd}回: {len(base)}試合、{len(team)}チーム")
    assert len(base) == 13 and base.match_no.nunique() == 13
    assert len(team) == 26
    assert not team.duplicated(["match_no", "side"]).any()
    assert set(base.match_no) == set(team.match_no)
    assert team.groupby("match_no").side.apply(lambda s: set(s) == {"home", "away"}).all()
    assert team[["xi_attack_legacy", "xi_defensive_legacy"]].notna().all().all()
    attack_avg = team.xi_attack_legacy.mean()
    defense_avg = team.xi_defensive_legacy.mean()
    assert attack_avg > 0 and defense_avg > 0
    home = team[team.side == "home"].set_index("match_no")
    away = team[team.side == "away"].set_index("match_no")
    rows = []
    for r in base.itertuples(index=False):
        h = home.loc[r.match_no]
        a = away.loc[r.match_no]
        assert norm(r.home_team) == norm(h.team) and norm(r.away_team) == norm(a.team)
        assert r.home_lambda > 0 and r.away_lambda > 0
        hr = (h.xi_attack_legacy / attack_avg) / (a.xi_defensive_legacy / defense_avg)
        ar = (a.xi_attack_legacy / attack_avg) / (h.xi_defensive_legacy / defense_avg)
        assert hr > 0 and ar > 0
        for alpha in (0.0, 0.25, 0.5):
            hl = float(r.home_lambda * hr ** alpha)
            al = float(r.away_lambda * ar ** alpha)
            p2 = float(skellam.cdf(-1, hl, al))
            p0 = float(skellam.pmf(0, hl, al))
            p1 = 1.0 - p0 - p2
            assert min(p1, p0, p2) >= 0
            rows.append({
                "round": rnd, "match_no": r.match_no,
                "home_team": r.home_team, "away_team": r.away_team,
                "alpha": alpha, "home_lambda": hl, "away_lambda": al,
                "p1": p1, "p0": p0, "p2": p2,
                "home_identity_coverage": h.identity_coverage,
                "away_identity_coverage": a.identity_coverage,
            })
    out = pd.DataFrame(rows)
    assert len(out) == 39
    assert out.groupby("match_no").size().eq(3).all()
    path = root / f"toto{rnd}_player_1x2_legacy_v01.csv"
    out.to_csv(path, index=False)
    print("保存:", path)
    print("研究用・未較正（本番予想には未適用）")
    view = out[out.alpha == 0.5].copy()
    view["本命"] = view[["p1", "p0", "p2"]].idxmax(axis=1).str[1:]
    print(view[["match_no", "home_team", "away_team", "p1", "p0", "p2", "本命"]].round(3).to_string(index=False))

if __name__ == "__main__":
    main()
