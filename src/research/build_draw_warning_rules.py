from itertools import combinations
from pathlib import Path

import pandas as pd

INPUT_PATH = Path(
    "data/training_data_v3.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


RULES = {
    "Elo<=30":
        lambda d: d["elo_diff"].abs() <= 30,

    "Elo<=50":
        lambda d: d["elo_diff"].abs() <= 50,

    "Points<=3":
        lambda d: d["points_diff"].abs() <= 3,

    "Points<=5":
        lambda d: d["points_diff"].abs() <= 5,

    "GoalDiff<=3":
        lambda d: d["goal_diff_diff"].abs() <= 3,

    "GoalDiff<=5":
        lambda d: d["goal_diff_diff"].abs() <= 5,

    "Form<=3":
        lambda d: d["form_diff"].abs() <= 3,

    "Rank<=4":
        lambda d: d["rank_diff"].abs() <= 4,

    "DrawBase":
        lambda d: (
            d["elo_expected_draw_base"]
            .between(
                0.70,
                0.85,
                inclusive="both",
            )
        ),
}


def evaluate(df, names):

    mask = pd.Series(
        True,
        index=df.index,
    )

    for name in names:
        mask &= RULES[name](df)

    target = df[mask]

    if len(target) == 0:
        return None

    draws = (
        target["result"]
        .astype(int)
        .eq(0)
        .sum()
    )

    return {
        "rule":
            " & ".join(names),
        "conditions":
            len(names),
        "matches":
            len(target),
        "draws":
            int(draws),
        "draw_rate":
            draws / len(target),
    }


def main():

    df = pd.read_csv(INPUT_PATH)

    rows = []

    rule_names = list(RULES)

    for n in [2, 3]:

        for combo in combinations(
            rule_names,
            n,
        ):

            result = evaluate(
                df,
                combo,
            )

            if result is not None:
                rows.append(result)

    result = (
        pd.DataFrame(rows)
        .sort_values(
            [
                "draw_rate",
                "matches",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    result["qualifies"] = (
        (result["matches"] >= 300)
        &
        (result["draw_rate"] >= 0.30)
    )

    print("=" * 100)
    print("Draw Warning Rule Research")
    print("=" * 100)

    print(
        result.head(30).to_string(
            index=False,
            formatters={
                "draw_rate":
                    "{:.2%}".format
            },
        )
    )

    print()
    print("=" * 100)
    print("Qualified Rules")
    print("=" * 100)

    print(
        result[
            result["qualifies"]
        ].to_string(
            index=False,
            formatters={
                "draw_rate":
                    "{:.2%}".format
            },
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_DIR /
        "draw_warning_rules.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print(
        OUTPUT_DIR /
        "draw_warning_rules.csv"
    )


if __name__ == "__main__":
    main()
