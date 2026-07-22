from pathlib import Path

import pandas as pd

INPUT_PATH = Path(
    "data/evaluation/toto_2025_prediction_details_v2.csv"
)

OUTPUT_PATH = Path(
    "data/evaluation/draw_research/"
    "draw_probability_distribution_2025.csv"
)


def main():

    df = pd.read_csv(INPUT_PATH)

    bins = [
        0.00,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        1.00,
    ]

    labels = [
        "0.00-0.20",
        "0.20-0.25",
        "0.25-0.30",
        "0.30-0.35",
        "0.35-0.40",
        "0.40+",
    ]

    df["draw_band"] = pd.cut(
        df["prob_draw"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    rows = []

    for band, target in df.groupby(
        "draw_band",
        observed=True,
    ):

        matches = len(target)

        draws = (
            target["actual"]
            .eq(0)
            .sum()
        )

        accuracy = (
            target["correct"]
            .mean()
        )

        rows.append({
            "draw_band": band,
            "matches": matches,
            "draws": draws,
            "draw_rate": draws / matches,
            "accuracy": accuracy,
            "avg_draw_probability":
                target["prob_draw"].mean(),
        })

    result = (
        pd.DataFrame(rows)
        .sort_values(
            "avg_draw_probability"
        )
    )

    print("=" * 100)
    print("Draw Probability Distribution")
    print("=" * 100)

    print(
        result.to_string(
            index=False,
            formatters={
                "draw_rate":
                    "{:.2%}".format,
                "accuracy":
                    "{:.2%}".format,
                "avg_draw_probability":
                    "{:.3f}".format,
            },
        )
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
