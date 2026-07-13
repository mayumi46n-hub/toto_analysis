from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(
    "data/models/gradient_boosting_v1.pkl"
)

DATA_PATH = Path(
    "data/training_data_v3.csv"
)

PREDICTION_START_SEASON = 2023
SAMPLE_SIZE = 20


def result_name(result):
    names = {
        1: "ホーム勝ち",
        0: "引分",
        2: "アウェイ勝ち",
    }

    return names.get(
        int(result),
        str(result),
    )


def load_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"モデルがありません: {MODEL_PATH}"
        )

    artifact = joblib.load(
        MODEL_PATH
    )

    required_keys = {
        "model",
        "feature_columns",
        "model_name",
        "model_version",
    }

    missing = (
        required_keys
        - set(artifact)
    )

    if missing:
        raise RuntimeError(
            f"モデル情報が不足しています: "
            f"{sorted(missing)}"
        )

    print("Model Loaded")
    print("----------------------------------")
    print(f"Path: {MODEL_PATH}")
    print(
        f"Name: "
        f"{artifact['model_name']}"
    )
    print(
        f"Version: "
        f"{artifact['model_version']}"
    )
    print(
        f"Accuracy: "
        f"{artifact.get('test_accuracy', 0):.4f}"
    )

    return artifact


def load_prediction_data(
    feature_columns,
):
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"データがありません: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH
    )

    df = df[
        df["season"]
        >= PREDICTION_START_SEASON
    ].copy()

    missing_columns = [
        column
        for column in feature_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise RuntimeError(
            "不足している特徴量: "
            + ", ".join(missing_columns)
        )

    print()
    print(
        f"予測対象読込: {len(df)}試合"
    )
    print(
        f"対象年度: "
        f"{df['season'].min()}"
        f"〜{df['season'].max()}"
    )

    X = df[feature_columns]

    return X, df


def probability_map(
    classes,
    probabilities,
):
    return {
        int(class_label): probability
        for class_label, probability
        in zip(
            classes,
            probabilities,
        )
    }


def show_predictions(
    model,
    X,
    df,
):
    probabilities = (
        model.predict_proba(X)
    )

    predictions = model.predict(X)

    sample_count = min(
        SAMPLE_SIZE,
        len(df),
    )

    print()
    print("Prediction Sample")
    print("=" * 72)

    for index in range(sample_count):
        row = df.iloc[index]

        probs = probability_map(
            classes=model.classes_,
            probabilities=(
                probabilities[index]
            ),
        )

        actual = int(
            row["result"]
        )

        predicted = int(
            predictions[index]
        )

        correct_mark = (
            "○"
            if actual == predicted
            else "×"
        )

        print(
            f"[{index + 1:02d}] "
            f"{int(row['season'])} "
            f"{row['league']} "
            f"予想={predicted}"
            f"({result_name(predicted)}) "
            f"実際={actual}"
            f"({result_name(actual)}) "
            f"{correct_mark}"
        )

        print(
            "     "
            f"1 ホーム勝ち: "
            f"{probs.get(1, 0.0) * 100:5.1f}%  "
            f"0 引分: "
            f"{probs.get(0, 0.0) * 100:5.1f}%  "
            f"2 アウェイ勝ち: "
            f"{probs.get(2, 0.0) * 100:5.1f}%"
        )


def main():
    artifact = load_artifact()

    model = artifact["model"]
    feature_columns = (
        artifact["feature_columns"]
    )

    X, df = load_prediction_data(
        feature_columns
    )

    show_predictions(
        model=model,
        X=X,
        df=df,
    )


if __name__ == "__main__":
    main()