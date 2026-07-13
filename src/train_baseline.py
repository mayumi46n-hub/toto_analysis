from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

DATA_PATH = Path("data/training_data_v1.csv")
MODEL_DIR = Path("data/models")
MODEL_PATH = MODEL_DIR / "baseline_rf_v1.pkl"


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    print(f"読込: {len(df)}試合")
    print(f"列数: {len(df.columns)}")

    return df


def split_dataset(df):
    train = df[df["season"] <= 2022].copy()
    test = df[df["season"] >= 2023].copy()

    print()
    print(
        f"学習年度: "
        f"{train['season'].min()}〜{train['season'].max()}"
    )
    print(
        f"評価年度: "
        f"{test['season'].min()}〜{test['season'].max()}"
    )
    print(f"学習: {len(train)}試合")
    print(f"評価: {len(test)}試合")

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


def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    return model


def save_model(model, feature_columns):
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_columns": feature_columns,
        "model_name": "RandomForestClassifier",
        "model_version": 1,
        "train_end_season": 2022,
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print()
    print("Model Saved")
    print("----------------------------------")
    print(MODEL_PATH)


def evaluate(
    model,
    feature_columns,
    X_test,
    y_test,
):
    pred = model.predict(X_test)

    print()
    print("Accuracy")
    print("----------------------------------")
    print(f"{accuracy_score(y_test, pred):.4f}")

    print()
    print("Confusion Matrix")
    print("----------------------------------")
    print(
        confusion_matrix(
            y_test,
            pred,
            labels=[1, 0, 2],
        )
    )

    print()
    print("Classification Report")
    print("----------------------------------")
    print(
        classification_report(
            y_test,
            pred,
            labels=[0, 1, 2],
            digits=4,
            zero_division=0,
        )
    )

    importance = (
        pd.DataFrame(
            {
                "feature": feature_columns,
                "importance": model.feature_importances_,
            }
        )
        .sort_values(
            "importance",
            ascending=False,
        )
        .head(20)
    )

    print()
    print("Top20 Feature Importance")
    print("----------------------------------")
    print(
        importance.to_string(
            index=False,
        )
    )


def main():
    df = load_dataset()

    (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_dataset(df)

    model = train_model(
        X_train,
        y_train,
    )

    evaluate(
        model,
        feature_columns,
        X_test,
        y_test,
    )

    save_model(
        model,
        feature_columns,
    )


if __name__ == "__main__":
    main()