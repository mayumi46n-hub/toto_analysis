from pathlib import Path

import pandas as pd

INPUT_PATH = Path(
    "data/evaluation/draw_research/"
    "draw_intelligence_v1_details.csv"
)

OUTPUT_DIR = Path(
    "data/evaluation/draw_research"
)


COMPONENTS = [
    "score_draw_base",
    "score_elo",
    "score_goal_diff",
    "score_points",
    "score_form",
    "score_rank",
]


def main():

    df = pd.read_csv(INPUT_PATH)

    print("=" * 88)
    print("Draw Intelligence Score Pattern Analysis")
    print("=" * 88)

    summary_rows = []

    for score in sorted(
        df["draw_intelligence_score"].unique()
    ):

        target = df[
            df["draw_intelligence_score"]
            == score
        ]

        print()
        print("-" * 88)
        print(
            f"Score {score}"
        )
        print(
            f"試合数: {len(target)}"
        )

        row = {
            "score": score,
            "matches": len(target),
        }

        for component in COMPONENTS:

            rate = (
                target[component]
                .gt(0)
                .mean()
            )

            row[component] = rate

            print(
                f"{component:18}"
                f"{rate:6.1%}"
            )

        summary_rows.append(row)

    result = pd.DataFrame(
        summary_rows
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "draw_score_pattern_analysis.csv"
    )

    result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("=" * 88)
    print("CSV Saved")
    print(output_path)


if __name__ == "__main__":
    main()
