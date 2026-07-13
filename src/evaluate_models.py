from pathlib import Path
from time import perf_counter

import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
)
from sklearn.metrics import accuracy_score

DATA_PATH = Path("data/training_data_v1.csv")


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    feature_columns = [
        c
        for c in df.columns
        if c not in (
            "season",
            "league",
            "result",
        )
    ]

    train = df[df["season"] <= 2022]
    test = df[df["season"] >= 2023]

    X_train = train[feature_columns]
    y_train = train["result"]

    X_test = test[feature_columns]
    y_test = test["result"]

    return (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    )


def evaluate_model(
    name,
    model,
    X_train,
    y_train,
    X_test,
    y_test,
):
    start = perf_counter()

    model.fit(
        X_train,
        y_train,
    )

    train_time = perf_counter() - start

    start = perf_counter()

    pred = model.predict(X_test)

    predict_time = perf_counter() - start

    accuracy = accuracy_score(
        y_test,
        pred,
    )

    return {
        "Model": name,
        "Accuracy": accuracy,
        "Train(s)": train_time,
        "Predict(s)": predict_time,
    }


def main():

    (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = load_dataset()

    models = [
        (
            "RandomForest",
            RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "ExtraTrees",
            ExtraTreesClassifier(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
        (
            "GradientBoosting",
            GradientBoostingClassifier(
                random_state=42,
            ),
        ),
    ]

    results = []

    print()
    print("Model Evaluation")
    print("=" * 70)

    for name, model in models:

        print(f"Training {name}...")

        result = evaluate_model(
            name,
            model,
            X_train,
            y_train,
            X_test,
            y_test,
        )

        results.append(result)

    df = pd.DataFrame(results)

    df = df.sort_values(
        "Accuracy",
        ascending=False,
    )

    print()
    print(df.to_string(index=False))

    best = df.iloc[0]

    print()
    print("Best Model")
    print("-" * 70)
    print(
        f"{best['Model']}  Accuracy={best['Accuracy']:.4f}"
    )


if __name__ == "__main__":
    main()