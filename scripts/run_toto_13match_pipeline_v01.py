import argparse
import subprocess
import sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    args = ap.parse_args()
    rnd = args.round
    root = Path("data/analysis")
    baseline = root / f"toto{rnd}_goal_lambda_baseline_v01.csv"
    team = root / f"toto{rnd}_xi_fs_team_value_coverage_sensitivity_v01.csv"
    missing = [str(p) for p in (baseline, team) if not p.exists()]
    if missing:
        print(f"第{rnd}回：入力CSVが不足しています")
        for path in missing:
            print("不足:", path)
        sys.exit(1)
    print(f"第{rnd}回：入力CSV確認OK")
    subprocess.run([
        sys.executable,
        "scripts/run_toto_player_1x2_v01.py",
        "--round", str(rnd),
    ], check=True)

if __name__ == "__main__":
    main()
