# TotoLABO Feature Catalog

Version: 0.1

---

# Featureとは

Feature（特徴量）は、
試合を数値で表現するための情報である。

AIはFeatureのみを入力として学習する。

TotoLABOでは、
Featureを研究・検証し、
有効性が確認されたもののみ採用する。

---

# Feature Pipeline

選手分析
    ↓
チーム分析
    ↓
試合分析
    ↓
Feature生成
    ↓
AI
    ↓
試合予測
    ↓
toto予想

---

# Feature Status

⬜ Planned

🚧 Developing

✅ Verified

🧪 Research

---

# Rank Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F001|home_rank|ホーム順位|✅|
|F002|away_rank|アウェイ順位|✅|
|F003|rank_diff|順位差|🧪|

Research

Research0001

---

# Form Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F010|home_form|ホームフォーム|🚧|
|F011|away_form|アウェイフォーム|🚧|
|F012|form_diff|フォーム差|⬜|

---

# H2H Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F020|h2h_home_win|ホーム勝数|⬜|
|F021|h2h_draw|引分数|⬜|
|F022|h2h_away_win|アウェイ勝数|⬜|
|F023|h2h_score|H2Hスコア|⬜|

---

# Match Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F030|attendance|観客数|⬜|
|F031|weekday|曜日|⬜|
|F032|weather|天候|⬜|
|F033|stadium|スタジアム|⬜|

---

# Team Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F100|team_attack|攻撃力|⬜|
|F101|team_defense|守備力|⬜|
|F102|home_strength|ホーム力|⬜|
|F103|away_strength|アウェイ力|⬜|

---

# Player Features

|ID|Feature|Description|Status|
|--|-------|-----------|------|
|F200|minutes|出場時間|⬜|
|F201|shoot|シュート数|⬜|
|F202|shoot_rate|決定率|⬜|
|F203|pass|パス成功|⬜|
|F204|cross|クロス|⬜|
|F205|dribble|ドリブル|⬜|
|F206|duel|デュエル|⬜|

---

# Future Features

・年俸

・監督

・移動距離

・故障者

・代表招集

・連戦

・中2日

・海外遠征

・SNS話題量（検討）

・ブックメーカーオッズ（参考値）

---

# Philosophy

Featureは増やすことが目的ではない。

Featureが

「勝敗を説明できるか」

を研究し、

有効性が確認されたものだけをAIへ採用する。