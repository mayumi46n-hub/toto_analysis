# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data/features/training_dataset_2026.csv"
DEFAULT_MODEL = PROJECT_ROOT / "data/models/lightgbm_toto_model.joblib"
DEFAULT_METRICS = PROJECT_ROOT / "data/models/lightgbm_toto_metrics.json"
DEFAULT_IMPORTANCE = PROJECT_ROOT / "data/models/lightgbm_feature_importance.csv"

TARGET = "target_toto"

EXCLUDE = {
    "target_home_win", "target_draw", "target_away_win", "target_toto",
    "jleague_match_id", "footystats_page_id", "season", "league",
    "match_date", "home_team_name", "away_team_name", "home_team_id",
    "away_team_id", "competition", "kickoff_time", "stadium",
    "result_season", "result_competition", "result_match_date",
    "result_kickoff_time", "result_home_team", "result_away_team",
    "home_score", "away_score", "result_stadium", "result_attendance",
    "result_section",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="toto 3クラス分類用LightGBMモデルを学習します。"
    )
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--model-output", type=Path, default=DEFAULT_MODEL)
    p.add_argument("--metrics-output", type=Path, default=DEFAULT_METRICS)
    p.add_argument("--importance-output", type=Path, default=DEFAULT_IMPORTANCE)
    p.add_argument("--test-size", type=float, default=0.25)
    p.add_argument("--random-state", type=int, default=42)
    p.add_argument("--num-boost-round", type=int, default=300)
    p.add_argument("--early-stopping-rounds", type=int, default=30)
    p.add_argument("--allow-empty-target", action="store_true")
    return p.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def import_lightgbm():
    try:
        import lightgbm as lgb
    except ImportError as exc:
        raise RuntimeError(
            "lightgbmが未インストールです。次を実行してください:\n"
            "pip install lightgbm"
        ) from exc
    return lgb


def load_training_data(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"入力CSVが見つかりません: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    if TARGET not in df.columns:
        raise ValueError(f"{TARGET}列がありません")

    y_all = pd.to_numeric(df[TARGET], errors="coerce")
    mask = y_all.isin([0, 1, 2])
    df = df.loc[mask].copy()
    y = y_all.loc[mask].astype(int)

    X = pd.DataFrame(index=df.index)

    for column in df.columns:
        if column in EXCLUDE:
            continue

        numeric = pd.to_numeric(df[column], errors="coerce")

        if numeric.notna().any():
            X[column] = numeric.astype(float)

    if len(y) > 0 and X.empty:
        raise RuntimeError("数値特徴量が見つかりません")

    return df, X, y


def validate_classes(y: pd.Series, test_size: float) -> dict[int, int]:
    counts = {
        int(k): int(v)
        for k, v in y.value_counts().sort_index().items()
    }

    if len(counts) < 2:
        raise RuntimeError(
            f"学習には最低2クラス必要です。現在: {counts}"
        )

    for label, count in counts.items():
        if count < 2:
            raise RuntimeError(
                f"各クラス最低2件必要です: class={label}, count={count}"
            )

        if count * test_size < 1 or count * (1 - test_size) < 1:
            raise RuntimeError(
                "train/testの両方に各クラスを配置できません: "
                f"class={label}, count={count}, test_size={test_size}"
            )

    return counts


def main() -> int:
    args = parse_args()

    if not 0 < args.test_size < 1:
        raise ValueError("--test-sizeは0より大きく1未満で指定してください")

    input_path = resolve(args.input)
    model_path = resolve(args.model_output)
    metrics_path = resolve(args.metrics_output)
    importance_path = resolve(args.importance_output)

    _, X, y = load_training_data(input_path)

    if len(y) == 0:
        print("=" * 100)
        print("LightGBM Training")
        print("=" * 100)
        print(f"input        : {rel(input_path)}")
        print("labeled rows : 0")
        print()
        print("target_totoが入った試合がありません。")
        print("現在の2026/27データは未開催のため、まだ学習できません。")

        if args.allow_empty_target:
            print("--allow-empty-target指定により正常終了します。")
            return 0

        return 2

    class_counts = validate_classes(y, args.test_size)

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    lgb = import_lightgbm()

    train_set = lgb.Dataset(X_train, label=y_train)
    valid_set = lgb.Dataset(X_valid, label=y_valid, reference=train_set)

    params = {
        "objective": "multiclass",
        "num_class": 3,
        "metric": ["multi_logloss", "multi_error"],
        "learning_rate": 0.03,
        "num_leaves": 31,
        "min_data_in_leaf": 10,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.9,
        "bagging_freq": 1,
        "lambda_l2": 1.0,
        "verbosity": -1,
        "seed": args.random_state,
    }

    callbacks = [lgb.log_evaluation(period=20)]

    if args.early_stopping_rounds > 0:
        callbacks.append(
            lgb.early_stopping(
                args.early_stopping_rounds,
                verbose=True,
            )
        )

    model = lgb.train(
        params,
        train_set,
        num_boost_round=args.num_boost_round,
        valid_sets=[train_set, valid_set],
        valid_names=["train", "valid"],
        callbacks=callbacks,
    )

    iteration = model.best_iteration or model.current_iteration()
    probabilities = model.predict(X_valid, num_iteration=iteration)
    predicted = np.argmax(probabilities, axis=1)

    accuracy = float(accuracy_score(y_valid, predicted))
    loss = float(log_loss(y_valid, probabilities, labels=[0, 1, 2]))
    matrix = confusion_matrix(
        y_valid,
        predicted,
        labels=[0, 1, 2],
    ).astype(int).tolist()

    metrics = {
        "input": rel(input_path),
        "training_rows": int(len(X_train)),
        "validation_rows": int(len(X_valid)),
        "feature_count": int(X.shape[1]),
        "class_counts": {str(k): v for k, v in class_counts.items()},
        "best_iteration": int(iteration),
        "accuracy": accuracy,
        "log_loss": loss,
        "confusion_matrix": matrix,
        "class_mapping": {"0": "home_win", "1": "draw", "2": "away_win"},
        "params": params,
    }

    for path in (model_path, metrics_path, importance_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "feature_columns": list(X.columns),
            "target_column": TARGET,
            "class_mapping": {0: "home_win", 1: "draw", 2: "away_win"},
            "metrics": metrics,
        },
        model_path,
    )

    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    importance = pd.DataFrame(
        {
            "feature": list(X.columns),
            "importance_gain": model.feature_importance("gain"),
            "importance_split": model.feature_importance("split"),
        }
    ).sort_values(
        ["importance_gain", "importance_split"],
        ascending=False,
    )

    importance.to_csv(
        importance_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("=" * 100)
    print("LightGBM Training")
    print("=" * 100)
    print(f"labeled rows      : {len(y)}")
    print(f"training rows     : {len(X_train)}")
    print(f"validation rows   : {len(X_valid)}")
    print(f"feature count     : {X.shape[1]}")
    print(f"class counts      : {class_counts}")
    print(f"accuracy          : {accuracy:.6f}")
    print(f"log loss          : {loss:.6f}")
    print(f"best iteration    : {iteration}")
    print(f"model             : {rel(model_path)}")
    print(f"metrics           : {rel(metrics_path)}")
    print(f"feature importance: {rel(importance_path)}")
    print()
    print("CONFUSION MATRIX")
    print("-" * 100)
    for row in matrix:
        print(row)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
