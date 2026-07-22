import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)

CSV_PATH = (
    "data/evaluation/"
    "toto_2025_prediction_details.csv"
)


def main():
    df = pd.read_csv(CSV_PATH)

    evaluated = df.dropna(
        subset=["actual", "prediction"]
    ).copy()

    evaluated["actual"] = (
        evaluated["actual"].astype(int)
    )
    evaluated["prediction"] = (
        evaluated["prediction"].astype(int)
    )

    print("=" * 72)
    print("2025 Prediction Analysis")
    print("=" * 72)

    print()
    print(f"CSV全行数: {len(df)}")
    print(f"評価対象: {len(evaluated)}")
    print(f"対象外・未予測: {len(df) - len(evaluated)}")

    print()
    print("Classification Report")
    print("-" * 72)

    report = classification_report(
        evaluated["actual"],
        evaluated["prediction"],
        labels=[1, 0, 2],
        target_names=[
            "1 Home",
            "0 Draw",
            "2 Away",
        ],
        digits=4,
        zero_division=0,
    )

    print(report)

    matrix = confusion_matrix(
        evaluated["actual"],
        evaluated["prediction"],
        labels=[1, 0, 2],
    )

    matrix_df = pd.DataFrame(
        matrix,
        index=[
            "Actual 1 Home",
            "Actual 0 Draw",
            "Actual 2 Away",
        ],
        columns=[
            "Pred 1 Home",
            "Pred 0 Draw",
            "Pred 2 Away",
        ],
    )

    print()
    print(
        "Confusion Matrix "
        "(行=実際 / 列=予測)"
    )
    print("-" * 72)
    print(matrix_df.to_string())


if __name__ == "__main__":
    main()