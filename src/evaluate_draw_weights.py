from pathlib import Path
import time

import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    recall_score,
)


DATA_PATH = Path("data/training_data_v3.csv")

DRAW_WEIGHTS = [
    1.00,
    1.05,
    1.10,
    1.15,
    1.20,
    1.25,
    1.30,
    1.35,
    1.40,
    1.50,
]


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    train = df[df["season"] <= 2022].copy()
    test = df[df["season"] >= 2023].copy()

    feature_columns = [
        column
        for column in df.columns
        if column not in (
            "season",
            "league",
            "result",
        )
    ]

    X_train = train[feature_columns]
    y_train = train["result"].astype(int)

    X_test = test[feature_columns]
    y_test = test["result"].astype(int)

    return (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    )


def make_sample_weight(
    y_train,
    draw_weight,
):
    weights = np.ones(
        len(y_train),
        dtype=float,
    )

    draw_mask = (
        y_train.to_numpy() == 0
    )

    weights[draw_mask] = draw_weight

    return weights


def evaluate_setting(
    X_train,
    X_test,
    y_train,
    y_test,
    draw_weight,
):
    sample_weight = make_sample_weight(
        y_train=y_train,
        draw_weight=draw_weight,
    )

    model = GradientBoostingClassifier(
        random_state=42,
    )

    started = time.perf_counter()

    model.fit(
        X_train,
        y_train,
        sample_weight=sample_weight,
    )

    train_seconds = (
        time.perf_counter() - started
    )

    prediction = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        prediction,
    )

    macro_f1 = f1_score(
        y_test,
        prediction,
        labels=[1, 0, 2],
        average="macro",
        zero_division=0,
    )

    draw_recall = recall_score(
        y_test,
        prediction,
        labels=[0],
        average="macro",
        zero_division=0,
    )

    draw_predictions = int(
        (prediction == 0).sum()
    )

    return {
        "draw_weight": draw_weight,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "draw_recall": draw_recall,
        "draw_predictions": draw_predictions,
        "train_seconds": train_seconds,
        "prediction": prediction,
    }


def main():
    (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = load_dataset()

    print("Light Draw Weight Evaluation")
    print("=" * 78)
    print(f"学習: {len(X_train)}試合")
    print(f"評価: {len(X_test)}試合")
    print(f"特徴量: {len(feature_columns)}列")
    print()

    results = []

    for draw_weight in DRAW_WEIGHTS:
        print(
            "Training "
            f"draw_weight={draw_weight:.2f}..."
        )

        result = evaluate_setting(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            draw_weight=draw_weight,
        )

        results.append(result)

    comparison_rows = []

    for result in results:
        comparison_rows.append({
            "draw_weight": (
                result["draw_weight"]
            ),
            "accuracy": result["accuracy"],
            "macro_f1": result["macro_f1"],
            "draw_recall": (
                result["draw_recall"]
            ),
            "draw_predictions": (
                result["draw_predictions"]
            ),
            "train_seconds": (
                result["train_seconds"]
            ),
        })

    result_df = pd.DataFrame(
        comparison_rows
    )

    result_df = result_df.sort_values(
        by=[
            "macro_f1",
            "accuracy",
        ],
        ascending=False,
    )

    print()
    print("Comparison")
    print("=" * 78)

    print(
        result_df.to_string(
            index=False,
            formatters={
                "accuracy": "{:.4f}".format,
                "macro_f1": "{:.4f}".format,
                "draw_recall": "{:.4f}".format,
                "train_seconds": "{:.2f}".format,
            },
        )
    )

    candidates = result_df[
        result_df["accuracy"] >= 0.44
    ].copy()

    if candidates.empty:
        best_row = result_df.iloc[0]
        selection_reason = (
            "Accuracy 0.44以上の候補なし。"
            "Macro F1最大を選択"
        )
    else:
        candidates = candidates.sort_values(
            by=[
                "macro_f1",
                "draw_recall",
                "accuracy",
            ],
            ascending=False,
        )

        best_row = candidates.iloc[0]
        selection_reason = (
            "Accuracy 0.44以上の中で"
            "Macro F1最大"
        )

    best_weight = float(
        best_row["draw_weight"]
    )

    best = next(
        result
        for result in results
        if result["draw_weight"]
        == best_weight
    )

    print()
    print("Selected Candidate")
    print("=" * 78)
    print(selection_reason)
    print(
        f"draw_weight: {best_weight:.2f}"
    )
    print(
        f"accuracy: {best['accuracy']:.4f}"
    )
    print(
        f"macro_f1: {best['macro_f1']:.4f}"
    )
    print(
        f"draw_recall: "
        f"{best['draw_recall']:.4f}"
    )
    print(
        f"draw_predictions: "
        f"{best['draw_predictions']}"
    )

    print()
    print(
        classification_report(
            y_test,
            best["prediction"],
            labels=[1, 0, 2],
            target_names=[
                "1 Home",
                "0 Draw",
                "2 Away",
            ],
            digits=4,
            zero_division=0,
        )
    )


if __name__ == "__main__":
    main()