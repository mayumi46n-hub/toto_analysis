python - <<'PY'
from ctypes import PyDLL
from pathlib import Path

p = Path("src/train_gradient_boosting.py")
s = p.read_text(encoding="utf-8")

old = """def train_model(X_train, y_train):
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
"""

new = """def train_model(X_train, y_train):
    draw_weight = 1.30

    model = GradientBoostingClassifier(
        random_state=42,
    )

    sample_weight = np.ones(
        len(y_train),
        dtype=float,
    )

    sample_weight[
        y_train.to_numpy() == 0
    ] = draw_weight

    print()
    print("GradientBoosting 学習開始")
    print(f"Draw Weight: {draw_weight:.2f}")

    model.fit(
        X_train,
        y_train,
        sample_weight=sample_weight,
    )

    print("GradientBoosting 学習完了")

    return model
"""

assert s.count(old) == 1
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("STEP2 draw weight OK")
PyDLL