from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

INPUT_PATH = Path("data/training_data_v3.csv")

TARGET = "result"

DROP_COLUMNS = [
    "season",
    "league",
    "result",
]


def main():

    df = pd.read_csv(INPUT_PATH)

    X = df.drop(
        columns=DROP_COLUMNS,
    )

    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = GradientBoostingClassifier(
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    importance = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_,
    })

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print("=" * 90)
    print("Feature Importance")
    print("=" * 90)

    print(
        importance.head(25).to_string(
            index=False,
            formatters={
                "importance":"{:.4f}".format
            },
        )
    )

    output = Path(
        "data/evaluation/feature_importance.csv"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    importance.to_csv(
        output,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("CSV Saved")
    print(output)


if __name__ == "__main__":
    main()
