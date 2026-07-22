from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/evaluation/"
    "toto_2025_prediction_details_v1.csv"
)

OUTPUT_PATH = Path(
    "data/evaluation/"
    "draw_threshold_analysis_v1.csv"
)

THRESHOLDS = [
    0.20,
    0.22,
    0.24,
    0.25,
    0.26,
    0.28,
    0.30,
    0.32,
    0.34,
    0.35,
    0.36,
    0.38,
    0.40,
]


def main():
    df = pd.read_csv(INPUT_PATH)

    evaluated = df.dropna(
        subset=[
            "actual",
            "prediction",
            "prob_draw",
        ]
    ).copy()

    evaluated["actual"] = (
        evaluated["actual"].astype(int)
    )

    evaluated["prediction"] = (
        evaluated["prediction"].astype(int)
    )

    evaluated["is_draw"] = (
        evaluated["actual"] == 0
    )

    total_matches = len(evaluated)
    total_draws = int(
        evaluated["is_draw"].sum()
    )

    rows = []

    for threshold in THRESHOLDS:
        warning_mask = (
            evaluated["prob_draw"] >= threshold
        )

        warning_count = int(
            warning_mask.sum()
        )

        warned_draws = int(
            (
                warning_mask
                & evaluated["is_draw"]
            ).sum()
        )

        warned_non_draws = int(
            (
                warning_mask
                & ~evaluated["is_draw"]
            ).sum()
        )

        recall = (
            warned_draws / total_draws
            if total_draws
            else 0.0
        )

        precision = (
            warned_draws / warning_count
            if warning_count
            else 0.0
        )

        warning_rate = (
            warning_count / total_matches
            if total_matches
            else 0.0
        )

        rows.append({
            "threshold": threshold,
            "warning_count": warning_count,
            "warning_rate": warning_rate,
            "warned_draws": warned_draws,
            "warned_non_draws": warned_non_draws,
            "draw_precision": precision,
            "draw_recall": recall,
        })

    result = pd.DataFrame(rows)

    result["f1"] = (
        2
        * result["draw_precision"]
        * result["draw_recall"]
        / (
            result["draw_precision"]
            + result["draw_recall"]
        )
    ).fillna(0.0)

    print("=" * 88)
    print("Draw Threshold Analysis - v1")
    print("=" * 88)
    print(f"評価試合数: {total_matches}")
    print(f"実際の引分: {total_draws}")
    print()

    print(
        result.to_string(
            index=False,
            formatters={
                "threshold": "{:.2f}".format,
                "warning_rate": "{:.2%}".format,
                "draw_precision": "{:.2%}".format,
                "draw_recall": "{:.2%}".format,
                "f1": "{:.4f}".format,
            },
        )
    )

    best_f1 = result.sort_values(
        by=[
            "f1",
            "draw_recall",
        ],
        ascending=False,
    ).iloc[0]

    print()
    print("Best by Draw F1")
    print("-" * 88)
    print(
        f"threshold: "
        f"{best_f1['threshold']:.2f}"
    )
    print(
        f"警戒試合: "
        f"{int(best_f1['warning_count'])}"
    )
    print(
        f"引分的中: "
        f"{int(best_f1['warned_draws'])}"
        f" / {total_draws}"
    )
    print(
        f"precision: "
        f"{best_f1['draw_precision']:.2%}"
    )
    print(
        f"recall: "
        f"{best_f1['draw_recall']:.2%}"
    )
    print(
        f"F1: "
        f"{best_f1['f1']:.4f}"
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
    print(f"CSV Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()