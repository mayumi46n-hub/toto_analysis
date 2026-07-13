from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

DATA_PATH = Path("data/training_data_v3.csv")
MODEL_DIR = Path("data/models")
MODEL_PATH = MODEL_DIR / "gradient_boosting_v1.pkl"

TRAIN_END_SEASON = 2022
TEST_START_SEASON = 2023


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"学習データがありません: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"読込: {len(df)}試合")
    print(f"列数: {len(df.columns)}")

    return df


def split_dataset(df):
    train = df[
        df["season"] <= TRAIN_END_SEASON
    ].copy()

    test = df[
        df["season"] >= TEST_START_SEASON
    ].copy()

    if train.empty:
        raise RuntimeError(
            "学習データが0件です"
        )

    if test.empty:
        raise RuntimeError(
            "評価データが0件です"
        )

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

    print()
    print(
        f"学習年度: "
        f"{train['season'].min()}"
        f"〜{train['season'].max()}"
    )
    print(
        f"評価年度: "
        f"{test['season'].min()}"
        f"〜{test['season'].max()}"
    )
    print(f"学習: {len(train)}試合")
    print(f"評価: {len(test)}試合")
    print(f"特徴量: {len(feature_columns)}列")

    return (
        feature_columns,
        X_train,
        X_test,
        y_train,
        y_test,
    )


def train_model(X_train, y_train):
    model = GradientBoostingClassifier(
        random_state=42,
    )

    print()
    print("GradientBoosting 学習開始")

    model.fit(
        X_train,
        y_train,
    )

    print("GradientBoosting 学習完了")

    return model


def evaluate_model(
    model,
    feature_columns,
    X_test,
    y_test,
):
    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print()
    print("Accuracy")
    print("----------------------------------")
    print(f"{accuracy:.4f}")

    print()
    print("Confusion Matrix")
    print("行=実際 / 列=予測 / 順序=[1, 0, 2]")
    print("----------------------------------")
    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=[1, 0, 2],
        )
    )

    print()
    print("Classification Report")
    print("----------------------------------")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            digits=4,
            zero_division=0,
        )
    )

    importance = (
        pd.DataFrame(
            {
                "feature": feature_columns,
                "importance": (
                    model.feature_importances_
                ),
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

    return accuracy


def save_model(
    model,
    feature_columns,
    accuracy,
):
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_columns": feature_columns,
        "model_name": (
            "GradientBoostingClassifier"
        ),
        "model_version": 1,
        "training_data_version": 3,
        "train_end_season": (
            TRAIN_END_SEASON
        ),
        "test_start_season": (
            TEST_START_SEASON
        ),
        "test_accuracy": accuracy,
        "class_order": list(
            model.classes_
        ),
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print()
    print("Model Saved")
    print("----------------------------------")
    print(MODEL_PATH)


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

    accuracy = evaluate_model(
        model=model,
        feature_columns=feature_columns,
        X_test=X_test,
        y_test=y_test,
    )

    save_model(
        model=model,
        feature_columns=feature_columns,
        accuracy=accuracy,
    )


if __name__ == "__main__":
    main()