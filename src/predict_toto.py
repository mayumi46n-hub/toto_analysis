from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("data/models/baseline_rf_v1.pkl")
DATA_PATH = Path("data/training_data_v1.csv")


def load_model():
    artifact = joblib.load(MODEL_PATH)

    print("Model Loaded")
    print("----------------------------------")
    print(MODEL_PATH)

    return (
        artifact["model"],
        artifact["feature_columns"],
    )


def load_dataset(feature_columns):
    df = pd.read_csv(DATA_PATH)

    print()
    print(f"読込: {len(df)}試合")

    return df[feature_columns], df


def predict(
    model,
    X,
    df,
):
    probabilities = model.predict_proba(X)
    predictions = model.predict(X)

    class_order = list(model.classes_)

    print()
    print("Prediction Sample")
    print("----------------------------------")

    for i in range(min(20, len(df))):

        probs = {
            c: p
            for c, p in zip(
                class_order,
                probabilities[i],
            )
        }

        print(
            f"[{i + 1:02d}] "
            f"{df.iloc[i]['season']} "
            f"{df.iloc[i]['league']} "
            f"Result={df.iloc[i]['result']} "
            f"Pred={predictions[i]}"
        )

        print(
            "    "
            f"Home={probs.get(1,0)*100:5.1f}%   "
            f"Draw={probs.get(0,0)*100:5.1f}%   "
            f"Away={probs.get(2,0)*100:5.1f}%"
        )


def main():
    (
        model,
        feature_columns,
    ) = load_model()

    (
        X,
        df,
    ) = load_dataset(feature_columns)

    predict(
        model,
        X,
        df,
    )


if __name__ == "__main__":
    main()