# Project AKAMURASAKI
# Draw Research v1
期間：2026年7月

---

# 目的

「引分を制するものはtotoを制する」

引分予測精度向上のため、
2002〜2025年（24年間）のJリーグデータを研究する。

---

# 使用データ

対象期間
2002〜2025

対象試合数
16,848試合

引分数
4,319試合

引分率
25.64%

---

# 実施した研究

## 1 Draw Distribution

リーグ別
年度別
引分率を調査

結果

・J1 約24%
・J2 約27%

2022年は30%を超える特殊シーズン

---

## 2 Draw Conditions

以下を調査

・Elo差
・順位差
・勝点差
・得失点差
・フォーム差
・休養日差

結果

差が小さいほど
引分率は高くなる傾向。

---

## 3 Draw Pattern

単独条件

2条件

3条件

を探索。

結果

最良でも

約28%

30%は超えなかった。

---

## 4 Draw Intelligence Score v1

6指標から
0〜10点を作成。

結果

Score7

29.37%

が最高。

Score10は最高ではなかった。

---

## 5 Draw Probability

GradientBoostingの

prob_draw

を調査。

結果

Draw確率が高いほど
実際の引分率が高くなる
傾向は確認できなかった。

---

## 6 Draw Trap

AIが

ホーム勝ち

アウェイ勝ち

と予測したが

実際は引分

となった試合を研究。

結果

Draw Probabilityだけでは
Trapは検出できなかった。

---

# 学んだこと

引分は

単一の特徴量では説明できない。

Eloだけでもない。

DrawBaseだけでもない。

Draw Probabilityだけでもない。

複数の条件が
組み合わさることで
発生する。

---

# 今後の研究

Draw Trap v2

AIの弱点分析

Confidence研究

Draw Risk Engine

GradientBoosting v3

training_data_v4

---

# 現時点での結論

引分予測は

「引分確率」

ではなく

「AIが引分で間違える条件」

を学習した方が
実戦的である可能性が高い。