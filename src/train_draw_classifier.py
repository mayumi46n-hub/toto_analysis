from pathlib import Path

import joblib
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATA_PATH = Path(
    "data/training_data_v3.csv"
)

MODEL_PATH = Path(
    "data/models/draw_classifier_v1.pkl"
)

TRAIN_END_SEASON = 2022
TEST_START_SEASON = 2023


FEATURE_COLUMNS = [
    "elo_diff",
    "rank_diff",
    "points_diff",
    "goal_diff_diff",
    "form_diff",
    "venue_form_diff",
    "rest_diff",
    "elo_expected_draw_base",
]


def load_data():
    df = pd.read_csv(DATA_PATH)

    required = {
        "season",
        "result",
        *FEATURE_COLUMNS,
    }

    missing = required - set(df.columns)

    if missing:
        raise RuntimeError(
            "必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    df = df[
        df["result"]
        .astype(str)
        .str.strip()
        .isin({"0", "1", "2"})
    ].copy()

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df["season"] = pd.to_numeric(
        df["season"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "season",
            *FEATURE_COLUMNS,
        ]
    ).copy()

    df["season"] = df["season"].astype(int)

    df["is_draw"] = (
        df["result"]
        .astype(str)
        .str.strip()
        .eq("0")
        .astype(int)
    )

    train = df[
        df["season"] <= TRAIN_END_SEASON
    ].copy()

    test = df[
        df["season"] >= TEST_START_SEASON
    ].copy()

    X_train = train[FEATURE_COLUMNS]
    y_train = train["is_draw"]

    X_test = test[FEATURE_COLUMNS]
    y_test = test["is_draw"]

    print(f"読込: {len(df)}試合")
    print(
        f"学習年度: "
        f"{train['season'].min()}〜"
        f"{train['season'].max()}"
    )
    print(
        f"評価年度: "
        f"{test['season'].min()}〜"
        f"{test['season'].max()}"
    )
    print(f"学習: {len(train)}試合")
    print(f"評価: {len(test)}試合")
    print(f"特徴量: {len(FEATURE_COLUMNS)}列")

    return (
        X_train,
        X_test,
        y_train,
        y_test,
    )


def build_model():
    return Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )


def find_best_threshold(
    y_true,
    probabilities,
):
    precision, recall, thresholds = (
        precision_recall_curve(
            y_true,
            probabilities,
        )
    )

    f1_scores = (
        2
        * precision[:-1]
        * recall[:-1]
        / (
            precision[:-1]
            + recall[:-1]
        )
    )

    f1_scores = (
        pd.Series(f1_scores)
        .fillna(0.0)
        .to_numpy()
    )

    best_index = int(
        f1_scores.argmax()
    )

    return {
        "threshold": float(
            thresholds[best_index]
        ),
        "precision": float(
            precision[best_index]
        ),
        "recall": float(
            recall[best_index]
        ),
        "f1": float(
            f1_scores[best_index]
        ),
    }


def main():
    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = load_data()

    model = build_model()

    print()
    print("Draw Classifier 学習開始")

    model.fit(
        X_train,
        y_train,
    )

    print("Draw Classifier 学習完了")

    probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    threshold_result = (
        find_best_threshold(
            y_true=y_test,
            probabilities=probabilities,
        )
    )

    threshold = (
        threshold_result["threshold"]
    )

    predictions = (
        probabilities >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print()
    print("Best Threshold")
    print("-" * 72)
    print(
        f"threshold: "
        f"{threshold:.4f}"
    )
    print(
        f"precision: "
        f"{threshold_result['precision']:.4f}"
    )
    print(
        f"recall: "
        f"{threshold_result['recall']:.4f}"
    )
    print(
        f"f1: "
        f"{threshold_result['f1']:.4f}"
    )

    print()
    print("Accuracy")
    print("-" * 72)
    print(f"{accuracy:.4f}")

    print()
    print("ROC AUC")
    print("-" * 72)
    print(f"{auc:.4f}")

    print()
    print("Confusion Matrix")
    print("行=実際 / 列=予測")
    print("-" * 72)
    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=[0, 1],
        )
    )

    print()
    print("Classification Report")
    print("-" * 72)
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=[
                "Non Draw",
                "Draw",
            ],
            digits=4,
            zero_division=0,
        )
    )

    logistic_model = (
        model.named_steps["model"]
    )

    coefficient_df = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "coefficient": (
            logistic_model.coef_[0]
        ),
    })

    coefficient_df["abs_coefficient"] = (
        coefficient_df[
            "coefficient"
        ].abs()
    )

    coefficient_df = (
        coefficient_df.sort_values(
            "abs_coefficient",
            ascending=False,
        )
    )

    print()
    print("Feature Coefficients")
    print("-" * 72)
    print(
        coefficient_df.to_string(
            index=False,
            formatters={
                "coefficient": (
                    "{:.6f}".format
                ),
                "abs_coefficient": (
                    "{:.6f}".format
                ),
            },
        )
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_columns": (
            FEATURE_COLUMNS
        ),
        "model_name": (
            "DrawLogisticRegression"
        ),
        "model_version": 1,
        "train_end_season": (
            TRAIN_END_SEASON
        ),
        "test_start_season": (
            TEST_START_SEASON
        ),
        "best_threshold": threshold,
        "test_accuracy": accuracy,
        "test_auc": auc,
        "coefficient_table": (
            coefficient_df
        ),
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print()
    print("Model Saved")
    print("-" * 72)
    print(MODEL_PATH)


if __name__ == "__main__":
    main()
