
---

# 2026-09-05 第1650回 toto / WINNER 実戦前アップデート

## 0. チャット消失対策・STATE保存運用

重要な節目では、ChatGPTから提示された heredoc 形式のテキストを
Macのターミナルへそのまま貼り付けて
`TOTO_LABO_STATE.md` に保存する運用を継続する。

以前のチャットでも、
「ターミナルに貼り付けるだけで STATE.md に保存できる形式」
で状態保存を行っていた。

今後も以下を基本とする。

- 既存STATEは原則上書きしない
- 重要な更新は `cat >> TOTO_LABO_STATE.md <<'EOF'` で追記
- 追記前にバックアップを作る
- 同時に現在地点の短い `.txt` 要約も作る
- チャットが消失しても、STATEから再開できる状態を維持する

---

# 1. 第1650回 対象13試合

1. 福岡－水戸
2. 鹿島－浦和
3. 千葉－G大阪
4. 名古屋－町田
5. 神戸－長崎
6. 柏－横浜FM
7. 岡山－広島
8. 川崎F－清水
9. C大阪－東京V
10. FC東京－京都
11. 徳島－いわき
12. 山形－甲府
13. 札幌－栃木C

---

# 2. totoLABO 基本AI P(1/0/2)

No1  福岡－水戸
0.423 / 0.286 / 0.291

No2  鹿島－浦和
0.498 / 0.259 / 0.243

No3  千葉－G大阪
0.375 / 0.303 / 0.322

No4  名古屋－町田
0.336 / 0.302 / 0.361

No5  神戸－長崎
0.464 / 0.268 / 0.268

No6  柏－横浜FM
0.478 / 0.266 / 0.256

No7  岡山－広島
0.312 / 0.284 / 0.404

No8  川崎F－清水
0.474 / 0.268 / 0.258

No9  C大阪－東京V
0.461 / 0.272 / 0.267

No10 FC東京－京都
0.356 / 0.310 / 0.334

No11 徳島－いわき
0.436 / 0.280 / 0.284

No12 山形－甲府
0.497 / 0.258 / 0.244

No13 札幌－栃木C
0.383 / 0.299 / 0.318

ΣP(draw) = 約3.655

危険度・混戦度では
No10 → No4 → No3 → No13
を特に重視。

---

# 3. 市場人気率の長期統計

`toto_vote_result_history.csv`
有効試合数 11,633。

市場1番人気がホーム1:
- 全体的中率 約49.46%

市場1番人気がアウェイ2:
- 全体的中率 約44.29%

市場人気帯別で重要な結果:

## ホーム1人気

40–49%
的中率 約40.7%

50–59%
的中率 約46.1%

60–69%
的中率 約50.5%

70%以上
的中率 約62.6%

ホーム人気が70%以上で外れた場合、
引分0へ流れる割合が高くなる。

## アウェイ2人気

40–49%
的中率 約37.8%

50–59%
的中率 約43.6%

60–69%
的中率 約44.9%

70%以上
的中率 約57.7%

アウェイ2人気が40–69%帯で外れる場合、
0よりホーム1へ反転する比率がやや高い。

重要ルール:
- アウェイ人気2はホーム人気1より過信しない
- 60%台のアウェイ2でも鉄板扱いしない
- 独立したホーム側根拠がある場合、ホーム1を軽く切らない
- 0は市場統計だけで機械的に追加しない
- P0、entropy、外部情報、試合構造で判断する

第1650回では特に
No3 G大阪2人気
No4 町田2人気
のホーム1再評価に効く。

---

# 4. totoONE / 予想XI

取得済み:
`data/raw/totoone/round_1650/full_20260904_192900.json`

13/13試合あり。

予想XI
13/13。

formation
13/13。

J1についてはFansaka player powerとの対応が高精度。

過去照合では
予想XIとJリーグ/Fansaka対応は非常に高一致率。

J2 No11～13は
J1と同等のFansaka定量player powerを無理に作らない。

---

# 5. Fansaka player power

取得済み:
`data/players/fansaka_j1_player_power.csv`

主列:
`player_power_fp`

1650予想XIでJ1の戦力比較が可能。

代表的な予想XI戦力差:

No1
福岡 > 水戸
約 +9～10%

No2
鹿島 > 浦和

No3
G大阪 > 千葉
約 +13%

No4
町田 > 名古屋

No5
神戸 ≈ 長崎
神戸微上

No7
広島 > 岡山
約 +5%

No8
清水 > 川崎F
予想XI player powerでは清水優位

No10
京都 ≈ FC東京
ほぼ互角～京都微上

注意:
Fansakaは
「選手個体の質・選手力レイヤー」
として使う。

FootyStatsやJリーグStatsと単純合算しない。

---

# 6. Jリーグ公式 Stats

`get_jleague_stats.py` を2026へ変更して取得。

生成済み:

data/j1_stats_2026.csv
data/j2_stats_2026.csv
data/j3_stats_2026.csv

J1:
20クラブ × 6指標
欠損なし。

取得項目:
- score_per_game
- ball_rate
- pass_count_per_game
- sprint_per_game
- clean_sheet
- distance_per_game

J2/J3:
- score_per_game
- ball_rate
- pass_count_per_game
- clean_sheet
は使用可能。

sprint_per_game
distance_per_game
はJ2/J3でrankingListなしとなり欠損。

したがってJ2/J3は
存在する4指標だけ使用し、
欠損を捏造補完しない。

---

# 7. FootyStats

1650用FootyStats分析は
13試合について実施済み。

HTML直接取得は429/Cloudflareに当たったため、
回避は行わない。

ユーザー保存PDF:
13 H2H + 26 team PDF
合計39PDFを利用。

主に確認:
- PPG
- home/away PPG
- xG/xGA
- venue xG
- shots
- SOT
- conversion
- possession
- BTTS
- CS
- FTS
- HT
- 1H/2H
- H2H

注意:
team PDF current4/5 と
H2H page last10等の分母を混ぜない。

---

# 8. 9/5 確定スタメン監査

今日9/5開催の
No1
No11
No12
について公式スタメン確認済み。

## No1 福岡－水戸

水戸:
totoONE予想XIと 11/11一致。

福岡:
予想XIから3人変更。

OUT:
- 永石拓海
- 藤本一輝
- 碓井聖生

IN:
- 藤田和輝
- 田代雅也
- ウェリック・ポポ

Fansaka予想XI:
福岡 57.304
水戸 52.201

確定XI:
福岡 約56.544
水戸 52.201

福岡は予想比
約 -1.3%

それでも水戸より
約 +8%前後 player power優位。

結論:
大幅弱化ではない。

No1最終:
1 ≳ 2 > 0

toto買い目:
12維持。

---

## No11 徳島－いわき

徳島:
totoONE予想XIと10/11一致。

予想:
トニー・アンデルソン

確定:
渡大生

いわき:
10/11一致。

予想:
遠藤凌

確定:
藤井海和

J2なのでFansaka定量は使わず、
主力性・役割・JリーグStats・FootyStatsで判断。

JリーグStats:
徳島優位。

主な数字:
得点/試合
徳島 2.0
いわき 1.2

保持率
徳島 51.2
いわき 48.6

パス
徳島 451.3
いわき 349.5

CS
徳島 9
いわき 6

ただし:
徳島は前戦120分の疲労を考慮。

結論:
1 > 0 > 2

toto:
1維持。

---

## No12 山形－甲府

両チームとも
totoONE予想XIと11/11一致。

当日XI補正なし。

FootyStats:
山形優位。

JリーグStats:
全体として比較的互角。

totoLABO:
1=.497
0=.258
2=.244

結論:
1 >>> 0 > 2

toto:
1固定維持。

---

# 9. 第1650回 予算別買い目

## 2,400円 / 24口 最終低予算案

12 / 1 / 12 / 02 / 1 / 1 / 2 / 1 / 1 / 102 / 1 / 1 / 2

No1 12
No2 1
No3 12
No4 02
No5 1
No6 1
No7 2
No8 1
No9 1
No10 102
No11 1
No12 1
No13 2

24口 = 2,400円

2,400円での弱点:
- No8を1固定
- No13を2固定

本当はNo8 10、
No13 12または102が欲しいが、
有限予算のため削る。

---

## 4,800円 / 48口 本線

12 / 1 / 12 / 02 / 1 / 1 / 2 / 10 / 1 / 102 / 1 / 1 / 2

48口 = 4,800円

4,800円を
費用対効果の基準案とする。

---

## 7,200円 / 72口 安全強化版

12 / 1 / 102 / 02 / 1 / 1 / 2 / 10 / 1 / 102 / 1 / 1 / 2

72口 = 7,200円

4,800円との差:
No3 千葉－G大阪を
12 → 102

アウェイ2人気の長期統計を踏まえ、
No3はトリプル化価値が高い。

---

# 10. 各試合 最終方向

No1 福岡－水戸
1 ≳ 2 > 0

No2 鹿島－浦和
1 > 0 ≈ 2

No3 千葉－G大阪
2 ≈ 1 > 0
ただし三方向分裂のため高予算なら102

No4 名古屋－町田
2 > 0 > 1
ただしアウェイ人気監査上、1切りは弱点

No5 神戸－長崎
1 >> 0 > 2

No6 柏－横浜FM
1 > 2 ≈ 0

No7 岡山－広島
2 > 0 > 1

No8 川崎F－清水
1 ≈ 0 > 2
事前構造1 vs XI清水優位
10が理想

No9 C大阪－東京V
1 >> 0 > 2

No10 FC東京－京都
1 ≈ 0 ≈ 2
今回最重要トリプル
102維持

No11 徳島－いわき
1 > 0 > 2

No12 山形－甲府
1 >> 0 > 2

No13 札幌－栃木C
1 ≈ 2 > 0
2固定は低予算上の妥協
12/102候補

---

# 11. WINNER 最新オッズ

最新ユーザー保存PDF:
スポーツくじ「WINNER」
2026/09/05 17:56時点。

オッズは5分毎更新。

重要:
今後WINNER分析では
古い1:18オッズより
17:56 PDFを優先する。

---

# 12. WINNER 17:56 主な1650オッズ

## No1 福岡－水戸

福岡:
1-0 7.4
2-0 8.9
2-1 6.5
3-0 18.9
3-1 11.1
3-2 14.4
4点以上 14.3

draw:
0-0 9.8
1-1 5.2
2-2 8.4
both 3+ 23.1

水戸:
0-1 8.6
0-2 8.2
1-2 5.8
0-3 14.3
1-3 9.1
2-3 11.5
4点以上 5.1

---

## No2 鹿島－浦和

鹿島:
1-0 6.4
2-0 5.7
2-1 4.6
3-0 9.1
3-1 6.8
3-2 7.7
4+ 7.1

draw:
0-0 13.2
1-1 9.0
2-2 9.3
both3+ 16.3

浦和:
0-1 11.8
0-2 13.9
1-2 8.6
0-3 20.4
1-3 13.4
2-3 10.4
4+ 11.5

---

## No3 千葉－G大阪

千葉:
1-0 8.3
2-0 9.3
2-1 8.6
3-0 21.5
3-1 18.3
3-2 9.6
4+ 21.1

draw:
0-0 9.3
1-1 8.7
2-2 10.1
both3+ 26.0

G大阪:
0-1 6.9
0-2 5.7
1-2 5.0
0-3 8.0
1-3 6.2
2-3 12.3
4+ 6.0

---

## No4 名古屋－町田

名古屋:
1-0 10.6
2-0 10.3
2-1 8.1
3-0 21.9
3-1 15.9
3-2 18.1
4+ 18.5

draw:
0-0 11.8
1-1 5.6
2-2 8.9
both3+ 39.5

町田:
0-1 6.5
0-2 6.3
1-2 4.8
0-3 8.4
1-3 4.4
2-3 13.5
4+ 7.3

---

## No5 神戸－長崎

神戸:
1-0 4.5
2-0 3.8
2-1 4.2
3-0 6.4
3-1 6.8
3-2 11.8
4+ 7.0

draw:
0-0 12.5
1-1 9.0
2-2 12.3
both3+ 19.4

長崎:
0-1 10.0
0-2 17.0
1-2 9.7
0-3 35.5
1-3 19.2
2-3 20.1
4+ 20.8

---

## No6 柏－横浜FM

柏:
1-0 7.1
2-0 6.9
2-1 5.5
3-0 10.5
3-1 7.8
3-2 12.1
4+ 10.5

draw:
0-0 12.8
1-1 7.9
2-2 10.5
both3+ 16.8

横浜FM:
0-1 7.7
0-2 9.2
1-2 6.8
0-3 13.5
1-3 8.2
2-3 10.9
4+ 9.2

---

## No7 岡山－広島

岡山:
1-0 6.6
2-0 11.0
2-1 7.8
3-0 26.6
3-1 23.6
3-2 25.3
4+ 24.3

draw:
0-0 9.7
1-1 7.3
2-2 9.0
both3+ 37.6

広島:
0-1 5.8
0-2 4.8
1-2 5.4
0-3 6.4
1-3 6.9
2-3 14.6
4+ 5.8

---

## No8 川崎F－清水

川崎:
1-0 7.8
2-0 5.9
2-1 5.0
3-0 9.2
3-1 6.4
3-2 10.6
4+ 5.0

draw:
0-0 9.8
1-1 6.8
2-2 11.5
both3+ 16.6

清水:
0-1 7.4
0-2 11.9
1-2 8.0
0-3 22.3
1-3 15.7
2-3 18.1
4+ 19.8

---

## No9 C大阪－東京V

C大阪:
1-0 4.6
2-0 4.0
2-1 4.4
3-0 6.7
3-1 6.0
3-2 14.3
4+ 7.4

draw:
0-0 9.6
1-1 7.8
2-2 16.6
both3+ 36.8

東京V:
0-1 8.2
0-2 16.3
1-2 11.7
0-3 25.1
1-3 17.2
2-3 18.4
4+ 17.7

---

## No10 FC東京－京都

FC東京:
1-0 6.4
2-0 6.2
2-1 5.3
3-0 8.5
3-1 7.7
3-2 11.9
4+ 9.0

draw:
0-0 9.1
1-1 7.2
2-2 11.1
both3+ 30.8

京都:
0-1 6.9
0-2 8.4
1-2 6.3
0-3 14.1
1-3 13.7
2-3 17.1
4+ 15.1

---

## No11 徳島－いわき

徳島:
1-0 4.9
2-0 5.2
2-1 5.9
3-0 9.6
3-1 9.0
3-2 11.3
4+ 7.0

draw:
0-0 8.1
1-1 6.6
2-2 11.8
both3+ 27.4

いわき:
0-1 8.3
0-2 10.1
1-2 7.4
0-3 20.4
1-3 14.1
2-3 15.9
4+ 15.5

---

## No12 山形－甲府

山形:
1-0 6.2
2-0 4.3
2-1 5.0
3-0 5.4
3-1 6.7
3-2 12.9
4+ 5.5

draw:
0-0 10.4
1-1 5.9
2-2 12.9
both3+ 36.8

甲府:
0-1 9.1
0-2 12.6
1-2 8.1
0-3 32.7
1-3 25.6
2-3 27.7
4+ 24.5

---

## No13 札幌－栃木C

札幌:
1-0 5.2
2-0 4.4
2-1 4.8
3-0 7.2
3-1 6.6
3-2 10.8
4+ 7.1

draw:
0-0 14.6
1-1 9.8
2-2 9.0
both3+ 32.9

栃木C:
0-1 10.9
0-2 10.8
1-2 8.3
0-3 20.9
1-3 15.6
2-3 21.9
4+ 11.4

---

# 13. WINNER分析上の現状

現時点で
「試合評価とWINNERオッズの乖離」
を見ることは可能。

ただし
厳密なEVランキングには
score modelの校正が必要。

今の暫定EVは
正式な校正済みモデルではない。

したがって
高オッズtail betをそのまま
「優良」と断定しない。

例:
- 両チーム3点以上
- 4点以上

はλの小さな誤差に非常に敏感。

raw EVだけでなく
モデル不確実性を考慮する。

---

# 14. score model 校正プロジェクト開始

目的:

totoLABOの
P_final(1/0/2)
をベースに、

FootyStats
Jリーグ事前特徴量
home/away構造
将来的にXI power

を使って

λ_home
λ_away

を推定し、

WINNERの
exact score probability
を出す。

---

# 15. score model v1 最小構成

最初は複雑化しない。

入力候補:

- home xG
- away xG
- home xGA
- away xGA
- home GF
- away GF
- home GA
- away GA
- home PPG
- away PPG
- home/away venue PPG
- totoLABO P1
- totoLABO P0
- totoLABO P2

目的変数:

- home_score
- away_score

まず2本のPoisson regression:

home_score model
away_score model

出力:

λ_home
λ_away

---

# 16. score distribution

初期:

P(H=h,A=a)
=
Poisson(h | λ_home)
×
Poisson(a | λ_away)

0～6点程度まで作る。

そこから:

P(home win)
P(draw)
P(away win)

へ集約。

totoLABO P(1/0/2)との
整合性を確認する。

score modelは
「得点構造」。

totoLABOは
「勝敗方向」。

この2つを融合する。

---

# 17. Walk-forward検証

ランダムsplit禁止。

例:

～2021学習 → 2022予測
～2022学習 → 2023予測
～2023学習 → 2024予測
～2024学習 → 2025予測

評価:

- score log loss
- Brier score
- exact score hit rate
- top3 score coverage
- total goals calibration
- home goals calibration
- away goals calibration
- 0-0 calibration
- 1-0 calibration
- 0-1 calibration
- 1-1 calibration
- 2-1 calibration
- 1-2 calibration

---

# 18. Dixon-Coles

単純Poissonの次に
Dixon-Coles補正を導入。

特に:

0-0
1-0
0-1
1-1

の低得点セルを補正。

WINNERでは
この4スコアが重要なため、
Dixon-Colesの有効性を
walk-forwardで検証する。

必ず
「DCあり vs DCなし」
を比較する。

---

# 19. WINNER EV

校正後:

EV = P(score) × odds

ただし実運用では
raw EVだけで買わない。

候補:

- raw EV > 1.10
- shrink後EV > 1.03

などを検証する。

市場へのshrink例:

P_safe
=
0.8 × P_model
+
0.2 × P_market

ただし係数0.8/0.2は仮。
過去検証で決定する。

---

# 20. score model 実装候補

src/ml/train_score_model.py

src/ml/predict_score_distribution.py

src/evaluation/evaluate_score_calibration.py

将来的に:

src/ml/apply_dixon_coles.py

src/winner/rank_winner_ev.py

などへ分離可能。

---

# 21. score model 開発順序

STEP1
過去試合のscore training CSV作成。

STEP2
Poisson v1。

STEP3
walk-forward。

STEP4
calibration table。

STEP5
Dixon-Coles。

STEP6
totoLABO 1X2との整合補正。

STEP7
WINNERオッズ接続。

STEP8
EV ranking。

STEP9
Fansaka XI power / 当日XIを追加。

最初からXIを入れすぎない。
まずチーム事前指標だけで
score modelそのものを検証する。

---

# 22. 次の最優先タスク

最優先:

「score model用の過去学習CSVを1本作る」

必要項目:

match_id
date
season
league
home_team
away_team
home_score
away_score

＋

pre-match onlyの:

home_xG
away_xG
home_xGA
away_xGA
home_GF
away_GF
home_GA
away_GA
home_PPG
away_PPG
home_venue_PPG
away_venue_PPG
P1
P0
P2

重要:
試合後情報 leakage禁止。

---

# 23. 現在の重要原則

- totoLABO AIを主信号とする
- FootyStats MARKETは強い補助
- CORE4は警告・disagreement用
- 強制drawは禁止
- distanceはconfidenceではない
- strong source 1 vs 2 split → 0再点検
- rank / PPG / league recordは相関した情報として扱う
- XI / absence / shot contentはより独立した情報になり得る
- fatigue/travelは強弱差を圧縮し0不確実性を上げる
- special context flagは監査用
- market favorite directionを監査
- away favoriteはhome favoriteより慎重に扱う
- 予算有限ではfixed/expansion分類が最重要
- draw countを合わせるために個別確率を変更しない

---

# 24. 再開時キーワード

チャット再開時は以下を伝えればよい:

「TOTO_LABO_STATE.md の
2026-09-05 第1650回 / WINNER / score model calibration
の続きから再開」

次:
score model training dataset作成。


---

## 2026-09-05 Score model v1-A -> v1-C stacked checkpoint

### 1. score training base

Artifact:
- `data/features/score_training_v1a.csv`

Shape:
- 8,742 rows x 40 columns
- seasons 2018-2025
- completed regular J1/J2/J3 matches only

Completed rows:
- 2018: 1,040
- 2019: 1,074
- 2020: 1,074
- 2021: 1,052
- 2022: 1,074
- 2023: 1,148
- 2024: 1,140
- 2025: 1,140

Model:
- separate HOME / AWAY `PoissonRegressor`
- median imputer
- StandardScaler
- independent Poisson score matrix
- evaluation score grid 0..8
- rest days clipped at 30
- walk-forward test years 2022-2025

### 2. v1-A baseline

Artifacts:
- `data/evaluation/score_model_v1a_walkforward_predictions_2022_2025.csv`
- `data/evaluation/score_model_v1a_walkforward_summary_2022_2025.csv`
- `data/evaluation/score_model_v1a_walkforward_2022_2025.json`

alpha:
- 0.20

Overall OOF 2022-2025:
- n = 4,502
- score logloss = 2.879397
- exact score hit = 0.121057
- top3 score hit = 0.342959
- 1X2 Brier = 0.646241
- 1X2 logloss = 1.069589
- mean lambda HOME = 1.344087
- mean lambda AWAY = 1.196790

All four folds beat historical-mean Poisson baseline on both HOME and AWAY deviance.

### 3. v1-A calibration diagnostics

Aggregate 1X2:
- actual HOME = 0.406042
- predicted HOME = 0.402229
- actual DRAW = 0.264993
- predicted DRAW = 0.263316
- actual AWAY = 0.328965
- predicted AWAY = 0.334455

Main score cells:
- 0-0 pred 0.079903 / actual 0.084851
- 1-0 pred 0.105745 / actual 0.114394
- 0-1 pred 0.095073 / actual 0.105064
- 1-1 pred 0.124440 / actual 0.124167
- 2-0 pred 0.071467 / actual 0.061306
- 0-2 pred 0.057522 / actual 0.043758
- 2-1 pred 0.083189 / actual 0.091071
- 1-2 pred 0.074440 / actual 0.077521
- 2-2 pred 0.049218 / actual 0.045313

Marginal / joint:
- BTTS pred 0.508000 / actual 0.508441
- either-team clean sheet pred 0.492000 / actual 0.491559
- 0-0 underpredicted about 0.5pt
- AWAY 1 goal underpredicted and AWAY 2 goals overpredicted modestly

Decision:
- independent Poisson structure remains acceptable
- do not introduce Dixon-Coles mechanically
- observed desired 00/10/01 directions cannot be solved coherently by one classic DC rho

### 4. marginal post-hoc calibration test

Artifact:
- `data/evaluation/score_model_v1a1_marginal_calibration_2023_2025.csv`

2023-2025:
- raw score LL = 2.874585
- calibrated = 2.889716
- raw 1X2 LL = 1.069816
- calibrated = 1.069925
- raw Brier = 0.646448
- calibrated = 0.646523
- exact improved 0.120187 -> 0.122520
- top3 worsened 0.346558 -> 0.343932

Decision:
- REJECT marginal calibration
- exact-hit-only improvement is insufficient when proper scoring worsens

### 5. FootyStats temporal join

Existing FootyStats temporal artifacts:
- `data/features/training_dataset_2018_2024.csv`
- `data/features/validation_dataset_2025.csv`

Joined artifact:
- `data/features/score_training_v1b.csv`

Shape:
- 8,742 rows x 44 columns

CORE4 coverage:
- `fs_csv_pre_match_ppg_home`: 100%
- `fs_csv_pre_match_ppg_away`: 100%
- `fs_csv_home_team_pre_match_xg`: 100%
- `fs_csv_away_team_pre_match_xg`: 100%

Join:
- `jleague_match_id`
- 8,742 / 8,742
- duplicate IDs = 0
- missing CORE4 = 0

### 6. FootyStats ablation

Overall OOF 2022-2025:

v1-A:
- score LL 2.879397

v1-A + FS PPG:
- score LL 2.879493
- no value / slight degradation

v1-A + FS xG:
- score LL 2.875663
- HOME deviance 1.174417
- AWAY deviance 1.165643
- 1X2 LL 1.066335
- Brier 0.643862
- exact 0.124833
- top3 0.340515

v1-A + CORE4:
- score LL 2.875803

Decision:
- improvement is driven by FootyStats xG
- FootyStats PPG is redundant with existing J.League PPG/form information
- adopt xG-only extension

Additional aggregate FootyStats features:
- average goals
- BTTS
- O1.5
- O2.5
- O3.5

did not produce robust enough improvement to justify complexity.
Maximum feature set score LL 2.875552 versus xG-only 2.875663, but other proper metrics worsened and 2025 score LL worsened.

Decision:
- retain xG-only

### 7. alpha search for v1-Bxg

Candidate alpha:
- 0
- .01
- .03
- .05
- .10
- .20
- .30
- .50
- 1.0

Internal 2022-2024 best:
- alpha 0.50 = 2.888778

Reference:
- alpha 0.20 = 2.889634

2025 confirmation:
- alpha 0.50 = 2.835219
- alpha 0.20 = 2.834462

Decision:
- difference is tiny internally
- 0.50 fails to confirm in 2025
- keep alpha = 0.20

### 8. formal v1-Bxg model

Artifacts:
- `data/evaluation/score_model_v1bxg_walkforward_predictions_2022_2025.csv`
- `data/evaluation/score_model_v1bxg_walkforward_summary_2022_2025.csv`
- `data/evaluation/score_model_v1bxg_walkforward_2022_2025.json`

Definition:
- J.League base pre-match features
- FootyStats HOME pre-match xG
- FootyStats AWAY pre-match xG
- separate HOME/AWAY Poisson
- alpha 0.20
- independent Poisson score matrix

OOF 2022-2025:
- n 4,502
- score LL 2.875663
- 1X2 LL 1.066335
- Brier 0.643862
- exact 0.124833
- top3 0.340515
- mean lambda HOME 1.338009
- mean lambda AWAY 1.193775

By year score LL:
- 2022 2.890929
- 2023 2.872425
- 2024 2.905744
- 2025 2.834462

### 9. multisource OOF audit

Artifact:
- `data/evaluation/multisource_walk_forward_predictions_2022_2025.csv`

Shape:
- 4,502 rows x 29 columns

Coverage against v1-Bxg OOF:
- 4,502 / 4,502
- 100%
- duplicate jleague_match_id = 0
- season mismatch = 0
- ensemble probability missing = 0
- probability sum = 1 for all rows

Ensemble probability means:
- HOME 0.401910
- DRAW 0.264399
- AWAY 0.333691

Standalone ensemble 1X2:
- accuracy 0.455797
- logloss 1.058643
- Brier 0.638117

Leakage status:
- filename / dataset structure indicate walk-forward,
  but final source-code generation audit still required before production sign-off.

### 10. v1-C stacked meta model

Meta inputs:
- log(v1-Bxg HOME lambda)
- log(v1-Bxg AWAY lambda)
- log(multisource P_HOME / P_DRAW)
- log(multisource P_AWAY / P_DRAW)

Temporal meta design:
- 2023 trained on 2022 OOF
- 2024 trained on 2022-2023 OOF
- 2025 trained on 2022-2024 OOF

Meta alpha search:
- 2023-2024 internal best = alpha 0.0
- 2025 confirmation also improved strongly

Selected alpha:
- 0.0

v1-C selected performance:

2023:
- score LL 2.872425 -> 2.865141
- 1X2 LL 1.083375 -> 1.074936

2024:
- score LL 2.905744 -> 2.896973
- 1X2 LL 1.056546 -> 1.050810

2025:
- score LL 2.834462 -> 2.819464
- 1X2 LL 1.059730 -> 1.043911

Overall 2023-2025:
- v1-Bxg score LL 2.870881
- v1-C score LL 2.860537
- v1-Bxg 1X2 LL 1.066589
- v1-C 1X2 LL 1.056595
- v1-Bxg Brier 0.644189
- v1-C Brier 0.637021
- v1-Bxg exact 0.123396
- v1-C exact 0.131272
- v1-Bxg top3 0.340723
- v1-C top3 0.352684

### 11. meta ablation: recalibration vs multisource signal

Artifacts:
- `data/evaluation/score_model_v1c_meta_ablation_2023_2025.csv`
- `data/evaluation/score_model_v1c_meta_ablation_overall_2023_2025.csv`

Overall:
v1-Bxg:
- score LL 2.870881
- 1X2 LL 1.066589
- Brier 0.644189
- exact 0.123396
- top3 0.340723

recalibration only:
- score LL 2.871893
- 1X2 LL 1.067217
- Brier 0.644708
- exact 0.120770
- top3 0.343349

recalibration + multisource:
- score LL 2.860537
- 1X2 LL 1.056595
- Brier 0.637021
- exact 0.131272
- top3 0.352684

Decision:
- generic lambda recalibration does NOT explain the improvement
- recalibration-only is worse than v1-Bxg
- multisource OOF directional probabilities have genuine incremental predictive value

Coefficient signs are structurally sensible:
HOME score model:
- HOME-vs-DRAW log-ratio positive
- AWAY-vs-DRAW log-ratio negative

AWAY score model:
- HOME-vs-DRAW log-ratio negative
- AWAY-vs-DRAW log-ratio positive

Important interpretation:
- coefficient on log(base lambda) is around 0.33-0.43 once multisource enters
- therefore v1-C should be interpreted as a STACKED SCORE MODEL,
  not merely a small offset correction to v1-Bxg

Current score-model hierarchy:
1. v1-A = baseline
2. v1-Bxg = validated xG-enhanced core
3. v1-C stacked = current best candidate

Pending before production sign-off:
- inspect multisource walk-forward generation code for strict OOF / temporal leakage safety
- confirm ensemble weights and component models do not use test-season outcomes
- then generate formal production v1-C artifacts and Round 1650 score probabilities / WINNER EV


---

## 2026-09-05 Round1650 score-model production checkpoint

### FootyStats 2026 xG source issue

Initial production audit used:
- `data/features/footystats_csv_prediction_features_2026.csv`

Join itself:
- Round1650 13/13 matched
- duplicate jleague_match_id = 0
- formal missing = 0

But semantic xG audit failed:
- `fs_csv_home_team_pre_match_xg` = 0.0 for all 13
- `fs_csv_away_team_pre_match_xg` = 0.0 for all 13

Raw standard 2026 FootyStats CSVs also had all-zero pre-match xG:
- J1: 380 rows, HOME/AWAY pre-match xG all zero
- J2: 380 rows, HOME/AWAY pre-match xG all zero
- J3: 380 rows, HOME/AWAY pre-match xG all zero

Decision:
- Do NOT interpret standard 2026 xG=0 as real football xG.
- Treat standard 2026 FootyStats xG as semantically unavailable/broken for production.

Validated replacement:
- `data/features/footystats_csv_prediction_features_2026_redownload_v2.csv`

Round1650 coverage:
- 13/13
- duplicate IDs = 0
- HOME xG nonzero 13/13
- AWAY xG nonzero 13/13

Round1650 redownload-v2 xG:
1 福岡-水戸 1.29 / 1.58
2 鹿島-浦和 1.44 / 2.00
3 千葉-G大阪 0.92 / 1.48
4 名古屋-町田 2.08 / 1.84
5 神戸-長崎 1.53 / 0.57
6 柏-横浜FM 1.53 / 1.35
7 岡山-広島 1.89 / 2.25
8 川崎F-清水 1.85 / 1.46
9 C大阪-東京V 1.22 / 0.44
10 FC東京-京都 1.64 / 1.29
11 徳島-いわき 0.73 / 1.10
12 山形-甲府 2.10 / 1.34
13 札幌-栃木C 1.49 / 1.78

Production rule:
- For Round1650 score model, use
  `footystats_csv_prediction_features_2026_redownload_v2.csv`
  as the FootyStats xG source.
- Never silently fall back to the all-zero standard 2026 file.

### score_model_v1c_stacked production completed

Stage1:
- model = v1-Bxg
- training rows = 8,742
- seasons = 2018-2025
- features = J.League base pre-match + FootyStats HOME/AWAY pre-match xG
- separate HOME/AWAY PoissonRegressor
- alpha = 0.20

Stage2:
- model = stacked Poisson meta model
- meta OOF source:
  `data/evaluation/multisource_walk_forward_predictions_2022_2025.csv`
- OOF rows = 4,502
- causal walk-forward / weight-selection audit = PASS
- meta alpha = 0.0

Final meta coefficients:
HOME:
- intercept = 0.021150
- coefficients:
  - log base HOME lambda = 0.353834
  - log(P_HOME/P_DRAW) = +0.456188
  - log(P_AWAY/P_DRAW) = -0.110768

AWAY:
- intercept = 0.066137
- coefficients:
  - log base AWAY lambda = 0.478800
  - log(P_HOME/P_DRAW) = -0.174006
  - log(P_AWAY/P_DRAW) = +0.338605

Production artifacts:
- `data/predictions/score_model_v1c_stacked_toto1650.csv`
- `data/analysis/toto1650_v1c_top_scores.csv`
- `data/models/score_model_v1c_stacked_toto1650.joblib`
- `data/analysis/toto1650_score_model_v1c_report.json`

Round1650 final lambdas / 1X2:

1 福岡-水戸
- lambda 1.3166 / 1.1417
- P1/P0/P2 = 0.4062 / 0.2714 / 0.3223
- top score 1-1 = 0.1286

2 鹿島-浦和
- lambda 1.8438 / 1.0036
- P1/P0/P2 = 0.5706 / 0.2265 / 0.2030
- top score 1-1 = 0.1073

3 千葉-G大阪
- lambda 1.1447 / 1.4500
- P1/P0/P2 = 0.2984 / 0.2606 / 0.4410
- top score 1-1 = 0.1239

4 名古屋-町田
- lambda 1.1382 / 1.4201
- P1/P0/P2 = 0.3021 / 0.2632 / 0.4347
- top score 1-1 = 0.1252

5 神戸-長崎
- lambda 1.6013 / 0.8990
- P1/P0/P2 = 0.5387 / 0.2502 / 0.2111
- top score 1-0 = 0.1314

6 柏-横浜FM
- lambda 1.6540 / 0.9579
- P1/P0/P2 = 0.5371 / 0.2447 / 0.2182
- top score 1-0 = 0.1214

7 岡山-広島
- lambda 1.0595 / 1.4482
- P1/P0/P2 = 0.2764 / 0.2634 / 0.4602
- top score 1-1 = 0.1250

8 川崎F-清水
- lambda 1.5484 / 0.9988
- P1/P0/P2 = 0.5007 / 0.2551 / 0.2442
- top score 1-0 = 0.1213

9 C大阪-東京V
- lambda 1.4548 / 0.9487
- P1/P0/P2 = 0.4886 / 0.2654 / 0.2460
- top score 1-0 = 0.1315

10 FC東京-京都
- lambda 1.3005 / 1.1692
- P1/P0/P2 = 0.3958 / 0.2713 / 0.3329
- top score 1-1 = 0.1287

11 徳島-いわき
- lambda 1.4079 / 1.0005
- P1/P0/P2 = 0.4635 / 0.2689 / 0.2676
- top score 1-1 = 0.1267
- 1-0 virtually tied

12 山形-甲府
- lambda 1.8033 / 0.8152
- P1/P0/P2 = 0.6081 / 0.2266 / 0.1653
- top score 1-0 = 0.1315

13 札幌-栃木C
- lambda 1.2402 / 1.3444
- P1/P0/P2 = 0.3433 / 0.2644 / 0.3923
- top score 1-1 = 0.1258

Current score-model status:
- `score_model_v1c_stacked` = current production score model
- Round1650 production generation = PASS
- WINNER EV requires score odds; no local Round1650 odds file currently exists

---

# 2026-09-07 ROUND1650 POSTMATCH RESEARCH CHECKPOINT

## 0. 今日の研究目的

Round1650の失敗を後知恵で説明するのではなく、
2023-2025 OOFを使って、

- DRAW再点検
- favorite fragility
- fatigue
- direction failure
- venue fragility
- raw AI vs v1-C direction split
- single safety
- 有限予算portfolio

を順番に検証した。

基本方針：

- DESIGN = 2023-2024
- CONFIRM = 2025
- 2025を閾値調整に使わない
- 小標本の派手な数字は採用しない
- 1試合単位の警告が有効でも、
  有限予算totoで有効とは限らない
- probabilistic miss と bad decision を区別する
- 根拠がない敗因は UNEXPLAINED とする

---

# 1. Round1650 actual / ticket review

Actual toto outcomes:

1  0
2  2
3  1
4  2
5  1
6  2
7  1
8  1
9  0
10 1
11 1
12 2
13 2

72-ticket plan:

1  12
2  1
3  102
4  02
5  1
6  1
7  2
8  10
9  1
10 102
11 1
12 1
13 2

Ticket failures = SIX:

No1
No2
No6
No7
No9
No12

IMPORTANT:
v1-C top1 model misses = SEVEN:

No1
No2
No3
No6
No7
No9
No12

No3はv1-C top1自体は外れたが、
ticket 102でactual=1をcoverしている。

したがって、

- ticket failure = 6
- v1-C top1 failure = 7

を今後も混同しない。

---

# 2. DRAW RESEARCH UPDATE

## DRAW_RECHECK V1

Simple hard rules were tested.

Historical OOF:

baseline draw rate:
26.34%

P0 >= .27:
28.72%

top1 < .44:
27.78%

CORE:
P0 >= .27 AND top1 < .44
28.41%

SOURCE SPLITを追加したrule:
26.43%

結果：

SOURCE_SPLIT -> DRAW
は支持されなかった。

過去に使っていた、

「1と2でsourceが割れたら0再点検」

を自動ruleとして使わない。

DRAW_RECHECK_V1 hard ruleはproduction不採用。

---

## DRAW STRUCTURE V3 CONTINUOUS

DESIGN 2023-24の

- score_p_draw percentile
- draw_cell_00_11 percentile

の平均をcontinuous draw scoreとした。

Historical:

score >=75

DESIGN:
draw rate 約30.07%
baseline 26.75%
lift +3.32pt

CONFIRM:
draw rate 約28.74%
baseline 25.53%
lift +3.21pt

score >=90

DESIGN:
+4.19pt

CONFIRM:
+5.12pt

弱いが再現するsignal。

Round1650:

No1  72.38 actual 0
No10 69.60 actual 1
No11 69.19 actual 1
No9  58.46 actual 0

Interpretation:

No1:
moderate-high draw recheck。
>=75のrobust threshold直下なので、
「強いdraw rule」ではないが0を落とすには注意が必要だった。

No9:
draw scoreは58.46でmedium。
model-onlyでは強いdraw alarmではない。

No11:
69.19でもactual=1。
draw scoreはdeterministicではない。

Artifacts:

data/evaluation/draw_structure_v3_continuous_audit_2023_2025.csv
data/analysis/toto1650_draw_structure_v3_continuous_scoring.csv

---

# 3. FAVORITE CALIBRATION

v1-C OOF 3428:

favorite >= .55
n=233
actual accuracy=.6567
mean prediction=.5869

>= .58
n=113
accuracy=.6903

>= .60
n=66
accuracy=.7424

Conclusion:

55-65% favorite全体は
overconfidentではない。

むしろ多くのbandで実績の方が予測より高い。

したがって、

「60% favoriteは危険なので弱める」

というglobal ruleは棄却。

No12が負けたことを理由に
strong favorite全体を弱めない。

---

# 4. FAVORITE FRAGILITY

## V2

source dispersion中心のfragilityは
十分な再現性なし。

V2 production rejected。

---

## V3/V4 COMPOSITE

55-65% favoriteの内部で
fragilityを検証。

Round1650と同じ形で使える
six-flag version:

EARLY
XG_BIG_ADV
VENUE_DEF_WEAK
REST_NOT_BETTER
LOAD7_NOT_BETTER
RECENT_DEF_WEAK

Historical six-flag:

DESIGN baseline failure:
32.46%

count >=3:
40.00%

count >=4:
57.69%

CONFIRM baseline:
35.24%

count >=3:
41.67%

count >=4:
52.63%

ALL:

baseline:
33.79%

>=3:
40.74%

>=4:
55.56%

55-65% favorite限定では
>=4がかなり有望。

Round1650:

No2:
top1=.5706
flags=3
actual=2

No12:
top1=.6081
flags=4
actual=2

No12は
COMPOSITE_FAVORITE_FRAGILITY
candidateとして強い。

---

## SINGLE SAFETY V2での正しい帯内比較

55-65% favorite:

DESIGN
ALL        n114 accuracy .6754
NOT_FRAG   n77  accuracy .7792
FRAG>=4    n37  accuracy .4595

CONFIRM
ALL        n105 accuracy .6476
NOT_FRAG   n71  accuracy .6761
FRAG>=4    n34  accuracy .5882

ALL
ALL        n219 accuracy .6621
NOT_FRAG   n148 accuracy .7297
FRAG>=4    n71  accuracy .5211

重要：

FAVORITE_FRAGILEは
同じ55-65%帯の内部でsingle安全度を分ける。

ただし後述の有限予算portfolioでは
FRAGILE -> automatic double
は改善しなかった。

よって：

FAVORITE_FRAGILE>=4
= 有望warning

だが

automatic single prohibition
ではない。

---

# 5. FATIGUE CONTEXT V1

simple historical features:

REST_ADV_LOW
LOAD7_ADV_LOW
LOAD14_ADV_LOW
REST_DAYS_LOW
MATCHES7_HIGH
MATCHES14_HIGH

をOOF検証。

結果：

favorite/top1 failureにも
drawにも
安定したpositive liftなし。

CONFIRMでも再現しなかった。

mean fatigue countは
FAIL側の方がむしろ少ないケースもある。

Conclusion:

simple fatigue hypothesis rejected。

「疲労だからfavorite failure」
「疲労だからdraw」
をprimary causal explanationとして使わない。

Round1650:

No6の旧primary
FATIGUE_CONTEXT_UNDERWEIGHTED
は撤回/降格。

No9もfatigueをprimaryにしない。

疲労・暑さ・unchanged XI等の
rich contextはaudit-only。
historical representationができるまで
causal rule化しない。

Artifacts:

data/evaluation/fatigue_context_v1_audit_2023_2025.csv
data/evaluation/fatigue_context_v1_summary_2023_2025.csv

---

# 6. DIRECTION FAILURE V1

OOF 3428で
top1 HIT vs FAILを比較。

安定した方向：

FAIL側では

- top1_prob低い
- raw_top1_prob低い
- recent5_ppg_adv低い
- fs_xg_adv低い
- recent5_def_adv低い
- venue_ppg_adv低い
- venue_def_adv低い
- season_ppg_adv低い

傾向。

effect sizeは大きくない。

---

## RAW AI vs v1-C DIRECTION SPLIT

重要な再現signal。

DESIGN 2023-24:

SAME:
n=2107
failure=.5529

SPLIT:
n=181
failure=.6796

CONFIRM 2025:

SAME:
n=1056
failure=.5227

SPLIT:
n=84
failure=.6667

ALL:

SAME:
n=3163
failure=.5428

SPLIT:
n=265
failure=.6755

Conclusion:

raw multisource top1 と v1-C top1 が違う試合は
v1-C top1 failureが明確に高い。

ただし、

RAWを自動優先するruleではない。

使用法：

RAW-v1C SPLIT
= mandatory expansion/single audit warning candidate。

Artifacts:

data/evaluation/direction_failure_v1_audit_2023_2025.csv
data/evaluation/direction_failure_v1_summary_2023_2025.csv
data/evaluation/direction_failure_v1_threshold_diagnostics_2023_2025.csv

---

# 7. Round1650 RAW vs v1-C SPLIT

Round1650 split matches:

No3:
RAW top1=1 .3746
v1-C top1=2 .4410
actual=1

RAW correct / v1-C wrong。
ticket=102なので実戦ではcover成功。

No13:
RAW top1=1 .3832
v1-C top1=2 .3923
actual=2

RAW wrong / v1-C correct。
ticket=2で成功。

split total=2。

重要：

Round1650のSIX ticket failures

No1
No2
No6
No7
No9
No12

には

RAW-v1C SPLIT = ZERO。

したがってRound1650の6敗原因を

「stackingがraw directionを壊した」

とは説明しない。

Artifact:

data/analysis/toto1650_raw_vs_v1c_direction_split.csv

---

# 8. Round1650 DIRECTION SUPPORT

Historical DESIGN-fixed Q25 warningsを
Round1650にscoring。

No6 柏-横浜FM:

v1-C top1=1
prob=.5371
actual=2

season_ppg_adv=+1.50
venue_ppg_adv=+1.50
venue_def_adv=0.00
recent5_ppg_adv=+1.80
recent5_def_adv=+1.00
fs_xg_adv=+0.18
RAW-v1C split=False
direction_warning_count=0

Conclusion:

No6は簡単なdirection weaknessでは説明できない。

疲労hypothesisもreject済み。

現在primary:

UNEXPLAINED_DIRECTION_FAILURE
または
PROBABILISTIC_LOSS

無理に原因を作らない。

---

No7 岡山-広島:

v1-C top1=2
prob=.4602
actual=1

season_ppg_adv=+1.00
venue_ppg_adv=0.00
venue_def_adv=-0.50
recent5_ppg_adv=+0.80
recent5_def_adv=+0.40
fs_xg_adv=+0.36

warnings:

LOW_venue_ppg_adv
LOW_venue_def_adv

count=2

No7はNo6とは異なり
venue方向の裏付けが弱かった。

Artifact:

data/analysis/toto1650_direction_failure_scoring.csv

---

# 9. VENUE FRAGILITY V1

No7型をhistorical OOFで検証。

VENUE_NONPOS_AND_DEF_NEG:

venue_ppg_adv <= 0
AND
venue_def_adv < 0

DESIGN:
n=339
failure=.5959
baseline=.5629
lift +.0329

CONFIRM:
n=159
failure=.6038
baseline=.5333
lift +.0704

ALL:
n=498
failure=.5984
baseline=.5531
lift +.0453

再現あり。

---

## NO7-LIKE ZONE

venue_ppg_adv <= 0
AND
venue_def_adv <= -0.5

DESIGN:
n=172
failure=.6221
baseline=.5629
lift +.0592

CONFIRM:
n=76
failure=.6184
baseline=.5333
lift +.0851

ALL:
n=248
failure=.6210
baseline=.5531
lift +.0679

Conclusion:

No7のvenue weaknessは
post-hoc storyだけではなく、
historical OOFでも再現。

ただしconfidence band 44-50では
incremental liftは小さい。

よってNo7のより正確な解釈：

「広島2予測そのものが異常」
ではなく、

46%しかないweak top1で、
さらにvenue supportも弱いのに
single 2としたことが脆かった。

Current primary candidate:

WEAK_SINGLE + VENUE_FRAGILITY

DERBY_CONTEXTはsecondary / unvalidated。

Artifacts:

data/evaluation/venue_fragility_v1_audit_2023_2025.csv
data/evaluation/venue_fragility_v1_summary_2023_2025.csv

---

# 10. SINGLE SAFETY V1

candidate warnings:

LOW_TOP1
LOW_RAW_TOP1
RAW_V1C_SPLIT
VENUE_FRAGILE
DRAW_HIGH
FAVORITE_FRAGILE

Broad warning count exact historical:

ALL 2023-25

0 warnings:
n1787 accuracy .4841

1:
n690 accuracy .4710

2:
n433 accuracy .4065

3:
n348 accuracy .3276

4:
n154 accuracy .3182

5:
n16 accuracy .1875

2023-24 / 2025とも概ね同方向。

Interpretation:

warning 2以上、
特に3以上では
top1 single reliabilityが低下。

ただしLOW_TOP1等を含むため、
probabilityそのものとの重複がある。

単純warning countだけでproduction ruleにしない。

---

Individual warnings failure lift:

RAW_V1C_SPLIT:
DESIGN +11.66pt
CONFIRM +13.33pt

LOW_RAW_TOP1:
DESIGN +7.87pt
CONFIRM +10.47pt

LOW_TOP1:
DESIGN +5.94pt
CONFIRM +11.20pt

DRAW_VHIGH:
DESIGN +7.38pt
CONFIRM +9.57pt

DRAW_HIGH:
DESIGN +6.52pt
CONFIRM +8.48pt

VENUE_FRAGILE:
DESIGN +3.29pt
CONFIRM +7.04pt

これらはsingle-risk warningとして保持。

---

# 11. SINGLE SAFETY V2 — incremental value

General strong warnings:

RAW_V1C_SPLIT
VENUE_FRAGILE
DRAW_VHIGH

を同一probability threshold内で比較。

P>=.44:

DESIGN
prob only accuracy .5061
no strong warning .5120
lift +.0059

CONFIRM
prob only .5578
no warning .5630
lift +.0052

小さいがsame direction。

P>=.50:

DESIGN
.6126 -> .6180
+0.54pt

CONFIRM
.6277 -> .6267
-0.10pt

再現なし。

P>=.55:

DESIGN
.6754 -> .6847

CONFIRM
.6387 -> .6441

ただしwarned nが極小。

P>=.60:

警告対象なし。

Conclusion:

general strong warning filterは
probability以上のincremental valueが小さい。

「warningなし = single safe」
という万能filterにはしない。

---

# 12. TOTO HISTORY STRUCTURE AUDIT

File:

toto_vote_result_history.csv

shape:
11641 x 17

rounds:
901

hold_cnt_id:
198 - 1637

13-match rounds:
853

non-13 rounds:
48

duplicate
(hold_cnt_id, match_no):
0

score/result mismatch:
0

result includes:
1 / 0 / 2 / 中止

13試合portfolioでは
complete 13-match roundsのみ使用。

Artifact:

data/evaluation/toto_history_round_structure_audit.csv

---

# 13. OOF -> TOTO LINKAGE

Initial conservative matching:

MM/DD
+
normalized home team
+
normalized away team

result/scoreはlinkage keyに使わず
post-link audit only。

OOF 3428:

UNIQUE:
1481

UNMATCHED:
1890

AMBIGUOUS:
57

UNIQUE内 result audit:

True:
1475

False:
6

Falseはtoto history側に年がないため
別年同月日カードへ誤linkしたもの。

これを理由に
match-level UNIQUE全部を信用しない。

---

# 14. STRICT CLEAN PORTFOLIO DATASET

完全13試合かつ
全13件 result audit=True のroundのみ採用。

Result:

strict clean rounds:
61 / 61 candidate rounds

2023:
20 rounds

2024:
20 rounds

2025:
21 rounds

Total:
61 rounds
793 matches

DESIGN:
40 rounds
520 matches

CONFIRM:
21 rounds
273 matches

Integrity:

duplicate jleague_match_id = 0
duplicate round/match_no = 0
all groups exactly13 = True
probability sums exactly1.0

Artifacts:

data/evaluation/portfolio_oof_clean_matches_2023_2025.csv
data/evaluation/portfolio_oof_clean_rounds_2023_2025.csv

これは現在のfinite-budget portfolio OOF母集団。

---

# 15. PORTFOLIO SIMULATION V1

Budgets:

24
48
72
144 combinations

Policies:

BASELINE
= v1-C probability onlyで
model-covered probabilityを最大化。

FAV_PROTECT
= FAVORITE_FRAGILEをsingle禁止。

STRONG_PROTECT
= FAVORITE_FRAGILE
+ RAW_V1C_SPLIT
+ DRAW_VHIGH
+ VENUE_FRAGILE
をsingle禁止。

IMPORTANT:

Safety警告をhard constraintとして評価。

---

## CONFIRM 2025 — primary decision

BASELINE:

24:
mean covered 8.0476
13/13 0
12+ 1
11+ 1

48:
mean 8.3810
13/13 0
12+ 1
11+ 2

72:
mean 8.6667
13/13 0
12+ 1
11+ 2

144:
mean 8.8571
13/13 0
12+ 1
11+ 3

---

## FAV_PROTECT minus BASELINE — CONFIRM

24:
d13 0
d12+ 0
d11+ +1
mean -0.0476

48:
0 / 0 / 0
mean -0.0476

72:
0 / 0 / 0
mean -0.0952

144:
d13 0
d12+ +1
d11+ 0
mean +0.0476

Conclusion:

FAVORITE_FRAGILE -> automatic double
はportfolioで明確な改善なし。

hard rule不採用。

warningとして保持。

---

## STRONG_PROTECT minus BASELINE — CONFIRM

24:
d13 0
d12+ 0
d11+ +1
mean -0.0476

48:
0 / 0 / 0
mean -0.1905

72:
0 / 0 / 0
mean -0.2857

144:
d13 0
d12+ +1
d11+ -1
mean -0.0952

Protection relaxed rounds:

24:
9 / 21

48:
4 / 21

72:
4 / 21

144:
1 / 21

Conclusion:

STRONG_PROTECTはhard protectionとして重すぎる。

有限予算で他試合のmarksを奪い、
CONFIRMで平均coverageを悪化させる。

STRONG_PROTECT hard rule REJECTED。

---

# 16. IMPORTANT INTERPRETATION

今回の研究で区別すべきこと：

「warningが1試合単位でfailureを予測する」

と

「warning試合を強制doubleにすると
13試合toto全体が改善する」

は別。

前者は複数signalで支持された。

後者は今回支持されなかった。

したがって、

RAW_V1C_SPLIT
DRAW_VHIGH
VENUE_FRAGILE
FAVORITE_FRAGILE

は

single-risk / expansion-priority information

として保持するが、

automatic double
automatic single prohibition

には使わない。

---

# 17. Round1650 FAILURE CLASSIFICATION — CURRENT

No1 福岡-水戸 actual0

Primary:
DRAW_STRUCTURE_UNDERWEIGHTED
+
DECISION_ALLOCATION

Notes:

draw score 72.38。
robust >=75 threshold直下。
simple SOURCE_SPLIT->DRAWはreject済み。

ticket 12で0を除外。

---

No2 鹿島-浦和 actual2

Primary:

WARNING_NOT_CONVERTED_TO_MARKS

Prematch late reviewで
鹿島1安全度をdowngradeし
0/2再点検対象にしていたが
ticketは1のまま。

favorite fragility flags=3。
V4補助signalだがprimaryにしない。

---

No6 柏-横浜FM actual2

Primary:

UNEXPLAINED_DIRECTION_FAILURE
/
PROBABILISTIC_LOSS

Reason:

direction warnings=0
raw-v1C split=False
season/venue/recent supportは強い
fatigue simple OOF rejected

無理に原因を作らない。

旧
FATIGUE_CONTEXT_UNDERWEIGHTED
をprimaryから撤回。

---

No7 岡山-広島 actual1

Primary:

WEAK_SINGLE
+
VENUE_FRAGILITY

v1-C top1=2 .4602

venue_ppg_adv=0
venue_def_adv=-0.5

No7-like historical zone:

DESIGN failure .6221
CONFIRM .6184

venue signalは再現。

ただしportfolioで
VENUE_FRAGILE -> automatic double
は改善せず。

DERBYはsecondary / unvalidated。

---

No9 C大阪-東京V actual0

Primary:

DRAW_MISSED
+
WEAK_SINGLE

v1-C home=.4886
draw score=58.46

model-only draw warningはmedium。

fatigue primaryは撤回。

tactical/context explanationは
qualitative / unvalidatedのまま。

---

No12 山形-甲府 actual2

Primary candidate:

COMPOSITE_FAVORITE_FRAGILITY

v1-C home=.6081

sixflag count=4。

55-65帯内historicalでは
fragility>=4が明確に低accuracy。

ただしfinite-budget testで

FRAGILE -> automatic double

は改善しなかった。

したがって、

「1固定が絶対に間違いだった」
とは断定しない。

正確には：

strong pre-match warning existed,
but hard protection is not validated。

---

# 18. CURRENT RULE STATUS

## KEEP / PROMISING WARNINGS

RAW_V1C_SPLIT
- strong individual OOF warning
- not automatic override

DRAW_STRUCTURE continuous
- >=75 weak reproducible
- >=90 stronger
- not automatic 0

VENUE_FRAGILE
- reproducible moderate warning
- not automatic double

FAVORITE_FRAGILE >=4 within 55-65
- strong band-internal separation
- not automatic double

LOW_TOP1
LOW_RAW_TOP1
- useful single-risk context

---

## REJECTED / DOWNGRADED

SOURCE_SPLIT -> DRAW
REJECTED

DRAW_RECHECK hard V1
NOT PRODUCTION

global FAVORITE_OVERCONFIDENCE
REJECTED

FAVORITE_FRAGILITY V2 source dispersion
REJECTED

simple FATIGUE_CONTEXT
REJECTED

STRONG_PROTECT hard single prohibition
REJECTED

FAVORITE_FRAGILE -> automatic double
NOT SUPPORTED

VENUE_FRAGILE -> automatic double
NOT SUPPORTED

---

# 19. KEY MODELING LESSON

Current major lesson:

「誰が一番勝ちそうか」

と

「どの試合を広げるべきか」

は別問題。

しかし、

single-risk warningを
hard protectionにすると
finite budgetでは他試合を犠牲にして
全体性能が落ちうる。

したがって次は、

SINGLE SAFETY hard rule

ではなく、

EXPANSION PRIORITY

として使う。

---

# 20. NEXT RESEARCH START POINT

NEXT:

EXPANSION PRIORITY V1

Goal:

BASELINEの確率ベース拡張価値を中心に残し、

warningを

「強制double」

ではなく

「同程度の候補間で拡張順位を少し上げるbonus」

として使用。

Candidate warning inputs:

RAW_V1C_SPLIT
DRAW_VHIGH
VENUE_FRAGILE
FAVORITE_FRAGILE
possibly DRAW_HIGH
LOW_TOP1 / LOW_RAW_TOP1

IMPORTANT:

bonus magnitudeは
DESIGN 2023-24だけで決める。

CONFIRM 2025は完全holdout。

Primary evaluation:

same budgets
24 / 48 / 72 / 144

13/13 primary
12+ secondary
11+ secondary
mean covered supporting

Safety gain must exceed marks displaced elsewhere。

---

# 21. CURRENT PRODUCTION PHILOSOPHY

Do not promote a warning just because
Round1650 would have been saved.

Need:

historical OOF
+
DESIGN/CONFIRM reproducibility
+
finite-budget portfolio improvement

before production promotion。

Unknown failures remain unknown。

Success and failure cases both accumulate
as toto LABO assets。

Round1652では、
Round1650の失敗を単純なhard rulesにせず、
拡張順位の精度として活かす。


---

# 2026-09-07 ROUND1653 FOOTYSTATS PDF FIRST PASS

## 0. Source

Round1653 FootyStats PDFs:

13 matches
x 3 PDFs each:

- home
- away
- H2H

Total:
39 PDFs

IMPORTANT:

This section is based only on the FootyStats PDFs.
It does NOT yet include:

- totoLABO AI
- v1-C
- totoONE
- official vote rates
- predicted XI
- injuries / suspensions
- late news

Do not treat this as final prediction.

---

# 1. Round1653 official match order

1 水戸 - 川崎F
2 清水 - 福岡
3 G大阪 - FC東京
4 町田 - 横浜FM
5 長崎 - 名古屋
6 広島 - C大阪
7 東京V - 千葉
8 浦和 - 岡山
9 今治 - 鳥栖
10 いわき - 横浜FC
11 八戸 - 湘南
12 甲府 - 磐田
13 秋田 - 徳島

---

# 2. FootyStats strongest directional agreement

## No5 長崎 - 名古屋

FootyStats direction:
HOME 1

Key venue structure:

長崎 home PPG = 1.33
名古屋 away PPG = 0.00

長崎 home xG = 1.55
名古屋 away xG = 0.94

長崎 home xGA = 1.51
名古屋 away xGA = 1.82

Current status:

FOOTYSTATS_SINGLE_CANDIDATE

Need AI / XI confirmation before final single.

---

## No6 広島 - C大阪

FootyStats direction:
HOME 1

Key venue structure:

広島 home PPG = 2.33
C大阪 away PPG = 0.00

広島 home GF = 2.33
C大阪 away GF = 0.00

広島 home GA = 0.33
C大阪 away GA = 2.00

広島 home xG = 2.05
C大阪 away xG = 1.21

広島 home xGA = 1.10
C大阪 away xGA = 1.49

Current status:

STRONGEST_FOOTYSTATS_SINGLE_CANDIDATE

Need AI / XI confirmation.

---

## No9 今治 - 鳥栖

FootyStats direction:
AWAY 2

今治 recent:
LLLLD

今治 home PPG = 0.00
鳥栖 away PPG = 1.00

今治 xG = 1.38
鳥栖 xG = 1.55

今治 xGA = 1.34
鳥栖 xGA = 1.18

Current status:

FOOTYSTATS_AWAY_SINGLE_CANDIDATE

But away win rate is not dominant enough for automatic single.

---

# 3. FootyStats dangerous single candidates

## No1 水戸 - 川崎F

Result indicators favor 水戸:

水戸 home PPG = 1.67
川崎F away PPG = 0.67

But content indicators favor 川崎F:

水戸 xG = 1.29
川崎F xG = 1.53

水戸 xGA = 1.85
川崎F xGA = 1.60

H2H:
4 matches
水戸 0 wins
川崎F 2 wins
draw 2

BTTS = 100%

Status:

HIGH_CONTRADICTION
DRAW_RECHECK
SINGLE_DANGER

---

## No3 G大阪 - FC東京

G大阪 home PPG = 2.00
FC東京 away PPG = 1.67

But content:

G大阪 xG = 1.40
FC東京 xG = 1.70

G大阪 xGA = 1.88
FC東京 xGA = 1.13

Status:

RESULT_VS_CONTENT_SPLIT
SINGLE_DANGER
AWAY_EXPANSION_RECHECK

---

## No7 東京V - 千葉

東京V home PPG = 0.25
千葉 away PPG = 0.00

東京V xG = 0.95
千葉 xG = 1.15

東京V xGA = 1.97
千葉 xGA = 2.06

Both sides weak.

Status:

HIGH_UNCERTAINTY
DRAW_RECHECK
SINGLE_DANGER

---

## No8 浦和 - 岡山

Result form favors 浦和.

But venue content:

浦和 xG = 1.29
岡山 xG = 1.70

浦和 xGA = 2.06
岡山 xGA = 1.10

Status:

RESULT_VS_CONTENT_SPLIT
SINGLE_DANGER
AWAY_RECHECK

---

## No10 いわき - 横浜FC

いわき home PPG = 1.50
横浜FC away PPG = 1.50

xG:
1.78 vs 1.87

xGA:
1.53 vs 1.60

Very close.

Status:

THREE_WAY_RISK
DRAW_RECHECK
SINGLE_DANGER

---

## No12 甲府 - 磐田

甲府 home PPG = 2.00
磐田 away PPG = 1.50

But content:

甲府 xG = 1.16
磐田 xG = 1.53

甲府 xGA = 1.64
磐田 xGA = 1.28

Status:

RESULT_VS_CONTENT_SPLIT
SINGLE_DANGER
DRAW_SECONDARY_RECHECK

---

# 4. Draw recheck candidates from FootyStats

Primary:

No1 水戸 - 川崎F
No7 東京V - 千葉
No10 いわき - 横浜FC
No13 秋田 - 徳島

Secondary:

No12 甲府 - 磐田

---

## No13 秋田 - 徳島

秋田 home PPG = 1.33
徳島 away PPG = 0.00

xG:
1.33 vs 1.34

xGA:
1.85 vs 1.60

H2H:
8 matches

秋田 wins = 2
徳島 wins = 1
draws = 5

Average goals:
1.38

BTTS:
38%

Status:

LOW_SCORING_DRAW_RECHECK
1/0 candidate before AI integration

---

# 5. Other matches

## No4 町田 - 横浜FM

町田 home PPG = 3.00
横浜FM away PPG = 2.00

町田 xG = 1.57
横浜FM xG = 1.38

町田 xGA = 1.50
横浜FM xGA = 1.56

Status:

HOME_LEAN
but 横浜FM away strength is meaningful.

Current preliminary:
1 center
2 expansion candidate

---

## No11 八戸 - 湘南

八戸 home PPG = 2.00
湘南 away PPG = 1.67

八戸 xG = 1.66
湘南 xG = 1.12

八戸 xGA = 1.32
湘南 xGA = 1.60

FootyStats venue content favors 八戸.

Status:

FOOTYSTATS_HOME_LEAN
CATEGORY_STRENGTH_CONFLICT_RECHECK

Do not override using team reputation alone.

---

# 6. Round1653 preliminary FootyStats classification

Single candidates:

No5 1
No6 1
No9 2

Danger single / expansion priority:

No1
No3
No7
No8
No10
No12

Draw recheck:

No1
No7
No10
No13

Secondary draw recheck:

No12

Moderate directional lean:

No4 -> 1 center / 2 recheck
No11 -> 1 lean / external strength recheck

---

# 7. Important methodological rule

Round1650 portfolio research showed:

A warning can predict higher single failure
WITHOUT improving the total toto portfolio
when forced into automatic doubles.

Therefore Round1653:

DO NOT use

warning -> automatic double

Instead use warnings as:

EXPANSION PRIORITY BONUS

The probability model remains primary.

---

# 8. NEXT

Next task:

EXPANSION PRIORITY V1

Need to combine:

- totoLABO AI P(1/0/2)
- v1-C
- FootyStats PDF warnings
- DRAW STRUCTURE
- RAW-v1C SPLIT
- VENUE FRAGILITY
- FAVORITE FRAGILITY
- totoONE / XI
- official vote rates

Goal:

rank expansion value
without hard-protecting every warning match.


---

# TOTO LABO LIVE TRACK RECORD DEFINITION

TOTO LABO LIVE START:
Round 1644

Important distinction:

- Round1644以降
  = toto LABO live prediction / live decision history

- 2023-2025 OOF / 61 strict-clean rounds
  = historical research / backtest only
  = NOT live toto LABO performance

今後、実戦成績とhistorical backtestを混同しない。


## Round1653 morning checkpoint

### Pipeline status
- Official toto Round1653 card registered in `toto_matches`: 13/13 PASS.
- J.League pre-match feature regenerated leak-safe for prediction-season 2026.
- Created:
  - `data/features/jleague_pre_match_features_toto1653.csv`
  - rows = 8785 = r26 base 8772 + Round1653 target 13.
- Round1653 target J.League IDs confirmed 13/13.

### FootyStats prediction feature source
- `data/features/footystats_csv_prediction_features_2026.csv`
  - Round1653 xG columns: 13/13 all zero -> DO NOT USE for 1653 RAW generation.
- `data/features/footystats_csv_prediction_features_2026_redownload_v2.csv`
  - Round1653 target = 13/13
  - xG nonzero = 13/13
  - used explicitly for Round1653 RAW multisource prediction.

### Round1653 RAW multisource AI
Generated:
- `data/predictions/multisource_premarket_predictions_2026_toto1653.csv`
- `data/models/multisource_premarket_model_2026_toto1653.joblib`
- `data/reports/multisource_premarket_report_2026_toto1653.json`

Source weights:
- FootyStats = 0.00
- Team2 = 0.20
- J.League = 0.10
- Elo = 0.70

RAW top1:
1. 水戸 1: 35.59 / 31.16 / 33.25
2. 清水 1: 39.21 / 29.68 / 31.11
3. G大阪 1: 43.22 / 28.14 / 28.64
4. 町田 1: 44.14 / 27.88 / 27.98
5. 長崎 1: 47.00 / 26.71 / 26.28
6. 広島 1: 49.30 / 25.83 / 24.88
7. 東京V 1: 38.81 / 29.77 / 31.42
8. 浦和 1: 47.68 / 26.47 / 25.85
9. 今治 1: 39.32 / 29.52 / 31.16
10. いわき 1: 42.95 / 28.11 / 28.94
11. 八戸 1: 40.76 / 28.99 / 30.25
12. 磐田 2: 34.15 / 30.34 / 35.51
13. 徳島 2: 32.74 / 29.63 / 37.63

RAW prediction count:
- 1 = 11
- 0 = 0
- 2 = 2

### Official toto market snapshot
Source:
- `data/current_toto_1653.csv`

Market top:
1 川崎F 2
2 清水 1
3 FC東京 2
4 町田 1
5 名古屋 2
6 広島 1
7 東京V 1
8 浦和 1
9 鳥栖 2
10 横浜FC 2
11 湘南 2
12 磐田 2
13 徳島 2

SOURCE_SPLIT:
- No1, No3, No5, No9, No10, No11

Reminder:
- SOURCE_SPLIT is a warning / recheck signal only.
- Do NOT use it as an automatic expansion or market-override rule.

### FootyStats v2 extraction
Archive:
- `1653_v2.zip`
- 39 real PDFs = 13 matches x home/away/H2H.
- Extracted with `pdftotext`; OCR not needed.

Saved:
- `data/analysis/footystats_1653_v2_core_extracted.csv`

CORE6 complete 13/13:
- home venue PPG
- away venue PPG
- home xG
- away xG
- home xGA
- away xGA

H2H complete 13/13.

Important FootyStats v2 structures:
- No6 広島-C大阪:
  PPG 2.33 vs 0.00 / xG 2.05 vs 1.21 / xGA 1.10 vs 1.49 / H2H 18-5-6
  -> strong 広島1 direction.
- No9 今治-鳥栖:
  PPG 0.00 vs 1.00 / xG 1.39 vs 1.82 / xGA 1.55 vs 1.23
  -> 鳥栖2 direction.
- No10 いわき-横浜FC:
  PPG 1.50 vs 1.50 / xG 1.78 vs 1.90 / xGA 1.53 vs 1.65
  -> close match; single dangerous.
- No11 八戸-湘南:
  PPG 2.00 vs 1.67 / xG 1.09 vs 1.11 / xGA 1.45 vs 1.57
  -> nearly even by FootyStats; prior “八戸 content clearly superior” withdrawn.
- No12 甲府-磐田:
  PPG 2.00 vs 1.50 / xG 1.16 vs 1.39 / xGA 1.64 vs 1.33
  -> results-home / content-away split.
- No13 秋田-徳島:
  PPG 1.33 vs 0.00 / xG 1.10 vs 0.80 / xGA 2.14 vs 1.71 / H2H draw 5/8
  -> 秋田 result-side strength but draw/徳島 defensive caution.

### Integrated Round1653 diagnostics
Saved:
- `data/analysis/toto1653_ai_market_footystats_integrated.csv`

SOURCE_SPLIT:
- No1, No3, No5, No9, No10, No11

DRAW_RECHECK:
- No1, No2, No7, No9, No12, No13

Current provisional classification:
- Strong FIX candidate:
  - No6 広島 1
- FIX candidate:
  - No4 町田 1
- FIX-lean but caution:
  - No8 浦和 1
- Expansion priority:
  - No1, No5, No9, No10, No11, No12
- Draw recheck:
  - No1, No2, No7, No9, No12, No13

Interpretation notes:
- No5: AI + FootyStats favor 長崎1, market strongly favors 名古屋2 -> major unresolved conflict.
- No9: AI favors 今治1, while market + FootyStats favor 鳥栖2 -> AI is isolated.
- No10: AI favors いわき1, market strongly 横浜FC2, FootyStats close -> major conflict.
- No11: AI favors 八戸1, market strongly 湘南2, FootyStats nearly even, H2H 0-0-3 -> major conflict.
- No12: AI almost three-way, FootyStats result/content split, H2H strongly 磐田 -> expansion/draw priority.
- No13: AI and market both slightly 徳島2, but draw probability is high and H2H draw-heavy -> draw recheck.

### Next session
Priority:
1. Recheck latest external pre-match information for No5, No9, No10, No11, No12.
2. Confirm suspensions / injuries / expected XI / rotation / manager comments.
3. Then classify final FIX vs EXPANSION.
4. After that run finite-budget portfolio optimization, keeping BASELINE probability optimization as production policy.
5. Expansion Priority V2 remains research-only tie-breaker; do not promote to production automatically.


## Round1653 2026-09-10 AM checkpoint

### Latest toto market
- No1 水戸-川崎F: 25.98 / 23.14 / 50.88
- No2 清水-福岡: 40.86 / 31.60 / 27.54
- No3 G大阪-FC東京: 29.85 / 23.31 / 46.84
- No4 町田-横浜FM: 64.11 / 16.88 / 19.01
- No5 長崎-名古屋: 23.02 / 20.57 / 56.41
- No6 広島-C大阪: 70.33 / 15.97 / 13.70
- No7 東京V-千葉: 46.81 / 27.91 / 25.28
- No8 浦和-岡山: 61.75 / 17.93 / 20.32
- No9 今治-鳥栖: 14.01 / 15.92 / 70.07
- No10 いわき-横浜FC: 12.09 / 13.10 / 74.81
- No11 八戸-湘南: 14.99 / 17.59 / 67.42
- No12 甲府-磐田: 26.28 / 22.72 / 51.00
- No13 秋田-徳島: 30.68 / 30.96 / 38.36

### Current classification
FIX strong:
- No6=1
- No8=1

FIX / strong lean:
- No4=1
- No9=2
- No12=2

Expansion priority:
- No11
- No10
- No3
- No5

Draw / close-game caution:
- No1
- No2
- No7
- No13

### MARKET 5% sensitivity findings
- No3: market-side 2 increases modestly
- No5: market-side 2 increases meaningfully
- No10: 2 becomes stronger than 1
- No11: 2 becomes stronger than 1, draw remains secondary
- MARKET5 portfolio costs only about 0.7-1.1% pure-v1C coverage across tested budget sizes
- Treat MARKET5 as warning/sensitivity only, not production probability blend

### Budget-stage insight
- 2400-4800口 range currently gives best balance of protection vs dilution
- Priority for budget allocation:
  No11 > No10 > No3 > No5
- No9=2 and No12=2 are strong main lines
- No4=1 and No6=1 remain strongest structural anchors

### Tonight
- Re-download all 39 FootyStats PDFs for Round1653
- Compare against 1653_v2 mechanically
- Diff PPG / xG / xGA / H2H
- Re-rank No3 / No5 / No10 / No11 if values change

## 2026-09-11 FootyStats追加特徴検証 / FS_ERROR_WARNING v0.1

### 追加12特徴の1X2直接投入
2019-2024 walk-forward DESIGN + 2025 untouched CONFIRMで検証。

結論:
- CORE4は維持。
- A19 / AGG12 / ALL12はproduction不採用。
- GOAL_ENV / TIMING / STYLEの一括追加も不採用。
- DESIGNで改善した単独特徴も2025 CONFIRMで再現せず、production確率への追加採用は0。

### CORE4 Error Warning研究
目的:
CORE4確率自体は変更せず、CORE4 top1が外れやすい試合をFootyStats追加情報で検知する。

追加候補の中では
`fs_csv_average_goals_per_match_pre_match`
が最も年別安定。

Top10 risk lift vs RISK_BASE:
2020 1.123 vs 1.074
2021 1.173 vs 1.085
2022 1.047 vs 1.047
2023 1.128 vs 1.100
2024 1.160 vs 1.129
2025 1.224 vs 1.145

AUCも2020/21/22/24/25でBASE以上、2023のみ微悪化。

結論:
FS_ERROR_WARNING v0.1を研究用補助センサーとして採用。
用途は「極端な固定危険帯」の検知のみ。
production確率には混ぜない。
warning probability値を校正済み絶対失敗確率とは解釈しない。
自動的な買い目拡張ルールにはまだ昇格させない。

### Round1653 FS_ERROR_WARNING v0.1
rank:
1 No11 八戸 vs 湘南 0.6453 = 強警告
2 No10 いわき vs 横浜FC 0.6254 = 準強警告
3 No1 水戸 vs 川崎F 0.6213 = WATCH
4 No12 甲府 vs 磐田 0.6104 = WATCH
5 No7 東京V vs 千葉 0.6027 = WATCH

安全側:
No6 広島 vs C大阪 rank13
No4 町田 vs 横浜FM rank12

重要:
13試合中rank<=2は15.4%なので「Top10%」とは呼ばない。
rank1=強警告、rank2=準強警告として扱う。

### Round1653 統合上の意味
No11:
custom risk 1位 + FS_ERROR_WARNING 1位 + v1-C/MARKET TRUE SPLIT
→ 最優先拡張候補

No10:
custom risk 2位 + FS_ERROR_WARNING 2位 + v1-C/MARKET TRUE SPLIT
→ 第2拡張候補

No1/7/12:
WATCH。FS警告単独では買い目変更しない。

## 2026-09-11 late update — Round1653 pre-final

### LINEUP / PLAYER POWER
totoONE Round1653 PDFs No1-No13 acquired.
Predicted XI, absences/suspensions and team context are available for all 13 matches.

Football LAB adopted as an additional information source.

Research structure:
- J1 LINEUP_PLAYER_POWER:
  Fantasy Soccer + JLeague official Stats + FootyStats Player + Football LAB
- J2 LINEUP_PLAYER_POWER:
  JLeague official Stats + FootyStats Player + Football LAB
- Football LAB team metrics are handled separately as TEAM_CONTEXT.
- Do NOT merge this layer directly into v1-C production probabilities without historical validation.
- Missing player data must remain missing; no fabricated/imputed values presented as observed data.

Football LAB useful fields:
- player: attack/pass/cross/dribble/receive/shoot/goal/ball-winning/defence/save CBP
- team context: AGI/KAGI, chance creation, shot efficiency, attack CBP, ball-winning, defence
Avoid double-counting correlated metrics across JLeague / FootyStats / Football LAB.

### Round1653 integrated qualitative update
Strong FIX candidates:
- No4 町田 = 1
- No6 広島 = 1
- No9 鳥栖 = 2

Important expansion / warning:
- No3 G大阪-FC東京: 12 strongly preferred over hard 1.
  v1-C=1 but MARKET / FootyStats content / totoONE / lineup context warn toward FC東京.
- No10 いわき-横浜FC: 12.
  横浜FC direction is stronger, but FS_ERROR_WARNING rank2 -> avoid hard 2.
- No11 八戸-湘南: 102.
  FS_ERROR_WARNING rank1 + market/model split + close venue strength + 湘南 availability/load concerns.
- No7 東京V-千葉: hard 1 caution; DRAW is important, but expansion cost is high.
- No13 秋田-徳島: draw caution remains; 0 should not be casually discarded.
- No5 長崎-名古屋: MARKET strongly toward 2, while v1-C / FootyStats / Football LAB context preserve 1. Strong SOURCE_SPLIT.

### Integrated scenario optimization
Compared forced warning scenarios under rectangular ticket optimization.

At 7,200:
- BASE / No10=12 + No11=102 = 72 tickets
- coverage 0.000689355
- adding No3=12 costs 7.92%

At 9,600:
BASE:
12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 12 / 2 / 102
coverage 0.000889134

Integrated warning plan:
12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 102 / 2 / 12
96 tickets = 9,600 yen
coverage 0.000888862
loss vs pure v1-C optimum = only 0.03%

This simultaneously protects:
- No3=12
- No10=12
- No11=102

=> Current first-choice practical portfolio = 9,600 yen integrated plan.

At 14,400:
12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 102 / 2 / 102
144 tickets
coverage 0.001235373
No3=12 / No10=12 / No11=102 are naturally satisfied with 0% v1-C coverage loss.

### No7 expansion study
Under No3=12 / No10=12 / No11=102 constraints:

9,600:
- No7=10: loss 16.47%
- No7=12: loss 12.85%
- No7=02: loss 32.37%
- No7=102: loss 38.78%

14,400:
- No7=10: loss 16.70%
- No7=12: loss 13.09%
- No7=02: loss 32.56%
- No7=102: loss 14.24%

Interpretation:
- At 9,600, expanding No7 is currently too expensive.
- At 14,400, 102 costs only ~1.15pt more coverage loss than 12, but it forces protection to be removed elsewhere (notably No13).
- Do not expand No7 automatically; wait for final lineup / absence / market information.

### Current Round1653 first-choice plan
Budget ceiling: 9,600 yen
Actual: 96 tickets = 9,600 yen

12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 102 / 2 / 12

Priority final-monitor matches:
1. No7 東京V-千葉
2. No13 秋田-徳島
3. No1 水戸-川崎F
4. No5 長崎-名古屋
5. No8 浦和-岡山
6. No12 甲府-磐田

Core warnings currently maintained:
- No3 = 12
- No10 = 12
- No11 = 102

Do not rebuild/retrain production v1-C immediately before deadline.
Use late information only as auxiliary fixed-vs-expansion evidence.

### Final-day policy
Before sales close:
- refresh official toto voting percentages
- confirm actual starting XI / bench / late absences
- compare actual XI vs totoONE predicted XI
- update LINEUP_PLAYER_POWER only where real personnel changed
- check No7 / No13 first
- do not react to market movement alone; require supporting football information
- retain source/evidence distinction and no hindsight fabrication



---

## 2026-09-12 Round1653 FootyStats automation / analysis checkpoint

### Source automation status

- totoONE: ✅ 13/13 自動取得
- toto公式: ✅ 13/13 自動取得
- FootyStats: ✅ 13試合 × HOME/H2H/AWAY = 39/39 HTML自動取得
- Football LAB: 🔧 次工程
- Jリーグ公式: 🔧 後続
- Sportsnavi: 🔧 後続
- サッカー批評Web: 🔧 後続

### FootyStats acquisition

Round1653 の39HTML取得完了。

保存先:

`data/raw/footystats/round_html/1653/`

collector:

`scripts/fetch_footystats_round_3html_v01.py`

確認済み:
- requests方式でHOME/H2H/AWAY取得可能
- Playwright直接アクセスはCloudflare challengeを誘発したため使用しない
- 既存HTMLはSKIPして再利用
- H2H canonical redirect対応
- session定期再生成対応
- block / HTTP error / too-small response時は停止
- CAPTCHA / Cloudflare bypassは行わない
- No5 H2Hで一時85-byte response発生
- 時間を空けた再試行では約362KBの正常HTML取得
- 恒常的アクセス不可ではなかった

### FootyStats FULL RAW

No1でFULL RAW parser実証済み。

`scripts/parse_footystats_full_v01.py`

`data/parsed/footystats/toto1653_no01_full_v01.json`

取得カテゴリ:
- RESULT / FORM
- ATTACK
- DEFENSE
- xG
- SHOTS
- GOALS / TOTALS
- HALF
- TIMING
- CORNERS
- CARDS
- TERRITORY
- SETPLAY / OTHER
- H2H
- PLAYERS
- ODDS

原則:

「取れる情報は広く取る。使うときは意味ブロックにまとめる。」

GF / xG / shots / SOT / conversion 等を独立した複数voteとして数えない。

Round1653の13試合FULL RAW JSON一括保存は未完。
ただし元HTML39枚は保存済みなので再現可能。

### FootyStats NORMALIZED v0.4

完成:

`scripts/normalize_footystats_round_v04.py`

`data/analysis/footystats_toto1653_normalized_v04.csv`

結果:
- 13 rows
- 65 columns

主要NULL:
- home_xg_venue = 0
- away_xg_venue = 0
- home_xga_venue = 0
- away_xga_venue = 0
- home_gf_all = 0
- away_gf_all = 0
- home_ga_all = 0
- away_ga_all = 0

J1/J2両方に対応。

J2系ではHTML tableの

`Stats | Overall | At Home | At Away`

から
- xG For / Match
- xG Against / Match
- Scored / Match
- Conceded / Match

を構造的に取得する方式へ改善。

MARKET parserも修正済み。

例:
No3 G大阪 vs FC東京
- home 3.70
- draw 3.75
- away 1.89

### Round1653 venue xG / xGA

- No01 水戸 1.29 / 1.85 ; 川崎F 1.53 / 1.60
- No02 清水 1.09 / 1.62 ; 福岡 2.02 / 0.99
- No03 G大阪 1.40 / 1.88 ; FC東京 1.70 / 1.13
- No04 町田 1.57 / 1.50 ; 横浜FM 1.38 / 1.60
- No05 長崎 1.55 / 1.51 ; 名古屋 0.94 / 1.82
- No06 広島 2.05 / 1.10 ; C大阪 1.21 / 1.49
- No07 東京V 0.95 / 1.97 ; 千葉 1.15 / 2.06
- No08 浦和 1.29 / 2.06 ; 岡山 1.70 / 1.10
- No09 今治 1.39 / 1.55 ; 鳥栖 1.82 / 1.23
- No10 いわき 1.78 / 1.53 ; 横浜FC 1.90 / 1.65
- No11 八戸 1.09 / 1.45 ; 湘南 1.11 / 1.57
- No12 甲府 1.16 / 1.64 ; 磐田 1.39 / 1.33
- No13 秋田 1.10 / 2.14 ; 徳島 0.80 / 1.71

### FootyStats MATCH FEATURE BLOCK v0.1

完成:

`scripts/build_footystats_feature_blocks_v01.py`

`data/analysis/footystats_toto1653_feature_blocks_v01.csv`

結果:
- 13 rows
- 94 columns

重要feature NULL = 0:
- attack_block
- defense_block
- shot_quality_block
- half_block
- territory_block
- matchup_xg_home
- matchup_xg_away
- market_p1
- market_p0
- market_p2

v0.1 blocks:
- ATTACK
- DEFENSE
- SHOT_QUALITY
- HALF
- TERRITORY
- MATCHUP_XG
- DRAW_TOTALS
- SETPLAY / OTHER
- MARKET

注意:
`fs_block_mean` は勝率ではなくRound1653内のdiagnostic relative score。

HALF / TERRITORYは未検証。
次のv0.2でCOREとCONTEXTを分離する。

予定:

CORE:
- ATTACK
- DEFENSE
- SHOT_QUALITY

CONTEXT:
- HALF
- TERRITORY

別層:
- MATCHUP_XG
- MARKET

### MATCHUP_XG diagnostic

trained modelではなく比較診断用。

matchup_xg_home =
(home venue xG + away venue xGA) / 2

matchup_xg_away =
(away venue xG + home venue xGA) / 2

### Source disagreement v0.1

完成:

`scripts/build_toto1653_source_disagreement_v01.py`

`data/analysis/toto1653_source_disagreement_v01.csv`

比較対象:
- v1-C
- FootyStats feature blocks
- FootyStats matchup xG
- FootyStats bookmaker market

`disagreement_warning_v01` はcalibrated error probabilityではない。
診断用警戒スコア。

Round1653 warning rank:

1. No02 清水 vs 福岡
2. No10 いわき vs 横浜FC
3. No11 八戸 vs 湘南
4. No03 G大阪 vs FC東京
5. No08 浦和 vs 岡山
6. No13 秋田 vs 徳島
7. No01 水戸 vs 川崎F
8. No05 長崎 vs 名古屋
9. No06 広島 vs C大阪
10. No07 東京V vs 千葉
11. No04 町田 vs 横浜FM
12. No12 甲府 vs 磐田
13. No09 今治 vs 鳥栖

### Key Round1653 disagreement interpretation

No02 清水 vs 福岡:
- v1-C = 1, gap 0.0142
- FS block = AWAY
- FS matchup xG = AWAY
- FS market = 2
- v1-CだけHOMEの強いSOURCE_SPLIT

No10 いわき vs 横浜FC:
- v1-C = 1, gap 0.0155
- FS block = AWAY
- FS matchup xG = neutral
- FS market = 2
- 「2確定」ではなく「1固定危険」型

No11 八戸 vs 湘南:
- v1-C = 1, gap 0.0088
- FS block = neutral
- FS matchup xG = neutral
- FS market = 2
- 一本軸の弱い不確実性型

No03 G大阪 vs FC東京:
- v1-C = 1
- FS block = neutral
- FS matchup xG = strong AWAY
- FS market = 2
- v1-C vs MARKET + xG

No08 浦和 vs 岡山:
- v1-C = 1
- FS block = neutral
- FS matchup xG = strong AWAY
- FS market = 1 low-gap
- FootyStats内部でも大きな対立

No05 長崎 vs 名古屋:
- v1-C = 1
- FS block = HOME
- FS matchup xG = HOME
- FS market = 2
- 市場のみ逆方向

比較的整合:
- No04 町田 vs 横浜FM = HOME
- No06 広島 vs C大阪 = strong HOME
- No09 今治 vs 鳥栖 = strong AWAY
- No12 甲府 vs 磐田 = AWAY

### Production discipline

FootyStats新featureは研究・warning層。

production v1-Cは変更しない。

新featureをその場で再学習・本番blendしない。

昇格条件:

historical availability
→ historical extraction
→ walk-forward / OOF
→ calibration / discrimination
→ finite-budget toto portfolio validation

相関featureを独立voteとして数えない。

### Roadmap current position

1. FootyStats 39/39取得 ✅
2. 13試合FULL RAW化 🟡 No1実証済 / 13試合一括保存未完
3. 13試合NORMALIZED化 ✅ v0.4
4. FootyStats MATCH FEATURE BLOCK生成 ✅ v0.1
5. 1653の13試合を深く比較分析 🔧 CURRENT
6. Football LAB自動取得 ⏳
7. FootyStats × Football LAB クロス分析 ⏳
8. Jリーグ公式 ⏳
9. Sportsnavi ⏳
10. サッカー批評Web ⏳
11. 全ソース統合 warning / prediction layer ⏳
12. 過去ラウンドOOF検証 ⏳

### Next actions

1. feature_blocks_v02
   - CORE / CONTEXT分離

2. Round1653 deep comparison
   - No02
   - No10
   - No11
   - No03
   - No08
   - No13
   - No05

3. 39HTML → 13試合FULL RAW JSON一括保存

4. Football LAB自動取得

5. FootyStats × Football LAB cross analysis

### Target source architecture

SOURCE COLLECTORS
→ RAW SNAPSHOT
→ NORMALIZER
→ DIFF ENGINE
→ ROUND JOIN
→ FEATURE / EVENT BLOCKS
→ SOURCE DISAGREEMENT
→ WARNING / ANALYSIS
→ validated prediction layer
→ finite-budget optimizer

ニュース重複ルール:

同じ負傷情報が複数サイトに掲載されても複数voteにしない。

EVENT_ID = one underlying event
sources = multiple
confidence = higher
event count = 1



---

## CHECKPOINT — STEP 6 FOOTBALL LAB COMPLETE

### Status

Step 6 Football LAB automated acquisition / normalization / Round 1653 semantic processing is COMPLETE.

Current roadmap:

1. FootyStats 39/39 acquisition — COMPLETE
2. FootyStats 13-match FULL RAW — COMPLETE
3. FootyStats NORMALIZED — COMPLETE
4. FootyStats MATCH FEATURE BLOCK — COMPLETE
5. Round 1653 13-match deep comparison — COMPLETE
6. Football LAB acquisition / normalization / semantic processing — COMPLETE
7. FootyStats × Football LAB cross-source semantic comparison — NEXT
8. JLeague official — PENDING
9. Sportsnavi — PENDING
10. サッカー批評Web — PENDING
11. All-source warning / prediction layer — PENDING
12. Historical-round OOF validation — PENDING


### Step 6a — Football LAB RAW acquisition

Collector:

`scripts/fetch_football_lab_cbp_leagues_v01.py`

RAW root:

`data/raw/football_lab/cbp/2026`

Acquisition result:

- J1: 10/10 categories
- J2: 10/10 categories
- Total HTML: 20/20
- RAW acquisition: PASS

Categories acquired:

- offense
- pass
- cross
- dribble
- receive
- shot
- goal
- gain
- defense
- save

Important URL discovery:

- receive uses `passrec` on Football LAB.

Collector path matching was repaired to tolerate trailing slash differences.


### Step 6b — Football LAB table structure audit

BeautifulSoup-based structural audit completed without requiring lxml.

Audit result:

- FILES SEEN: 20
- TABLES SEEN: 98
- ERRORS: 0
- TABLE AUDIT: PASS

Important semantic discovery:

Team CBP exists for 9 categories:

- offense
- pass
- cross
- dribble
- shot
- goal
- gain
- defense
- save

`receive` does NOT contain `ls_teamCBP`.

Therefore:

- receive = PLAYER-ONLY source
- receive must NOT be fabricated as a team-level feature
- Team CBP parser uses semantic selector `#ls_teamCBP`
- positional table selection must not be used


### Step 6c — Team CBP NORMALIZED v0.1

Normalizer:

`scripts/normalize_football_lab_team_cbp_v01.py`

Output:

`data/analysis/football_lab_team_cbp_2026_normalized_v01.csv`

QA:

- TEAM CATEGORIES: 9
- LONG ROWS: 360
- TEAM ROWS: 40
- J1 ROWS: 20
- J2 ROWS: 20
- NORMALIZED NULL: 0
- CSV lines including header: 41
- NORMALIZE TEAM CBP: PASS

Normalized schema preserves, per category:

- cbp_rank
- cbp_total
- cbp_per_match
- cbp_recent5

Common league context:

- league_rank
- league_points
- goals_for
- goals_against

`team_short` extraction was verified to work correctly.


### Step 6d — Round 1653 26-team JOIN

Initial automatic normalized-name join:

- MATCH SLOTS: 26
- MATCHED: 22
- UNMATCHED: 4

Observed aliases only:

- 川崎フロンターレ -> 川崎Ｆ
- 横浜Ｆ・マリノス -> 横浜FM
- セレッソ大阪 -> Ｃ大阪
- 東京ヴェルディ -> 東京Ｖ

Policy:

1. Unicode/NFKC normalization
2. exact match
3. explicit observed alias
4. NO fuzzy matching

Feature builder:

`scripts/build_football_lab_toto1653_features_v01.py`

Output:

`data/analysis/football_lab_toto1653_feature_blocks_v01.csv`

Final QA:

- ROWS: 13
- COLS: 128
- JOIN SLOTS: 26
- EXACT JOINS: 22
- ALIAS JOINS: 4
- UNMATCHED: 0
- NULL CELLS: 0
- FOOTBALL LAB FEATURE BLOCK: PASS


### Step 6e — Football LAB semantic audit

Audit script:

`scripts/audit_football_lab_semantics_v01.py`

Primary semantic metric:

`cbp_per_match`

Reason:

J1 and J2 snapshots have different match counts, so raw cumulative totals must not be directly compared across leagues.

Standardization policy:

- J1 and J2 are standardized separately
- league-internal population mean / SD
- do NOT calculate one combined J1+J2 z-score

Major correlation findings:

J1:

- offense × pass = +0.986
- shot × goal = +0.621
- gain × defense = -0.196

J2:

- offense × pass = +0.987
- shot × goal = +0.844
- gain × defense = -0.095

Interpretation:

- offense/pass are nearly duplicate process information
- shot/goal are strongly correlated
- gain/defense are NOT one coherent independent family
- correlated CBP categories must NOT be counted as independent votes

Additional structural finding:

`defense` and `save` frequently correlate negatively with attacking-process metrics.

Therefore high defense/save CBP must NOT automatically be interpreted as stronger defensive quality.

They may partly reflect:

- defensive workload
- pressure faced
- game state
- last-line activity


### Step 6f — Football LAB semantic v0.1

Builder:

`scripts/build_football_lab_semantic_v01.py`

Output:

`data/analysis/football_lab_toto1653_semantic_v01.csv`

QA:

- ROWS: 13
- COLS: 48
- NULL: 0
- CSV lines including header: 14
- FOOTBALL LAB SEMANTIC: PASS

Semantic families:

#### BUILD_UP

- offense
- pass

These are highly correlated and treated as one semantic axis.

#### WIDTH_CARRY

- cross
- dribble

Related to creation but retained separately from BUILD_UP.

#### FINISHING

- shot
- goal

Treated as one correlated semantic axis.

#### RECOVERY

- gain

Retained as its own process axis.

#### DEFENSIVE_LAST_LINE

- defense
- save

Stored as contextual activity / pressure information.

IMPORTANT:

`DEFENSIVE_LAST_LINE` is NOT currently used as a directional win-strength vote.


### Football LAB Round 1653 semantic view

Research-only process results:

1. 水戸 - 川崎フロンターレ
   - PROC = -1.23
   - axes = 0-4
   - process split = 0

2. 清水 - 福岡
   - PROC = -1.10
   - axes = 0-4
   - process split = 0

3. Ｇ大阪 - ＦＣ東京
   - PROC = -1.01
   - axes = 0-4
   - process split = 0

4. 町田 - 横浜Ｆ・マリノス
   - PROC = +0.49
   - axes = 3-1
   - process split = 1

5. 長崎 - 名古屋
   - PROC = -0.67
   - axes = 0-4
   - process split = 0

6. 広島 - セレッソ大阪
   - PROC = +1.79
   - axes = 4-0
   - process split = 0

7. 東京ヴェルディ - 千葉
   - PROC = -1.02
   - axes = 0-4
   - process split = 0

8. 浦和 - 岡山
   - PROC = -0.39
   - axes = 2-2
   - process split = 1

9. 今治 - 鳥栖
   - PROC = -0.37
   - axes = 1-3
   - process split = 1

10. いわき - 横浜FC
    - PROC = -0.60
    - axes = 1-3
    - process split = 1

11. 八戸 - 湘南
    - PROC = -0.36
    - axes = 1-3
    - process split = 1

12. 甲府 - 磐田
    - PROC = -0.66
    - axes = 0-4
    - process split = 0

13. 秋田 - 徳島
    - PROC = +0.12
    - axes = 2-2
    - process split = 1


### Football LAB internal split counts

- build_up: 1
- width_carry: 3
- finishing: 3
- recovery: 0
- defensive_last_line: 4
- process_internal_split: 6


### Important Round 1653 observations after Football LAB

Strong away-process signals:

- No.1 水戸 vs 川崎F
- No.2 清水 vs 福岡
- No.3 G大阪 vs FC東京
- No.7 東京V vs 千葉

Strong home-process signal:

- No.6 広島 vs C大阪

Moderate away-process signals:

- No.5 長崎 vs 名古屋
- No.12 甲府 vs 磐田

Process-internal splits:

- No.4
- No.8
- No.9
- No.10
- No.11
- No.13

Especially important preliminary cross-source observations:

- No.2:
  FootyStats already warned against a fixed home pick.
  Football LAB is also 0-4 away across process axes.

- No.3:
  FootyStats matchup/market favored FC東京.
  Football LAB is also 0-4 away across process axes.

- No.6:
  Existing strongest home-fixed candidate.
  Football LAB strongly agrees: PROC +1.79, axes 4-0.

- No.10:
  Football LAB leans 横浜FC while recovery favors いわき.
  Existing low-gap / fixed-home danger remains important.

- No.13:
  BUILD_UP favors 徳島 while FINISHING and RECOVERY favor 秋田.
  PROC is nearly neutral at +0.12 with axes 2-2.
  This does NOT provide strong support for a fixed away pick.


### Interpretation constraints

Football LAB semantic values are currently RESEARCH FEATURES ONLY.

DO NOT:

- directly add PROC to v1-C probabilities
- interpret PROC as calibrated win probability
- count correlated CBP categories as independent votes
- treat defense/save CBP as automatic defensive strength
- mix J1/J2 raw totals directly
- fabricate team-level receive CBP
- introduce Football LAB into production probability blending without historical OOF validation

Current production principle remains:

`totoLABO AI primary`

External sources including Football LAB and FootyStats are currently:

- research layers
- warning layers
- semantic disagreement layers
- candidate future features pending historical validation


### NEXT — Step 7

Next task:

`FootyStats × Football LAB cross-source semantic comparison`

Required integration should preserve separately:

#### v1-C

- P1
- P0
- P2
- top
- gap

#### FootyStats

- VENUE PROCESS
- VENUE FORM
- MATCH CONTEXT
- MATCHUP_XG
- MARKET
- semantic split flags

#### Football LAB

- BUILD_UP
- WIDTH_CARRY
- FINISHING
- RECOVERY
- PROCESS
- process internal split
- defensive / last-line pressure context

#### Cross-source layer

Classify, without premature probability blending:

- SAME_DIRECTION
- OPPOSITE_DIRECTION
- NEUTRAL / WEAK
- SOURCE_SPLIT

Do NOT create an arbitrary combined weighted warning score before the semantic cross-source structure is inspected.

After Step 7 structural comparison, inspect all 13 matches, especially:

- No.2
- No.3
- No.10
- No.13

Then proceed toward additional sources and historical OOF validation.



---

## CHECKPOINT — STEP 7 FOOTYSTATS × FOOTBALL LAB CROSS-SOURCE SEMANTIC COMPLETE

### Status

Step 7 FootyStats × Football LAB cross-source semantic comparison is COMPLETE.

Current roadmap:

1. FootyStats 39/39 acquisition — COMPLETE
2. FootyStats 13-match FULL RAW — COMPLETE
3. FootyStats NORMALIZED — COMPLETE
4. FootyStats MATCH FEATURE BLOCK — COMPLETE
5. Round 1653 13-match deep comparison — COMPLETE
6. Football LAB acquisition / normalization / semantic processing — COMPLETE
7. FootyStats × Football LAB cross-source semantic comparison — COMPLETE
8. JLeague official — NEXT
9. Sportsnavi — PENDING
10. サッカー批評Web — PENDING
11. All-source warning / prediction layer — PENDING
12. Historical-round OOF validation — PENDING


### Step 7 input layers

FootyStats semantic source:

`data/analysis/toto1653_semantic_final_comparison_v03.csv`

Football LAB semantic source:

`data/analysis/football_lab_toto1653_semantic_v01.csv`

Cross-source builder:

`scripts/build_cross_source_semantic_v01.py`

Output:

`data/analysis/toto1653_cross_source_semantic_v01.csv`


### Step 7 output QA

Final QA:

- ROWS: 13
- COLS: 54
- UNPARSED FS SEMANTICS: 0
- NULL CELLS: 0
- STEP 7 SEMANTIC QA: PASS

Cross-source classifications:

- STRONG_ALIGNMENT: 6
- PARTIAL_ALIGNMENT: 3
- MIXED_SOURCE_SPLIT: 3
- FL_PROCESS_WEAK: 1

True source opposition matches:

- No.5
- No.7
- No.8

FootyStats internal semantic split present:

- No.1
- No.3
- No.4
- No.5
- No.6
- No.8
- No.11


### Important parser correction

Initial Step 7 parser assumed FootyStats direction fields were only:

- 1 = HOME
- 0 = NEUTRAL
- 2 = AWAY

Actual semantic fields also contain:

- N = NEUTRAL
- S = SPLIT

The parser was corrected so that:

- 1 -> HOME
- 2 -> AWAY
- 0 / N -> NEUTRAL
- S -> SPLIT

After correction:

- UNPARSED FS SEMANTICS: 0

This distinction is mandatory.

`SPLIT` must NOT be interpreted as an opposite-source vote.

Three structurally different states are preserved:

1. SOURCE OPPOSITION
   - one source HOME
   - another source AWAY

2. INTERNAL SPLIT
   - one source family is internally inconsistent

3. NEUTRAL
   - source does not provide a directional signal

These must not be collapsed into one disagreement variable.


### Cross-source methodology

The Step 7 layer is structural / research-only.

It compares:

#### v1-C

- P1
- P0
- P2
- top
- gap

#### FootyStats

- VENUE PROCESS
- VENUE FORM
- MATCH CONTEXT
- MATCHUP_XG
- MARKET
- semantic split information

#### Football LAB

- BUILD_UP
- WIDTH_CARRY
- FINISHING
- RECOVERY
- PROCESS
- process internal split
- defensive / last-line pressure context

The Football LAB process direction uses a research-only weak-signal threshold:

`|z| < 0.25 -> WEAK`

This threshold is NOT historically calibrated and must not be treated as an optimized production threshold.


### Cross-source classification definitions

#### STRONG_ALIGNMENT

Football LAB process direction agrees with at least three available FootyStats directional families, without true source opposition.

#### PARTIAL_ALIGNMENT

At least one FootyStats family agrees with Football LAB process direction, but the evidence is less complete because of neutral / split / unavailable directional information.

#### MIXED_SOURCE_SPLIT

There is at least one genuine HOME-vs-AWAY source opposition while another source may agree with Football LAB.

This is a true cross-source structural disagreement.

#### FL_PROCESS_WEAK

Football LAB aggregate process signal is below the research directional threshold.

This does NOT mean the match itself is low uncertainty; it only means Football LAB process does not provide a strong aggregate direction.


### Round 1653 corrected cross-source view

#### No.1 水戸 vs 川崎F

v1-C:

- top = 2
- gap = 0.020

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = AWAY
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -1.23
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 3
- opposite = 0
- internal split = 1
- STRONG_ALIGNMENT

Interpretation:

External directional layers strongly support AWAY.

The low v1-C gap remains important, so external agreement must not be interpreted as calibrated certainty.


#### No.2 清水 vs 福岡

v1-C:

- top = 1
- gap = 0.014

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = AWAY
- MATCHUP_XG = AWAY
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -1.10
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 4
- opposite = 0
- STRONG_ALIGNMENT

Interpretation:

This is one of the most important warning structures in Round 1653.

v1-C has HOME top with an extremely small gap, while all major external directional layers align AWAY.

No.2 remains a major candidate for historical validation of a `v1-C vs external-layer conflict` feature.


#### No.3 G大阪 vs FC東京

v1-C:

- top = 1
- gap = 0.085

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = AWAY
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -1.01
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 3
- opposite = 0
- internal split = 1
- STRONG_ALIGNMENT

Interpretation:

External research layers broadly align FC東京 / AWAY despite v1-C HOME top.

This is not a source-split match.

It is primarily a `v1-C vs aligned external sources` structure.


#### No.4 町田 vs 横浜FM

v1-C:

- top = 1
- gap = 0.270

FootyStats:

- VENUE PROCESS = NEUTRAL
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = NEUTRAL
- MARKET = HOME

Football LAB:

- PROCESS = HOME
- z = +0.49
- process internal split = 1

Cross-source:

- PARTIAL_ALIGNMENT

Interpretation:

v1-C HOME direction is supported by market and Football LAB.

External process evidence is not uniformly directional, but there is no true HOME-vs-AWAY source opposition.


#### No.5 長崎 vs 名古屋

v1-C:

- top = 1
- gap = 0.110

FootyStats:

- VENUE PROCESS = HOME
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = HOME
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -0.67
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 1
- opposite = 2
- MIXED_SOURCE_SPLIT

Interpretation:

This is a genuine source-opposition match.

FootyStats process / matchup favor HOME.

Football LAB process and market favor AWAY.

This is a clean PERFORMANCE / SOURCE disagreement case and should be retained for historical validation.


#### No.6 広島 vs C大阪

v1-C:

- top = 1
- gap = 0.359

FootyStats:

- VENUE PROCESS = HOME
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = HOME
- MARKET = HOME

Football LAB:

- PROCESS = HOME
- z = +1.79
- axes = 4-0
- internal process split = 0

Cross-source:

- same = 3
- opposite = 0
- STRONG_ALIGNMENT

Interpretation:

No.6 remains the strongest HOME-fixed structural candidate in the current Round 1653 research layer.

v1-C and the major external directional layers broadly agree.


#### No.7 東京V vs 千葉

v1-C:

- top = 1
- gap = 0.133

FootyStats:

- VENUE PROCESS = NEUTRAL
- MATCH CONTEXT = AWAY
- MATCHUP_XG = NEUTRAL
- MARKET = HOME

Football LAB:

- PROCESS = AWAY
- z = -1.02
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 1
- opposite = 1
- weak / neutral = 2
- MIXED_SOURCE_SPLIT

Interpretation:

Football LAB and FootyStats match context favor AWAY.

Market favors HOME.

FootyStats venue process and matchup xG are neutral.

This is genuine source opposition, but it must not automatically trigger ticket expansion.


#### No.8 浦和 vs 岡山

v1-C:

- top = 1
- gap = 0.143

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = AWAY
- MARKET = HOME

Football LAB:

- PROCESS = AWAY
- z = -0.39
- axes = 2-2
- internal process split = 1

Cross-source:

- same = 2
- opposite = 1
- internal FootyStats split present
- MIXED_SOURCE_SPLIT

Interpretation:

FootyStats process / matchup and Football LAB aggregate process lean AWAY.

Market favors HOME.

Football LAB itself is internally split 2-2.

This is a layered disagreement case rather than a simple AWAY signal.


#### No.9 今治 vs 鳥栖

v1-C:

- top = 2
- gap = 0.098

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = AWAY
- MATCHUP_XG = AWAY
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -0.37
- axes = 1-3
- internal process split = 1

Cross-source:

- same = 4
- opposite = 0
- STRONG_ALIGNMENT

Interpretation:

The major external directional families agree with v1-C AWAY.

Football LAB has some internal process heterogeneity, so the signal should not be interpreted as four independent votes.


#### No.10 いわき vs 横浜FC

v1-C:

- top = 1
- gap = 0.016

FootyStats:

- VENUE PROCESS = NEUTRAL
- MATCH CONTEXT = AWAY
- MATCHUP_XG = NEUTRAL
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -0.60
- axes = 1-3
- internal process split = 1

Cross-source:

- same = 2
- opposite = 0
- PARTIAL_ALIGNMENT

Interpretation:

This remains an important `1 fixed danger` match.

v1-C HOME advantage is extremely small.

Market, FootyStats match context, and Football LAB aggregate process lean AWAY.

No true external source opposition is present.


#### No.11 八戸 vs 湘南

v1-C:

- top = 1
- gap = 0.009

FootyStats:

- VENUE PROCESS = NEUTRAL
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = NEUTRAL
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -0.36
- axes = 1-3
- internal process split = 1

Cross-source:

- same = 1
- opposite = 0
- PARTIAL_ALIGNMENT

Interpretation:

This is the smallest v1-C gap in the round.

The external structure does not provide the same broad AWAY agreement as No.2, but market and Football LAB lean AWAY while FootyStats context is internally split.

Draw relevance remains a separate probability / portfolio question and must not be inferred directly from source disagreement.


#### No.12 甲府 vs 磐田

v1-C:

- top = 2
- gap = 0.097

FootyStats:

- VENUE PROCESS = AWAY
- MATCH CONTEXT = AWAY
- MATCHUP_XG = AWAY
- MARKET = AWAY

Football LAB:

- PROCESS = AWAY
- z = -0.66
- axes = 0-4
- internal process split = 0

Cross-source:

- same = 4
- opposite = 0
- STRONG_ALIGNMENT

Interpretation:

This is one of the cleanest AWAY-alignment matches.

The previously observed FORM=HOME exception remains contextual, but the principal process / matchup / market / Football LAB structure supports AWAY.


#### No.13 秋田 vs 徳島

v1-C:

- top = 2
- gap = 0.022

FootyStats:

- VENUE PROCESS = SPLIT
- MATCH CONTEXT = SPLIT
- MATCHUP_XG = NEUTRAL
- MARKET = AWAY

Football LAB:

- PROCESS = WEAK
- z = +0.12
- axes = 2-2
- internal process split = 1

Cross-source:

- same = 0
- opposite = 0
- weak = 4
- FL_PROCESS_WEAK

Interpretation:

No.13 is NOT primarily a true cross-source opposition match.

Instead, multiple semantic layers fail to produce a clean directional process signal.

Football LAB:

- BUILD_UP favors 徳島
- FINISHING favors 秋田
- RECOVERY favors 秋田
- aggregate process is near neutral

Therefore the external research layer does not provide strong justification for a fixed AWAY selection despite v1-C top=2 and market AWAY.


### Step 7 structural conclusions

The Round 1653 matches now separate into materially different disagreement types.

#### A. v1-C vs aligned external sources

Important examples:

- No.2
- No.3
- No.10

These must NOT be labeled as source opposition when the external sources themselves broadly agree.

The research question is whether historical OOF shows predictive value when:

- v1-C points one direction
- external semantic layers align in another direction
- especially when v1-C gap is small


#### B. True cross-source opposition

Matches:

- No.5
- No.7
- No.8

These contain genuine HOME-vs-AWAY disagreement between external source families.

This is distinct from internal semantic split.


#### C. Internal semantic uncertainty

Important examples:

- No.1
- No.3
- No.4
- No.5
- No.6
- No.8
- No.11

FootyStats has at least one internally split semantic family in these matches.

Internal split must not be counted as an independent opposing source.


#### D. Weak / unresolved external process

Important example:

- No.13

This structure differs from true source opposition.

The source layers are not necessarily fighting each other; rather, they fail to establish a strong aggregate process direction.


#### E. Broad external alignment with v1-C

Important examples:

- No.6 HOME
- No.9 AWAY
- No.12 AWAY

These are useful future historical-validation candidates for studying whether multi-source agreement improves fixed-selection reliability.


### Critical methodology constraints after Step 7

DO NOT interpret:

`number of agreeing source fields`

as the number of independent predictive votes.

Reasons:

- FootyStats xG / matchup xG are algebraically related
- Football LAB offense / pass are highly correlated
- Football LAB shot / goal are correlated
- match-context components may share the same underlying sample
- market is a separate information family but not automatically a production probability blend
- semantic families can contain internal splits

Therefore:

`same_count`

is structural metadata, NOT a calibrated confidence score.


### SOURCE_SPLIT policy

`cross_source_split = 1`

currently means:

At least one genuine HOME-vs-AWAY opposition exists between Football LAB process and the selected FootyStats / market directional families.

It does NOT mean:

- automatically select DRAW
- automatically buy a double
- automatically buy a triple
- automatically increase probability entropy
- automatically adjust P1/P0/P2

Historical OOF validation is required before any production action.


### Warning policy

Existing:

`warning_v03`

remains a diagnostic / research-priority measure.

It is NOT:

- calibrated error probability
- calibrated upset probability
- production blend weight
- automatic ticket expansion score

Step 7 does NOT replace warning_v03 with a new arbitrary combined warning score.


### Production probability policy remains unchanged

Production principle remains:

`totoLABO AI primary`

Current production probabilities remain based on the validated primary model / portfolio architecture.

FootyStats and Football LAB remain auxiliary layers for:

- research
- warning
- semantic disagreement
- source consistency
- candidate feature generation
- future historical OOF validation

No Football LAB or cross-source semantic feature is to be mixed into production P1/P0/P2 until historical OOF evidence supports it.


### Step 7 final status

`FootyStats × Football LAB cross-source semantic comparison: COMPLETE`

Final structural result:

- 13/13 matches joined
- 54 columns
- NULL = 0
- unparsed FootyStats semantic values = 0
- STRONG_ALIGNMENT = 6
- PARTIAL_ALIGNMENT = 3
- MIXED_SOURCE_SPLIT = 3
- FL_PROCESS_WEAK = 1
- TRUE SOURCE OPPOSITION = No.5, No.7, No.8

The distinction between:

- v1-C conflict
- external source opposition
- source-internal semantic split
- neutral signal
- weak signal

is now explicitly preserved.


### NEXT — Step 8 JLeague official

Next source layer:

`JLeague official`

Round 1653 JLeague match IDs:

1. 水戸 vs 川崎F — 46189
2. 清水 vs 福岡 — 46190
3. G大阪 vs FC東京 — 46192
4. 町田 vs 横浜FM — 46191
5. 長崎 vs 名古屋 — 46194
6. 広島 vs C大阪 — 46193
7. 東京V vs 千葉 — 46197
8. 浦和 vs 岡山 — 46198
9. 今治 vs 鳥栖 — 46565
10. いわき vs 横浜FC — 46560
11. 八戸 vs 湘南 — 46561
12. 甲府 vs 磐田 — 46564
13. 秋田 vs 徳島 — 46559

Step 8 should preserve the same acquisition discipline:

1. acquire broadly
2. save RAW
3. audit actual source structure
4. normalize without fabrication
5. preserve source semantics
6. join 13/13 with explicit QA
7. only then design research features
8. do NOT blend into production probability before historical OOF validation


---

## STEP 8 — JLEAGUE OFFICIAL — COMPLETE

### Status
STEP 8 COMPLETE.

JLeague official data for toto1653 has been discovered, acquired,
audited for temporal leakage, semantically normalized, and converted
into a 13-match research feature/event block.

### 8a Official match URL mapping
Output:
- data/raw/jleague/discovery/1653/jleague_toto1653_url_mapping_v03.csv

QA:
- matches: 13/13
- PASS: 13/13
- unique official URLs: 13/13

Important:
- toto1653 spans 2026-09-12 and 2026-09-13.
- No7 東京V-千葉 = J1 2026/091302
- No8 浦和-岡山 = J1 2026/091303
- JLeague internal IDs are not direct public URL path keys.

### 8b RAW acquisition
RAW root:
- data/raw/jleague/round_html/1653/

Page families:
- base
- preview
- lineup
- live
- stats

QA:
- 65/65 HTTP 200
- 65/65 fixture-specific valid pages
- each page family: 13/13

Manifest:
- data/raw/jleague/round_html/1653/manifest_v01.csv

Important parser finding:
The string "お探しのページは見つかりません" exists inside normal
JLeague common HTML and MUST NOT be used alone as a 404 validity test.

Use fixture-specific title / structure validation instead.

### 8c Temporal / leakage audit
Output:
- data/raw/jleague/round_html/1653/content_audit_v01.csv

Important:
URL/page existence != content availability.

No7/No8 provided a useful pre-match timing control:
their lineup/live pages existed but had little/no match content before
the 2026-09-13 fixtures.

Keyword presence alone is not sufficient to identify leakage because
terms such as 得点 / シュート / 試合速報 / スタッツ can appear in
navigation, historical context, or preview prose.

Target-match post-kickoff results, live stats, target-match xG,
shots, possession, and player performance MUST NOT enter a pre-match
prediction.

### 8d Preview extraction
Output:
- data/raw/jleague/round_html/1653/preview_text_audit_v01.csv

JLeague preview is valuable primarily as:
- NEWS
- PLAYER AVAILABILITY
- SUSPENSION / RETURN
- TACTICS
- SCHEDULE / REST
- PLAYER ROLE / CONTEXT

It is semantically different from FootyStats and Football LAB.

### 8e-8h Event extraction / QA
Candidate output:
- data/raw/jleague/round_html/1653/preview_event_candidates_v01.csv

Normalized candidate output:
- data/raw/jleague/round_html/1653/preview_events_normalized_v01.csv

Initial candidates: 45
False-positive filtering: 44
Overlap-normalized candidates: 38

Important false-positive:
"J1復帰後初勝利" was incorrectly detected as PLAYER RETURN.
Generic keyword matching therefore MUST NOT directly create production
events.

Overlapping contexts MUST NOT be counted as independent votes/events.

### 8i Semantic event block
Event output:
- data/raw/jleague/round_html/1653/jleague_semantic_events_v01.csv

Feature output:
- data/analysis/jleague_toto1653_semantic_v01.csv

QA:
- semantic events: 19
- matches: 13
- all model_action = RESEARCH_ONLY

Match event counts:
01 水戸-川崎      1
02 清水-福岡      2
03 G大阪-FC東京   3
04 町田-横浜FM    1
05 長崎-名古屋    0
06 広島-C大阪     2
07 東京V-千葉     1
08 浦和-岡山      5
09 今治-鳥栖      2
10 いわき-横浜FC  1
11 八戸-湘南      1
12 甲府-磐田      0
13 秋田-徳島      0

Important:
no_event=1 means no qualifying event was identified by this extraction.
It MUST NOT be interpreted as "no injuries / no absences / healthy team".

### High-value current examples

No8 浦和-岡山:
- 浦和 肥田野蓮治:
  RETURN_TO_FULL_TRAINING / POSSIBLE_SQUAD
- 浦和 サミュエル グスタフソン:
  RETURN_TO_FULL_TRAINING / POSSIBLE_SQUAD
- 浦和 山根視来:
  AVAILABILITY_UNCERTAIN / FIFTY_FIFTY
- 岡山 オベルダン:
  SUSPENSION / OUT
- 浦和:
  TACTICAL_FORMATION_OPTION / UNCERTAIN

These are useful counter-information against directional statistical
layers, but they MUST NOT automatically modify P(1,0,2).

### Production policy
JLeague official is currently a RESEARCH / EVENT / WARNING layer.

Do NOT directly add/subtract probability from:
- injury
- return
- suspension
- short rest
- tactical change

until historical OOF validation establishes an effect.

Preserve:
EVENT -> TEAM -> PLAYER -> STATUS -> TEMPORAL_SCOPE ->
CERTAINTY -> SOURCE -> MODEL_ACTION

Duplicate reports of the same real-world event should later share one
EVENT_ID rather than become multiple votes.

### Roadmap
1 FootyStats acquisition — COMPLETE
2 FootyStats FULL RAW — COMPLETE
3 FootyStats NORMALIZED — COMPLETE
4 FootyStats feature block — COMPLETE
5 toto1653 deep semantic comparison — COMPLETE
6 Football LAB — COMPLETE
7 FootyStats x Football LAB cross-source semantics — COMPLETE
8 JLeague official — COMPLETE
9 Sportsnavi — NEXT
10 サッカー批評Web — PENDING
11 all-source warning/prediction layer — PENDING
12 historical-round OOF validation — PENDING

NEXT:
STEP 9 — SPORTSNAVI


## STEP 9 — Sportsnavi acquisition / semantic event layer COMPLETE

### Acquisition architecture
Sportsnavi is treated as an event-discovery / coverage source, not as an
independent predictive vote.

Two discovery routes are required:

1. CLUB KEYWORD ROUTE
   - `https://sports.yahoo.co.jp/list/official/jleague?genre=jleague&keyword=<club>`
   - useful for club-specific official information
   - keyword parameter is not a strict filter
   - article-level relevance filtering is required

2. LEAGUE-WIDE BULLETIN ROUTE
   - required for cross-team notices whose titles do not contain each club name
   - critical example:
     `出場停止選手のお知らせ（2026/09/07）`
   - club-only discovery would have missed target-round suspension events

### Discovery / RAW results
Step 9b initial DOM relevance logic was rejected:
- 520 / 520 relevant was a false-positive caused by using an overly broad
  ancestor DOM container.

Step 9b-v02 article-title audit:
- source rows: 520
- title hits: 352

Step 9c pre-match candidate filter:
- priority candidates: 41

Step 9d RAW acquisition:
- candidates: 41
- HTTP 200: 41 / 41
- valid: 41 / 41
- unique article IDs: 39
- unique body SHA1: 39

Step 9e semantic audit:
- unique articles: 39
- keyword audit is discovery QA only; keyword count is NOT event strength.

### League-wide suspension bulletin
Sportsnavi/JLeague syndicated bulletin:
`2026090700082-spnaviow`

Target toto1653 suspensions confirmed:
- No2 清水: 住吉 ジェラニレショーン — SUSPENSION / OUT
- No8 岡山: オベルダン — SUSPENSION / OUT
- No11 湘南: 小野瀬 康介 — SUSPENSION / OUT
- No13 秋田: 土井 紅貴 — SUSPENSION / OUT

### Sportsnavi normalized events
Output:
`data/analysis/sportsnavi_toto1653_events_v01.csv`

Normalized events before cross-source dedupe:
- 27 events
- SQUAD_ADDITION 12
- LONG_TERM_ABSENCE 5
- SUSPENSION 4
- INJURY 2
- SQUAD_DEPARTURE 2
- SQUAD_RETURN 1
- RETURN_TO_TEAM 1

Future-season acquisition announcements are excluded from current-squad
semantic events.

### JLeague × Sportsnavi event dedupe
Output:
`data/analysis/toto1653_jleague_sportsnavi_events_v01.csv`

Cross-source status:
- NEW_COVERAGE: 25
- SAME_EVENT: 2

Confirmed SAME_EVENT:
- No3 G大阪: 植中 injury
- No8 岡山: オベルダン suspension

These MUST NOT be counted as two independent votes.

Important NEW high-value coverage includes:
- No1 川崎F: 宮城 long-term absence
- No1 川崎F: ラザル ロマニッチ injury
- No2 清水: 住吉 suspension
- No6 広島: 大迫 return to team
- No11 湘南: 小野瀬 suspension
- No12 甲府: 三平 long-term absence
- No12 甲府: 河田 long-term absence
- No12 磐田: 甲斐 long-term absence
- No12 磐田: 植村 long-term absence
- No13 秋田: 土井 suspension

### Sportsnavi 13-match semantic feature block
Output:
`data/analysis/sportsnavi_toto1653_semantic_v01.csv`

QA:
- matches: 13
- events: 27
- absence events: 11
- new coverage: 25
- same events: 2
- all model_action = RESEARCH_ONLY

Match event summary:
01 水戸-川崎F events=4 abs=2
02 清水-福岡 events=2 abs=1
03 G大阪-FC東京 events=3 abs=1
04 町田-横浜FM events=2 abs=0
05 長崎-名古屋 events=0 abs=0
06 広島-C大阪 events=4 abs=0
07 東京V-千葉 events=1 abs=0
08 浦和-岡山 events=4 abs=1
09 今治-鳥栖 events=0 abs=0
10 いわき-横浜FC events=0 abs=0
11 八戸-湘南 events=1 abs=1
12 甲府-磐田 events=5 abs=4
13 秋田-徳島 events=1 abs=1

`event_count=0` means only:
NO RELEVANT PRIORITY EVENT FOUND BY THE CURRENT SPORTSNAVI ROUTES.

It MUST NOT be interpreted as:
- healthy squad
- no injuries
- no suspensions
- complete information coverage

### Temporal / leakage policy
For production or historical OOF use:
- article publication timestamp MUST precede target-match kickoff/cutoff
- target-match post-kickoff information is forbidden
- acquisition may be broad, but model-use filtering must respect availability
  timestamp

### Provenance / independence policy
Sportsnavi is an aggregator/host.

Required conceptual structure:

SPORTSNAVI ARTICLE
    -> ORIGINAL PUBLISHER
    -> NORMALIZED EVENT
    -> EVENT_ID

JLeague official information syndicated through Sportsnavi is not an
independent source vote.

Exact article duplication and semantic event duplication must be removed
before any disagreement or warning logic.

### Production policy
Sportsnavi semantic features remain RESEARCH_ONLY.

Do NOT directly adjust P_final from:
- raw event counts
- absence counts
- transfer counts
- number of publishers/articles

Long-term absences may already be reflected in historical team performance.
Player importance, replacement quality, timing, and historical OOF validation
are required before any probability adjustment.

### STEP 9 STATUS
SPORTSNAVI: COMPLETE

Next roadmap:
STEP 10 — サッカー批評Web acquisition / semantic event layer
STEP 11 — all-source warning / prediction layer
STEP 12 — historical-round OOF validation


## STEP 10 SOCCERHIHYO WEB COMPLETE (20260912_223952)

- Source: サッカー批評Web / soccerhihyo.futabanet.jp
- Round: toto 1653
- Discovery: 125 unique recent articles; explicit toto1653 articles = 2
- Explicit articles: 111741, 111742
- Full acquisition followed HTML-discovered continuation links; teaser pages were not treated as full article content.
- Editorial pick image acquired: 620x1628 PNG.
- Two prediction series preserved separately:
  - EDITOR_YOU
  - REPORTER_TS
- Prediction rows: 13 matches / 26 predictions.
- Internal agreement only No9 and No12; both predict AWAY (2).
- Internal split: 11/13 matches.
- Explicit editorial-analysis directions:
  - No1 水戸-川崎Ｆ = HOME (1)
  - No4 町田-横浜FM = AWAY (2)
  - No7 東京Ｖ-千葉 = HOME (1)
  - No8 浦和-岡山 = HOME (1)
- T.S. agrees with explicit editorial analysis on all 4/4.
- YOU does not exactly agree with editorial direction on those 4:
  No1 DRAW, No4 HOME, No7 DRAW, No8 DRAW.
- Editorial analysis and individual image picks remain separate semantic layers.
- Same-media predictors are NOT treated as independent source votes.
- source_group = SOCCERHIHYO_EDITORIAL_1653
- prediction_independence = SAME_MEDIA_NOT_INDEPENDENT
- temporal_class = PREMATCH
- use_class = RESEARCH_ONLY
- No production probability blending until historical OOF validation.
- Outputs:
  - data/analysis/soccerhihyo_toto1653_predictions_v01.csv
  - data/analysis/soccerhihyo_toto1653_semantic_v01.csv
  - data/analysis/toto1653_cross_source_soccerhihyo_v01.csv
  - data/analysis/toto1653_soccerhihyo_direction_audit_v01.csv
- STEP 10: COMPLETE


## STEP 11 COMPLETE — ALL-SOURCE WARNING / PREDICTION ANALYSIS (20260912_224740)

- Round: toto 1653
- 13/13 matches integrated into one semantic evidence matrix.
- Production probability remains v1-C P_base. External sources are NOT automatically blended.
- Integrated research layers:
  - FootyStats semantic families and MARKET
  - Football LAB process
  - JLeague official event/context
  - Sportsnavi event discovery with cross-source deduplication
  - サッカー批評Web prediction/editorial layers
- Correlated features and same-media predictions are not treated as independent votes.
- JLeague/Sportsnavi absence/return/tactics information remains context/warning, not automatic 1/0/2 direction.
- Core representative research axes:
  FootyStats VENUE_PROCESS / MATCHUP_XG / MARKET + Football LAB PROCESS.
  Statistical independence is NOT assumed; historical OOF must validate/reduce these axes.
- Core direction classes:
  - BASE_ALIGNED: [1, 6, 9, 12]
  - EXTERNAL_OPPOSITION: [2, 3, 8]
  - LOW_V1C_GAP (<0.03 research threshold): [1, 2, 10, 11, 13]
- Coverage research:
  - FIXED_CANDIDATE: [6, 9, 12]
  - HIGH_EXPANSION_RESEARCH: [2, 3, 8, 10, 11, 13]
  - THREEWAY_RESEARCH: [1, 2, 10, 11, 13]
- Important interpretations:
  - No2: ultra-low v1-C gap + core external opposition.
  - No3: all representative external core axes oppose v1-C HOME.
  - No8: statistical/process opposition versus MARKET/T.S./editorial HOME support.
  - No10/11/13: low-gap unresolved cases with draw/away sensitivity.
  - No6/9/12: strongest fixed research candidates; this is NOT yet a production fixed-ticket rule.
  - No12 absence events affect both sides and must not be interpreted by raw count alone.
- Research thresholds such as gap<0.03 and P0>=0.27 are uncalibrated and must be validated historically.
- All outputs remain RESEARCH_ONLY / OOF_REQUIRED.
- No external feature is promoted into P_final before historical walk-forward OOF validation.
- Outputs:
  - data/analysis/toto1653_all_source_evidence_matrix_v01.csv
  - data/analysis/toto1653_all_source_warning_profile_v01.csv
  - data/analysis/toto1653_all_source_research_profile_v01.csv
  - data/analysis/toto1653_coverage_priority_v01.csv
  - data/analysis/toto1653_all_source_final_diagnostic_v01.csv
- STEP 11: COMPLETE


## Step 12 Historical OOF / finite-budget validation COMPLETE

### Baseline OOF
- v1-C stacked OOF: 2023-2025, n=3428.
- 1X2 LogLoss = 1.056595.
- Brier = 0.637021.
- Top1 accuracy = 0.446908.
- Reproduction matches existing STATE/evaluation artifacts.

### Endogenous warning diagnostics
- LOW_GAP (gap < .03): n=464, error=0.6099.
- DRAW_PRESS (P0 >= .27): n=1170, draw rate=0.2872.
- BOTH: n=315, error=0.6222.
- BOTH Top2 coverage=0.7206.
- BOTH Top2 residual misses=88/315 and all 88 were DRAW.
- These are frozen diagnostic thresholds, not historically optimized thresholds.

### Historical toto finite-budget base
- Clean v1-C OOF toto base: 61 complete rounds / 793 matches.
- Seasons: 2023=20 rounds, 2024=20, 2025=21.
- Exact DP reconstruction of existing BASELINE objective PASS.
- BASELINE maximizes product of selected probability mass under budget.
- 96-ticket optimum structure: 7 singles + 5 doubles + 1 triple for all 61 rounds.
- BASELINE96:
  - ALL: hit13=1, hit12+=2, hit11+=5, mean model coverage=.001232.
  - 2025 confirmation: hit13=0, hit12+=1, hit11+=3, coverage=.001491.

### BOTH hard-allocation test
- Frozen rule forcing the triple onto BOTH was tested at same 96-ticket structure.
- ALL: BASE 1/2/5 vs forced 0/2/5 for 13/12+/11+.
- 2025: no benefit.
- Therefore BOTH -> AUTO TRIPLE is rejected.
- BASELINE96 already expands 80/80 BOTH matches:
  DOUBLE=49, TRIPLE=31, SINGLE=0.

### Warning absorption
- LOW_GAP: 113/113 expanded by BASELINE96.
- BOTH: 80/80 expanded.
- DRAW_PRESS: 212/274 expanded (77.37%).
- Probability optimizer already absorbs most endogenous uncertainty.

### Historical external opposition validation
- multisource walk-forward predictions 2022-2025: n=4502.
- Clean toto OOF join: 793/793 complete.
- FootyStats/team2/JLeague/Elo source probabilities complete for 793/793.
- External source top1 disagreement vs v1-C:
  - 0 opposing sources: error=.4892.
  - 1 opposing source: error=.5979.
  - 2 opposing sources: error=.6392.
  - 3 opposing sources: error=.7273.
  - 4 opposing sources: error=1.0000 (n=5 only).
  - 2+ opposition: error=.6741 vs .5213 otherwise.
  - 3+ opposition: error=.7632 vs .5364 otherwise.
- 2+ opposition by season:
  2023=.6154, 2024=.6829, 2025=.7091.
- Thus external disagreement has strong historical OOF warning validity.

### External direction / allocation diagnostic
- On BASE misses with 2+ opposition:
  any opposing source rescued 59/91=.6484.
- Result-blind external consensus rescued 56/91=.6154.
- 3+ consensus rescued 19/29=.6552 on BASE misses.
- This supports directional information, but not BASE replacement.
- Frozen same-96 external-consensus swap:
  61 rounds, 15 swaps across 13 rounds.
  hit delta: -1 on 2 rounds, 0 on 54, +1 on 4, +2 on 1.
  2025: +1 on 2 rounds, otherwise unchanged.
  However 13/12+/11+ remained BASE=1/2/5 vs WARN=1/2/5 overall,
  and BASE=0/1/3 vs WARN=0/1/3 in 2025.
- Therefore external-consensus hard allocation is NOT promoted to production.

### External warning absorption
- Historical 2+ opposition matches: n=135.
- BASELINE96 allocation:
  SINGLE=15, DOUBLE=91, TRIPLE=29.
- Expanded rate=.8889.
- 3+ opposition expanded 32/33.
- 4-source opposition expanded 5/5.
- By season expanded rate:
  2023=.8974, 2024=.8537, 2025=.9091.

### Step 12 production conclusion
1. Warning validity does not imply automatic allocation validity.
2. LOW_GAP and BOTH are useful diagnostics but are already strongly absorbed by P-based optimization.
3. Historical external opposition is a validated error-warning concept.
4. External consensus has some directional information, but finite-budget evidence is insufficient to replace BASELINE allocation.
5. Production remains:
   P_final -> finite-budget BASELINE probability optimization.
6. Warning/source layers remain research-priority and diagnostic layers unless a future holdout/nested walk-forward allocation strategy shows robust improvement.
7. Current 1653-specific Football LAB / JLeague preview / Sportsnavi / Soccerhihyo semantic effects are NOT individually historical-OOF validated and must remain RESEARCH_ONLY.
8. Do not recreate historical news/source semantics using post-outcome information.

Step 12 status: COMPLETE.


## Step 13 toto1653 production baseline 96

### Production baseline
Historical OOF / finite-budget validation from Step 12 is authoritative.
No unvalidated external semantic hard rule is applied to production probabilities.

Production probability:
- v1-C probabilities remain the production P for this baseline.
- 1653-specific external semantic layers remain diagnostic/research layers.
- Finite-budget allocation uses the validated BASELINE probability optimizer.

### Production baseline 96
Pattern:
21 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 12 / 2 / 210

Structure:
- SINGLE = 7
- DOUBLE = 5
- TRIPLE = 1
- combinations = 96

Expanded:
- No01 水戸-川崎F = 21
- No02 清水-福岡 = 12
- No03 G大阪-FC東京 = 12
- No10 いわき-横浜FC = 12
- No11 八戸-湘南 = 12
- No13 秋田-徳島 = 210

Singles:
- No04 町田-横浜FM = 1 : RESEARCH_FIXED
- No05 長崎-名古屋 = 1 : RESEARCH_FIXED
- No06 広島-C大阪 = 1 : SUPPORTED_FIXED
- No07 東京V-千葉 = 1 : RESEARCH_FIXED
- No08 浦和-岡山 = 1 : BUDGET_CONSTRAINED_FIXED
- No09 今治-鳥栖 = 2 : SUPPORTED_FIXED
- No12 甲府-磐田 = 2 : SUPPORTED_FIXED

### Double protection audit
Existing five doubles are retained.

- No01 gap=.0202:
  LOW_GAP + event context + human opposition/draw.
- No02 gap=.0142:
  EXTERNAL_OPPOSITION + LOW_GAP + event context.
- No03 gap=.0855:
  EXTERNAL_OPPOSITION with strong AWAY external alignment;
  venue process=AWAY, matchup xG=AWAY, market=AWAY, FL process=AWAY;
  human opposition/draw also present.
- No10 gap=.0155:
  UNRESOLVED + LOW_GAP + human opposition.
- No11 gap=.0088:
  UNRESOLVED + LOW_GAP + event context + human opposition/draw.

Historical Step12 showed LOW_GAP is a valid error-warning region and
BASELINE96 naturally expanded 100% of historical LOW_GAP cases.

### No08 residual risk
No08 浦和-岡山 remains the principal budget-constrained single.

Evidence:
- core_direction_class = EXTERNAL_OPPOSITION.
- coverage = HIGH_EXPANSION_RESEARCH.
- venue process=AWAY.
- matchup xG=AWAY.
- FL process=AWAY.
- but venue form=HOME, market=HOME and editorial/base support exist.
- absence/event context exists.
- therefore evidence is internally mixed.

A same-96 swap No03 DOUBLE -> No08 DOUBLE was rejected:
- No03 external opposition is more directionally coherent.
- No03 FootyStats warning is stronger.
- removing No03 insurance is not justified.

No08=1 does NOT mean low risk.
It means the validated 96-ticket optimizer cannot expand it without
removing protection from another match with stronger/equivalent evidence.

### Residual research singles
- No04: UNRESOLVED / HUMAN_OPPOSITION_RESEARCH.
- No05: MIXED_DIRECTION / SOURCE_SPLIT.
- No07: MIXED_DIRECTION / SOURCE_SPLIT.
These remain research risks but do not displace the current five doubles.

### Supported singles
- No06 = 1.
- No09 = 2.
- No12 = 2.
These have BASE_ALIGNED / FIXED_CANDIDATE support.
No12 absence count alone does not override its strong directional alignment.

### Status
PRODUCTION_BASELINE_96_FIXED.

This is the validated baseline portfolio, not an immutable final ticket.
Pre-kickoff information may trigger a new diagnostic review, but any
allocation change must be explicitly compared against this same-96 baseline.

---

## 2026-09-13 checkpoint — Step13-16 postmortem / LOSS PATH / DRAW PATH research

### Step13 — toto1653 production baseline
Production remains BASELINE finite-budget probability optimization; no unvalidated external hard rule.

Canonical 96-ticket pattern:
`12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 12 / 2 / 102`

Expanded:
- DOUBLE: No1,2,3,10,11
- TRIPLE: No13
- SINGLE: No4,5,6,7,8,9,12

Single classification:
- No4 RESEARCH_FIXED
- No5 RESEARCH_FIXED
- No6 SUPPORTED_FIXED
- No7 RESEARCH_FIXED
- No8 BUDGET_CONSTRAINED_FIXED
- No9 SUPPORTED_FIXED
- No12 SUPPORTED_FIXED

IMPORTANT:
This production pattern is NOT identical to the earlier reference pre-deadline 96-ticket pattern.
Reference had No11=102 and No13=12; current production has No11=12 and No13=102.

### toto1653 postmortem / user-reported results
Known misses included:
- No4 町田 1-1 横浜FM: ticket single HOME -> actual DRAW
- No9 今治-鳥栖: ticket single AWAY -> actual HOME

No3 G大阪 0-2 FC東京 was covered by DOUBLE and is important structurally:
external/process evidence correctly indicated a strong LOSS PATH.

Research philosophy:
- A win may occur without an obvious reason, but a loss should be investigated for its pre-match loss path.
- DRAW prediction is strategically central to toto.
- Postmortem should search pre-match structural precursors, not create post-hoc rules.

### Step14 — historical disagreement recalibration
Historical OOF external opposition count is a strong BASE error/overconfidence warning.

Key result:
- General opposition-based BASE shrinkage failed nested walk-forward overall -> REJECT.
- Strong external consensus (CONS3+) local recalibration improved LL/Brier in both 2024 and 2025 nested WF tests.
- CONS3+ is a P_final recalibration CANDIDATE only; adjustment form/shrinkage still requires robustness/holdout validation.
- SOURCE_OPPOSITION -> DRAW hard rule remains rejected.
- Strong opposition more often shifts probability toward opposite WIN than DRAW.

### Step15 — No4 draw audit
No4 pre-match:
- v1-C HOME .518415 / DRAW .248626 / AWAY .232959
- gap .269790
- venue process NEUTRAL
- matchup xG NEUTRAL
- match context SPLIT
- market HOME
- Football LAB process HOME
- Football LAB recovery AWAY
- editorial direction AWAY
- draw_research_flag=0

Conclusion revised:
Do NOT close No4 as simply an unpredictable draw tail.
Research FAVORITE-FAIL and DRAW PATH:
1. Favorite survives vs favorite fails.
2. Conditional on favorite fail: DRAW vs opponent win.

DRAW may arise not from explicit DRAW votes, but from opposing win paths cancelling each other.

### Step16 — LOSS PATH / FAVORITE-FAIL / DRAW PATH

#### Step16a
No3 G大阪-FC東京:
- BASE HOME .4112
- venue process AWAY
- matchup xG AWAY
- market AWAY
- Football LAB process AWAY
- Football LAB recovery strongly AWAY
=> genuine multi-layer LOSS PATH.

No4:
- BASE HOME .5184
- market HOME
- FL process HOME
- venue/matchup NEUTRAL
- context SPLIT
- FL recovery AWAY
=> FAVORITE-FAIL candidate rather than strong opponent-win LOSS PATH.

#### Step16c — historical 4-source probability proxy
Using FootyStats/team2/JLeague/Elo external probability vectors:
base_support_deficit, draw_lift, opp_lift did NOT separate BASE_WIN / DRAW / OPP_WIN.
Conclusion:
mean external probabilities are too correlated/redundant with v1-C to identify DRAW PATH.

#### Step16d — external directional topology
Overall:
- BOTH_WIN_SIDES DRAW .269
- CANCEL_2v2 .261
- ONE_SIDE .251

Year-to-year instability is substantial.
High BASE >=.45 showed BOTH_WIN_SIDES DRAW .364 vs ONE_SIDE .212, but n=11 only.
No production rule.

#### Historical FootyStats asset
Available causal historical prediction assets:
- 2019-2024 walk-forward: 6562 matches
- 2025 OOS: 1140 matches
- total 7702
- IDs complete/no duplicates
- target_toto available
- model probabilities include xg2/core4/a19/market (plus older models where available)

CRITICAL LABEL QA:
FootyStats historical `target_toto` encoding is:
- 0 = HOME
- 1 = DRAW
- 2 = AWAY

TOTO LABO canonical encoding is:
- 1 = HOME
- 0 = DRAW
- 2 = AWAY

Therefore ALWAYS canonicalize:
`actual = target_toto.map({0:1, 1:0, 2:2})`

Step16g before this discovery used the wrong interpretation and MUST BE DISCARDED.

#### Step16i — corrected 7694 market-available matches
Actual canonical distribution:
- DRAW 1996
- HOME 3110
- AWAY 2588

Draw probabilities alone have weak discrimination:
actual DRAW vs HOME/AWAY differences are only small.

Directional topology:
- HAS_DRAW_VOTE n154 DRAW .240
- ONE_WIN_SIDE n4329 DRAW .251
- WIN_SIDE_SPLIT n3211 DRAW .272

core4 confidence:
- .33-.40 DRAW .275
- .40-.45 .265
- .45-.50 .236
- .50-.60 .221
- .60+ .273 (small n)

General result:
stronger favorite normally reduces DRAW.
Therefore No4-like high-confidence draws are candidates for HIDDEN_DRAW research.

#### Step16j — favorite confidence x split
For core4 confidence .45-.60:
split often raises DRAW relative to nonsplit, but NOT consistently by season.

2019 and 2025 reversed the relationship.
Therefore:
`favorite + WIN_SIDE_SPLIT -> DRAW` is NOT a validated rule.

Important distinction:
split is more useful as FAVORITE-FAIL/LOSS warning than as direct DRAW predictor.

#### Step16k — xG2 vs MARKET conflict
Within core4 confidence .45-.60:

- X1 M1: n1596 H .534 D .229 A .237
- X1 M2: n150  H .327 D .247 A .427
- X2 M1: n113  H .416 D .292 A .292
- X2 M2: n183  H .246 D .208 A .546

Interpretation candidate:
- process/xG AND market oppose favorite -> LOSS PATH
- market supports favorite while process/xG opposes -> FAVORITE-FAIL / HIDDEN_DRAW candidate

However generic XG/MARKET conflict DRAW rate is highly unstable by season.
No production rule yet.

### Current research direction
Do NOT optimize thresholds to reproduce No3/No4.

Move to favorite-relative coordinates:
- PROCESS_SUPPORTS_FAV
- PROCESS_OPPOSES_FAV
- MARKET_SUPPORTS_FAV
- MARKET_OPPOSES_FAV

Goal:
- LOSS_PATH: why BASE favorite can lose
- FAVORITE_FAIL: why favorite may fail to win
- DRAW_PATH: conditional on favorite failure, why result stops at DRAW rather than opponent win

Any production use requires causal historical OOF / nested walk-forward validation.

### NEXT STEP
Step16l has NOT yet been executed.

Next:
Step16l = inspect year-by-year reproducibility of directional xg2/market conflict in core4 confidence .45-.60.

After that, convert HOME/AWAY-specific patterns into favorite-relative features before any production rule/model is considered.

Status:
Step13 production analysis COMPLETE.
Step14 disagreement recalibration research COMPLETE.
Step15 No4 audit COMPLETE.
Step16a-k exploratory historical LOSS/DRAW path research COMPLETE.
Step16l NEXT.

---

## Future Architecture — MATCH KARTE / 100K Simulation Project

### Vision
TOTO LABOの次期大工程として、毎開催の13試合について
「全ソース取得 → 試合カルテ → lineup反映 → simulation → P_final → toto有限予算最適化」
を定型ルーティン化する。

目標は単純な1/0/2予測ではなく、
「なぜその確率になったのか」を説明可能な試合生成モデルを構築すること。

### Source Inventory Project
近々、現在利用している全データを棚卸しする。

対象:
- FootyStats
- toto One
- Jリーグ公式
- Football LAB
- Fantasy系 player parameter
- Sportsnavi
- サッカー批評Web
- その他追加可能なprematch source

棚卸しは単なるcolumn一覧ではなく、各データについて以下を定義する。

1. WHAT: 何を表すデータか
2. WHEN: kickoff前のいつ取得可能か
3. SEMANTIC: どの意味familyに属するか
4. KARTE ROLE: 試合カルテの何に使うか
5. SIM ROLE: simulationの何を動かす候補か
6. HISTORY: historical causal dataが存在するか
7. OOF: historical OOFで有効性を確認できるか
8. PRODUCTION STATUS: research-only / validated / production

原則:
「取れる情報は広く取る、使うときは絞る。」
取得したからproduction probabilityへ投入する、とはしない。

### MATCH KARTE FEATURE DICTIONARY
全データを最終的に以下のような試合構造へ整理する。

- TEAM POWER
- PLAYER / LINEUP POWER
- ATTACK PROCESS
- DEFENSIVE RISK
- FINISHING
- BUILD UP
- WIDTH / CARRY
- RECOVERY
- DEFENSIVE LAST LINE
- FORM
- MATCHUP
- ABSENCE / RETURN
- TACTICAL CONTEXT
- MARKET
- LOSS PATH
- FAVORITE-FAIL PATH
- DRAW PATH

FootyStats / Football LAB等で同名metricでもsemantic populationが違う場合は統合せず保持する。

### Player / Lineup Layer
スタメン予想または確定スタメン取得後、
Football LAB player stats / CBP、Fantasy系player parameter等を利用して
当日の実戦戦力を再計算する構想。

単純な「主力欠場=-X点」ではなく、
選手変更による影響を可能な範囲で、

- attacking power
- finishing
- build-up
- progression
- recovery
- defensive power
- last-line defense
- set piece
- role / position

等へ分解する。

予想スタメン時点と確定スタメン時点で再計算可能な設計を目指す。

### News / Editorial Layer
toto One / Sportsnavi / サッカー批評Web / Jリーグ記事等は
原則として独立model voteとして直接加算しない。

記事からEVENTを抽出する。

候補:
- INJURY
- SUSPENSION
- RETURN
- LINEUP_CHANGE
- FORMATION_CHANGE
- ROTATION
- FATIGUE
- ROLE_CHANGE
- TACTICAL_MISMATCH
- PLAYER_FORM
- MANAGER_INTENT

同一事象を複数媒体が報じても複数票にしない。

基本構造:
ONE EVENT_ID
+ multiple source
+ source confidence
+ publication time
+ prematch cutoff
+ affected team/player/role

既存のJLeague/Sportsnavi cross-source dedupe思想を拡張する。

### MATCH ENGINE
試合カルテから直接1/0/2だけを出すのではなく、
試合生成に必要なlatent parameterを作る構想。

候補:
- HOME attacking strength
- AWAY attacking strength
- HOME defensive vulnerability
- AWAY defensive vulnerability
- expected goals / scoring intensity
- tempo
- finishing variance
- defensive collapse / tail risk
- clean-sheet probability
- draw resistance
- favorite survival probability

LOSS PATH / FAVORITE-FAIL / DRAW PATH研究をMATCH ENGINE設計へ接続する。

### 100K Simulation
最終目標:
13試合それぞれを100,000回simulationする。

出力候補:
- P(HOME)
- P(DRAW)
- P(AWAY)
- score distribution
- top scorelines
- HOME/AWAY 2+ goals
- clean sheet
- BTTS
- total goals
- favorite survival
- favorite fail
- LOSS PATH probability
- DRAW PATH probability
- upset/tail probability

重要:
100,000回回すこと自体は精度向上を保証しない。
入力モデルとparameter calibrationが正しくなければ、
誤った試合を100,000回生成するだけである。

したがってsimulation parameterもhistorical OOF validationを必須とする。

### Future Routine
毎開催の理想ルーティン:

1. DATA ACQUISITION
   全prematch sourceを取得

2. NORMALIZE / SEMANTIC
   normalization / semantic separation / event dedupe

3. MATCH KARTE
   13試合の構造診断

4. LINEUP UPDATE
   予想スタメン → 確定スタメンでplayer power更新

5. MATCH ENGINE
   simulation parameter生成

6. 100K SIMULATION
   13試合 × 100,000回

7. CALIBRATION
   historical OOFでsimulation outputを較正

8. P_final
   1/0/2 + score distribution + LOSS/DRAW/FAVORITE-FAIL paths

9. TOTO OPTIMIZER
   96口 / 144口等の有限予算最適化

10. POSTMORTEM
    simulation vs actualを比較し、
    見落としたLOSS PATH / DRAW PATH / tail riskを記録する。

### Learning Loop
開催終了後は単なる的中率だけで評価しない。

例:
- G大阪 0-2 FC東京
  -> なぜFC東京2+ goals tailを十分評価できなかったか
  -> LOSS PATHのどのfeatureを見落としたか

- 町田 1-1 横浜FM
  -> なぜfavorite-failをDRAW PATHへ変換できなかったか
  -> 「勝ち切れない理由」を事前特徴から検出できたか

毎開催、
prediction -> simulation -> actual -> structural error
を蓄積する。

### Production Principle
- totoLABO AI / validated historical modelをprimaryとする。
- external sourceは意味を保存して広く取得する。
- correlated informationを独立voteとして数えない。
- news duplicationを複数voteにしない。
- no historical validation = research-only.
- post-outcome informationをprematch featureへ混入しない。
- thresholdを特定試合の結果に合わせて最適化しない。
- simulation導入後もwalk-forward / OOF / holdout原則を維持する。

### Roadmap Position
直近作業は変更しない。

NEXT:
Step16l — xG2 × MARKET directional conflictの年別再現性検証。

その後:
favorite-relative feature化
-> LOSS PATH
-> FAVORITE-FAIL
-> DRAW PATH
のhistorical validationを進める。

Step16系が一定のcheckpointに達した後、
次期大工程として
「ALL SOURCE INVENTORY -> MATCH KARTE FEATURE DICTIONARY」
を開始する。

Status:
MATCH KARTE / 100K Simulation = FUTURE ARCHITECTURE APPROVED FOR PLANNING.
Not yet production.

---

## 2026-09-14 SESSION UPDATE — STEP17-19b

### STEP17 — SUPPORTED FAVORITE / DOMINANCE WEAKNESS COMPLETE

Goal:
- Investigate FAVORITE-FAIL among supported favorites.
- Avoid post-hoc No4-specific rules.
- Historical prematch-only + walk-forward validation required.

Supported-favorite population:
- core4 favorite = HOME/AWAY
- favorite_confidence = 0.45-0.55
- MARKET supports same favorite (market_opposition=0)
- N=1435
- FAV_WIN=53.80%
- DRAW=23.28%
- OPP_WIN=22.93%
- Favorite-Fail=46.20%

DOMINANCE_WEAKNESS:
- Defined historically using favorite-relative FootyStats Pre-Match xG edge.
- xg_edge = favorite Pre-Match xG - opponent Pre-Match xG.
- Favorite-Fail xg_edge lower than Favorite-Win in all 6 inspected years.
- FAIL-WIN xg_edge:
  2020 -0.037
  2021 -0.084
  2022 -0.049
  2023 -0.007
  2024 -0.032
  2025 -0.060

Quartile audit:
- Q1 low xG edge Favorite-Fail=52.1%
- Q2=47.3%
- Q3=43.8%
- Q4 high xG edge=39.6%
- Q1 vs Q4 Favorite-Fail delta positive 6/6 years.

Walk-forward:
- confidence + xg_edge improved LL/Brier 4/5 test years.
- xg_edge coefficient negative 5/5.
- Adding MARKET favorite probability reduced incremental gain:
  improvement 3/5 years, coefficient still negative 5/5.
- DOM_RESID complexity was weaker than simple xg_edge and rejected.

Formal artifact:
data/evaluation/dominance_weakness_oof_2021_2025_v01.csv
- rows=1187
- NULL=0
- xG_edge coefficient negative 5/5.

dominance_lift ranking:
- Top10% Favorite-Fail=51.3%
- population Favorite-Fail=45.2%
- Q4 vs OTHER delta positive 4/5 years.
- 2023 exception.

2023 regime:
- Supported Favorite-Fail=53.6%, highest inspected year.
- FAIL-WIN xg_edge=-0.007.
- dominance_lift quartiles nearly flat.
- Interpretation:
  many supported favorites failed in 2023, but DOMINANCE_WEAKNESS
  was not the principal failure path.

Status:
DOMINANCE_WEAKNESS =
HISTORICAL OOF-SUPPORTED AUXILIARY FAVORITE-FAIL FEATURE.

NOT:
- direct DRAW feature
- production threshold
- universal Favorite-Fail explanation.

Do not optimize retrospective Q1/Top10 thresholds.

1653 / No4:
- Historical FootyStats Pre-Match xG semantic is not available
  in acquired 1653 RAW/normalized data.
- venue_xG and matchup_xG are different semantics.
- Do NOT substitute them.
- No4 remains SEMANTIC_NOT_MATCHED for DOMINANCE_WEAKNESS.

Rejected DRAW decomposition:
- LOW_ATTACK + LOW_EDGE -> DRAW was not stable.
- xG dominance remains Stage-A Favorite-Fail semantic only.


### STEP18 — FAVORITE-FAIL PATH DECOMPOSITION COMPLETE

Candidate audit:

1. DOMINANCE_WEAKNESS
- Pre-Match xG edge FAIL-WIN negative 6/6.
- Historical OOF support established.
- KEEP as auxiliary Favorite-Fail route.

2. PPG edge
- sign stable only 4/6.
- NOT PROMOTED.

3. LOW_SCORING_FAVORITE_RISK / Over2.5 odds
- FAIL-WIN direction positive 6/6.
- However incremental walk-forward after
  favorite_confidence + MARKET favorite strength:
  LL 0.668965 -> 0.670844
  Brier 0.238030 -> 0.239001
  LL improvement 2/5
  Brier improvement 2/5
  OU coefficient positive 5/5.
- REJECT as Stage-A predictive feature.
- Important:
  O/U remains historically useful in Stage-B
  DRAW vs OPP_WIN.

4. BTTS odds
- sign 3/6.
- NOT PROMOTED.

5. Causal rolling defensive vulnerability, previous 5 matches
- R_GA positive 4/6
- R_XGA positive 3/6
- R_SA positive 3/6
- R_SOTA positive 4/6
- insufficient stability.
- REJECT simple rolling defensive profile.

6. Favorite defense x opponent rolling attack
- XG_PRESS positive 2/6
- SOT_PRESS positive 2/6
- SHOT_PRESS positive 3/6
- GOAL_PRESS positive 2/6
- REJECT simple rolling matchup-pressure path.
- Do NOT retrospectively optimize rolling windows.

2023:
- high Supported-Favorite failure remains incompletely explained.
- DOMINANCE_WEAKNESS nearly disappears.
- simple rolling defense/opponent attack does not explain regime.
- Do not search specifically for a feature merely to fit 2023.

Current Favorite-Fail architecture:

FAVORITE_FAIL_PATH
  A. MARKET opposition
     - historically strong general route.
  B. DOMINANCE_WEAKNESS
     - OOF-supported auxiliary route for MARKET-supported favorites.
  C. PPG / Stage-A O-U / BTTS / simple rolling defense
     - rejected or not promoted.

Stage separation remains mandatory:

FAVORITE_FAIL
  -> DRAW_PATH
  -> LOSS_PATH

Same feature can have different semantic value by stage.
Example:
- O/U rejected for Stage A Favorite-Fail.
- O/U historically supported for Stage B DRAW vs OPP_WIN.

Sign consistency alone is insufficient.
Walk-forward LL/Brier validation required.

Rejected paths must not be resurrected through
retrospective threshold/window tuning.


### DRAW / LOSS PATH CURRENT STATUS

Formal DRAW PATH:
data/evaluation/draw_path_oof_2020_2025_v02.csv

Market-v2:
- Stage A:
  favorite_confidence + MARKET opposition
  -> Favorite-Fail.
- Stage B:
  O/U + MARKET opposition + interaction
  -> DRAW vs OPP_WIN.
- Final residual recalibration candidate.
- Historical OOF research support.
- NOT production yet.

Formal LOSS PATH:
data/evaluation/loss_path_oof_2020_2025_v01.csv

LOSS_PATH:
- strong/stable favorite-relative opponent-win ranking signal.
- Q4 substantially stronger than Q1.
- LOSS branch more stable than DRAW branch.

1653 blind audit:
- No7 was #1 DRAW-LIFT and actual DRAW.
- No8 was LOSS-side relative to No7 and actual opponent win.
- No4 remained a blind spot.
- Do not overclaim single-round confirmation.


### STEP19 — MATCH KARTE DATA INVENTORY IN PROGRESS

Purpose:
Build the source-to-simulation specification for future routine:

ACQUIRE
-> NORMALIZE / SEMANTIC
-> MATCH KARTE
-> LINEUP UPDATE
-> MATCH ENGINE
-> 100,000 SIMULATIONS PER MATCH
-> CALIBRATION
-> P_final
-> FINITE-BUDGET TOTO OPTIMIZER
-> POSTMORTEM LEARNING LOOP

Simulation principle:
100,000 simulations do NOT improve a wrong input model.
All simulation parameters require historical OOF/calibration
before production use.

Every source datum should eventually have:
- WHAT
- WHEN / temporal availability
- SEMANTIC
- MATCH KARTE ROLE
- SIMULATION ROLE
- HISTORICAL availability
- OOF status
- PRODUCTION status.


### STEP19a — DATA ASSET INVENTORY COMPLETE

Asset counts:

FOOTYSTATS
- files 209
- CSV 137
- HTML 59
- JSON 2

FS_RAW
- files 478
- CSV 35
- HTML 342
- JSON 1

FS_ANALYSIS
- files 240
- CSV 222
- JSON 14

FOOTBALL_LAB
- files 22
- CSV 1
- HTML 20
- JSON 1

JLEAGUE
- files 127
- CSV 13
- HTML 111
- JSON 2

SPORTSNAVI
- files 46
- CSV 5
- HTML 40
- JSON 1


### STEP19b — CSV SCHEMA FAMILY INVENTORY COMPLETE

Important FootyStats schema families:

MATCHES
- 32 files
- 11813 rows
- 66 columns
- single schema.

PLAYERS
- 24 files
- 15966 rows
- 271 columns
- single schema.

TEAMS
- 28 files
- 549 rows
- 293 columns
- single schema.

TEAMS2
- 22 files
- 434 rows
- 442 columns
- single schema.

LEAGUE
- 29 files
- 71 columns
- single schema.

2026 FS_RAW also contains:
- MATCHES 12 files / 3424 rows / 66 cols
- PLAYERS 4 / 2386 / 271
- TEAMS 10 / 284 / 293
- TEAMS2 1 / 20 / 442.

Primary role separation:

FootyStats MATCHES
-> historical causal / OOF / calibration backbone.

FootyStats PLAYERS
-> future lineup and player-power candidate.
-> temporal semantics must be audited before historical use.

FootyStats TEAMS / TEAMS2
-> rich current-round MATCH KARTE candidates.
-> season aggregates.
-> DO NOT join season-final values directly to historical matches.

Football LAB
-> process / build-up / width / finishing / recovery /
   defensive-last-line candidates.
-> currently mostly 2026; historical OOF availability unresolved.

JLeague / Sportsnavi
-> EVENT / availability / absence / return /
   lineup / tactical-context layers.

ANALYSIS
-> derived artifacts.
-> must not be confused with raw independent sources.


### FUTURE MATCH KARTE BLOCKS

Planned semantic blocks:

TEAM_POWER
PLAYER_LINEUP_POWER
ATTACK_PROCESS
DEFENSIVE_RISK
FINISHING
BUILD_UP
WIDTH_CARRY
RECOVERY
DEFENSIVE_LAST_LINE
FORM
MATCHUP
ABSENCE_RETURN
TACTICAL_CONTEXT
MARKET
FAVORITE_FAIL_PATH
DOMINANCE_WEAKNESS
DRAW_PATH
LOSS_PATH

News/editorial:
Do NOT count articles as independent votes.

Normalize to EVENT_ID such as:
INJURY
SUSPENSION
RETURN
LINEUP_CHANGE
FORMATION_CHANGE
ROTATION
FATIGUE
ROLE_CHANGE
TACTICAL_MISMATCH
PLAYER_FORM
MANAGER_INTENT

Same real-world event across media:
one EVENT_ID + multiple source/confidence/publish-time fields.


### FUTURE 100K MATCH ENGINE

Candidate latent parameters:

- home attacking strength
- away attacking strength
- defensive vulnerability
- scoring intensity
- tempo
- finishing variance
- collapse/tail risk
- clean-sheet probability
- draw resistance
- favorite survival / fail

Candidate simulation outputs:

- P(HOME/DRAW/AWAY)
- score distribution
- top scorelines
- BTTS
- totals
- clean sheets
- 2+ goal probabilities
- FAVORITE_SURVIVAL
- FAVORITE_FAIL
- DRAW_PATH
- LOSS_PATH
- upset/tail probabilities

All require historical OOF/calibration before production.


### PRODUCTION SAFETY RULES — CURRENT

- totoLABO AI remains primary.
- External sources are research/warning layers unless OOF promoted.
- MARKET is not a generic independent vote.
- correlated process metrics are not independent votes.
- MATCHUP_XG is algebraic/recombined information, not independent.
- no missing-data fabrication.
- no semantic substitution between differently defined xG fields.
- no post-outcome feature reconstruction presented as prematch evidence.
- no retrospective threshold/window tuning after seeing outcomes.
- warning validity != automatic ticket expansion.
- production portfolio remains probability-based finite-budget optimization
  until validated recalibration is promoted.
- rejected research paths remain rejected unless tested under a genuinely
  new prespecified hypothesis/data layer.


### CURRENT PRODUCTION 1653 REFERENCE

Production baseline96 selection was:

12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 12 / 2 / 102

IMPORTANT:
This is NOT identical to the earlier pre-deadline reference ticket.

Earlier reference:
12 / 12 / 12 / 1 / 1 / 1 / 1 / 1 / 2 / 12 / 102 / 2 / 12

Difference:
- current production: No11 double, No13 triple.
- earlier reference: No11 triple, No13 double.


### NEXT RESTART POINT

NEXT:
STEP19c — FootyStats MATCH KARTE semantic inventory.

Planned Step19c:
- classify MATCHES / PLAYERS / TEAMS / TEAMS2 columns into semantic blocks.
- do NOT print all 271/293/442 columns.
- summarize block counts + representative fields.
- overlapping regex classification is diagnostic only.

After Step19c:
- assign each semantic block:
  HISTORICAL_CAUSAL
  CURRENT_ONLY
  OOF_SUPPORTED
  RESEARCH_ONLY
  PRODUCTION_STATUS

Then:
- inventory Football LAB semantics.
- inventory JLeague / Sportsnavi / Soccerhihyo EVENT semantics.
- design unified MATCH KARTE schema.
- audit player/lineup temporal availability.
- design calibrated match engine and 100K simulation inputs.

SESSION END:
2026-09-14
Step17 COMPLETE.
Step18 COMPLETE.
Step19a-b COMPLETE.
Resume from Step19c.


## UPDATE: 2026-09-14 / STEP19c-20z / TOTO1654 PREPARATION

### STEP19c DATA INVENTORY DETAIL — COMPLETE
- FootyStats historical/current schema inventory completed.
- MATCHES: 66 cols. Historical causal/OOF core source.
- PLAYERS: 271 cols. Rich playing-time / goal / shot / pass / carry / defense / keeper data; promising PLAYER_LINEUP_POWER source.
- TEAMS: 293 cols.
- TEAMS2: 442 cols.
- Step19c regex family classification is diagnostic only.
- Large BTTS_OU counts in PLAYERS/TEAMS2 are regex overmatch and MUST NOT be treated as semantic truth.
- Precise semantic mapping is required before MATCH KARTE production use.

### TOTO1654 ROUND
Frozen 13-match manifest:
- data/config/toto_rounds/1654.csv
- 13/13 matches
- home_url / h2h_url / away_url ready
- H2H unique 13/13
- JLeague internal match IDs intentionally deferred; FootyStats acquisition does not depend on them.

### STEP20 FOOTYSTATS 1654 ACQUISITION PREPARATION
- Local DB initially had no toto1654 rows / current JLeague match IDs.
- Team FootyStats URLs resolved for all 13 matches.
- H2H URLs resolved 13/13 using team-page discovery plus local historical HTML/DB evidence.
- During discovery FootyStats returned HTTP 429 after multiple requests.
- Policy: DO NOT bypass rate limits. 429 means unknown/not-yet-fetched, not missing.
- Conservative delays and resumable acquisition required.
- Old keyword-only Cloudflare/block detection was found too sensitive; valid large HTML can contain such strings.

### GENERIC FOOTYSTATS COLLECTOR v02 — COMPLETE
Created:
- scripts/fetch_footystats_round_3html_v02.py

Design:
- manifest-driven
- generic --round
- no ROUND1653 hardcoding
- no JLeague ID requirement
- Home -> H2H -> Away
- resumable existing-file SKIP
- session rotation retained
- conservative delay retained
- preserve downloaded files on failure
- output: data/raw/footystats/round_html/<round>/

Validation:
- py_compile PASS
- toto1654 No01 福岡 vs 広島:
  - home 257442 bytes
  - h2h 366407 bytes
  - away 259499 bytes
  - READY 3/3 PASS
- immediate resume test:
  - home/h2h/away all SKIP
  - no GET / WAIT
  - READY 3/3 PASS

### STEP20aa — NOT YET EXECUTED
Remaining toto1654 FootyStats acquisition:
- No02-No13 = 36 new pages
- target total = 39/39
- long conservative delays make this approximately hour-scale work.
- Execute before work / unattended period rather than blocking active analysis time.
- On 429: stop safely and resume later; never force/bypass.

### CURRENT EXECUTION ORDER
Do NOT wait for Step20aa before doing offline analytical work.

Current order:
1. Save STATE.
2. Check latest toto1654-relevant information across:
   - toto official
   - toto ONE
   - FootyStats
   - Football LAB
   - JLeague official
   - Japan national-team related availability/fitness information
   - Sportsnavi
   - サッカー批評Web
   - other directly relevant credible sources
3. Normalize duplicate news into one EVENT_ID; syndicated articles are not independent votes.
4. Design and FREEZE MATCH KARTE v1 before interpreting toto1654 deeply.
5. Run Step20aa during unattended time.
6. Audit FootyStats RAW 39/39.
7. Parse/normalize 1654 with generic pipeline.
8. Populate frozen MATCH KARTE v1.
9. First toto1654 13-match deep dive.
10. Later lineup update -> player power -> calibrated match engine -> 100,000 simulations -> finite-budget optimizer.

### MATCH KARTE v1 PRINCIPLE
Freeze feature semantics before seeing/interpreting toto1654 outcomes or tailoring features to individual 1654 matches.

Separate:
- observed raw values
- semantic normalized values
- derived features
- historically OOF-supported auxiliary features
- research-only/unvalidated features
- news/event information
- lineup/player-power information
- simulation parameters

Every datum should track:
WHAT / WHEN / SOURCE / SEMANTIC / KARTE_ROLE / SIM_ROLE /
HISTORICAL_AVAILABILITY / OOF_STATUS / PRODUCTION_STATUS.

Existing production principle remains:
totoLABO AI primary.
External sources are research/warning/context layers unless historical OOF validation supports production use.

---

## 2026-09-14 AM UPDATE — MATCH KARTE v1 / v1-C RECONSTRUCTION

### Step21 MATCH KARTE v1

Step21a-n COMPLETE.

#### Step21a
MATCH KARTE v1 specification created.

Files:
- `data/config/match_karte/match_karte_v1_spec.json`
- `data/config/match_karte/match_karte_v1_blocks.csv`

18 blocks:
- TEAM_POWER
- PLAYER_LINEUP_POWER
- ATTACK_PROCESS
- DEFENSIVE_RISK
- FINISHING
- BUILD_UP
- WIDTH_CARRY
- RECOVERY
- DEFENSIVE_LAST_LINE
- FORM
- MATCHUP
- ABSENCE_RETURN
- TACTICAL_CONTEXT
- MARKET
- FAVORITE_FAIL_PATH
- DOMINANCE_WEAKNESS
- DRAW_PATH
- LOSS_PATH

Datum contract:
WHAT / WHEN / SOURCE / SOURCE_FRESHNESS / TEMPORAL_CUTOFF /
SEMANTIC / KARTE_ROLE / SIM_ROLE / HISTORICAL_AVAILABILITY /
OOF_STATUS / PRODUCTION_STATUS / EVENT_ID / LINEAGE.

Core principles:
- PREMATCH_ONLY
- NO_POSTHOC_1654_FEATURE_DESIGN
- NO_MISSING_DATA_FABRICATION
- DUPLICATE_NEWS_ONE_EVENT_ID
- SYNDICATION_NOT_INDEPENDENT_VOTE
- SOURCE_SEMANTICS_PRESERVED
- OOF_REQUIRED_FOR_PRODUCTION_PROMOTION
- TOTO_LABO_AI_PRIMARY

#### Step21b
Source map created:
`data/config/match_karte/match_karte_v1_source_map.csv`

22 rows / 9 source families.

Important terminology:
- `source_usage` = source/dataset-level role
- `production_status` = datum-level production gate

#### Step21c
Simulation mapping created:
- `match_karte_v1_sim_map.csv`
- `match_karte_v1_sim_map_meta.json`

Important:
KARTE presence != simulation use.
Unvalidated features must not alter production probabilities.

#### Step21d
Temporal policy created:
- `match_karte_v1_temporal_policy.csv`
- `match_karte_v1_temporal_policy.json`

Rules include:
- published_at <= prediction cutoff
- no post-kickoff stats
- no season-final leakage into historical OOF
- confirmed lineup after cutoff cannot rewrite frozen prior snapshot
- acquisition time != source update time
- no fabricated timestamps

#### Step21e-f
Physical schema and validation policy created.

Three physical tables:
- match
- event
- player

Missing values remain NULL.
UNKNOWN != healthy.
Event presence alone does not imply probability delta.
Absence count != player-strength loss.
MIDWEEK schedule is context only unless OOF validated.

#### Step21g-h
QA passed after renaming source-map field:
`production_status` -> `source_usage`

Final QA:
- ERRORS 0
- WARNINGS 0

#### Step21i
MATCH KARTE v1 formally frozen.

Freeze:
`data/config/match_karte/match_karte_v1_freeze.json`

1654 staging created:
- `data/analysis/match_karte/1654/toto1654_match_karte_v1_staging.csv`
- `data/analysis/match_karte/1654/toto1654_events_v1_staging.csv`
- `data/analysis/match_karte/1654/toto1654_players_v1_staging.csv`

Initial:
- 13 match rows
- 61 match fields
- P_base NULL
- P_final NULL

#### Step21j
1654 match kickoff metadata populated.

Initial freshness:
- JLEAGUE = FRESH
- FOOTYSTATS = UNKNOWN
- FOOTBALL_LAB = STALE
- TOTO_ONE = UNKNOWN

Prediction cutoff remains NULL until prediction snapshot freeze.

#### Step21k
Official/context events populated.

18 unique EVENT_ID:
- player/team events = 13
- MIDWEEK schedule events = 5

Important EVENT_ID lesson:
Multiple players in one article are separate real events and require separate EVENT_ID.
Syndicated reports of one real event share one EVENT_ID with multiple sources.

#### Step21l
Events aggregated into match KARTE.

Player/team event counts exclude MIDWEEK_MATCH.
MIDWEEK stored separately.

Relevant matches:
- No01 福岡-広島: EVENT 0/1
- No02 浦和-東京V: EVENT 0/4
- No03 清水-千葉: EVENT 1/2
- No04 岡山-京都: MIDWEEK away
- No08 町田-柏: EVENT 0/1, MIDWEEK both
- No09 G大阪-神戸: EVENT 1/0, MIDWEEK both
- No11 藤枝-大宮: EVENT 3/0

No probability adjustment applied.

#### Step21m
KARTE coverage audit PASS.

Coverage:
- IDENTITY 100%
- TEMPORAL 50% because prediction_cutoff intentionally NULL
- SOURCE_FRESHNESS 100% state-labeled
- EVENT_CONTEXT 100%
- BASE_PROB 0%
- FINAL_PROB 0%
- LINEUP 0%
- SIM_OUTPUT 0%

Expected NULL confirmed:
- P_base 13/13
- P_final 13/13
- prediction_cutoff 13/13

#### Step21n
1654 acquisition checklist frozen.

Files:
- `data/config/match_karte/toto1654_acquisition_checklist_v1.csv`
- `data/config/match_karte/toto1654_acquisition_checklist_v1.json`

20 tasks.
HIGH priority = 13.

Main remaining acquisition:
- FootyStats 1654 full RAW
- FootyStats parse / normalize / freshness audit
- Football LAB refresh check
- JLeague/JFA updates
- toto ONE 1654
- Sportsnavi
- Soccerhihyo
- expected / confirmed lineup

### Step20aa still pending

FootyStats generic collector:
`scripts/fetch_footystats_round_3html_v02.py`

No1 already acquired 3/3 and resume QA passed.

Remaining:
36 new pages for No2-No13.

Run unattended:
`python scripts/fetch_footystats_round_3html_v02.py --round 1654 --manifest data/config/toto_rounds/1654.csv --limit 13`

Target:
READY 39/39.

On HTTP 429:
STOP and resume later.
Do not bypass.

---

## Step22 — production baseline v1-C reconstruction

Purpose:
Recover existing production baseline exactly before generating Round1654 P_base.

Do NOT create a similar/new model.
1650/1653 saved production outputs must be reproduced first.

### Step22a-d

Repository search showed current scripts only consume the v1-C output.

Original v1-C writer/generator source code is no longer present in current `scripts/` or `src/`.

1650 report exists:
`data/analysis/toto1650_score_model_v1c_report.json`

Key metadata:
- model = score_model_v1c_stacked
- stage1_training_rows = 8742
- stage1_training_seasons = 2018-2025
- stage1_alpha = 0.2
- meta_training_rows = 4502
- meta_alpha = 0.0
- FootyStats source =
  `data/features/footystats_csv_prediction_features_2026_redownload_v2.csv`

### Step22e

1650 production meta coefficients recovered:

Home:
- intercept = 0.02114971325203815
- coefficients =
  0.35383403609678693
  0.4561876384370998
  -0.11076783232877811

Away:
- intercept = 0.06613697596141004
- coefficients =
  0.47879950558174084
  -0.17400639879996502
  0.3386047860389035

### Step22f-g

OOF artifacts found:
- `data/evaluation/score_model_v1c_stacked_oof_predictions_2023_2025.csv`
- `data/evaluation/score_model_v1c_stacked_oof_meta_coefficients_2023_2025.csv`
- `data/evaluation/score_model_v1c_stacked_oof_regeneration_audit_2023_2025.csv`

OOF prediction rows:
3428 x 53.

Relevant pipeline fields:
- lambda_home_base
- lambda_away_base
- ms_p_home
- ms_p_draw
- ms_p_away
- lambda_home_final
- lambda_away_final
- score_p_home
- score_p_draw
- score_p_away

Historical regeneration audit demonstrates saved and regenerated 1X2 outputs are effectively identical.

### Step22h

OOF meta coefficients reveal exact feature semantics:

Home meta inputs:
- log(lambda_home_base)
- log(ms_p_home / ms_p_draw)
- log(ms_p_away / ms_p_draw)

Away meta inputs:
- log(lambda_away_base)
- log(ms_p_home / ms_p_draw)
- log(ms_p_away / ms_p_draw)

Production prediction files:
- `data/predictions/score_model_v1c_stacked_toto1650.csv`
- `data/predictions/score_model_v1c_stacked_toto1653.csv`

### Step22i-j — META LAYER FULLY RECONSTRUCTED

Exact production formula recovered:

xh = log(ms_p_home / ms_p_draw)
xa = log(ms_p_away / ms_p_draw)

lambda_home_final =
exp(
    home_intercept
    + home_coef[0] * log(lambda_home_base)
    + home_coef[1] * xh
    + home_coef[2] * xa
)

lambda_away_final =
exp(
    away_intercept
    + away_coef[0] * log(lambda_away_base)
    + away_coef[1] * xh
    + away_coef[2] * xa
)

1650 13-match reconstruction QA:

- rows = 13
- MAX_DIFF_HOME = 2.220446049250313e-16
- MAX_DIFF_AWAY = 1.1102230246251565e-16
- MEAN_DIFF_HOME = 1.708035422500241e-17
- MEAN_DIFF_AWAY = 8.540177112501205e-18

Result:
`META_FORMULA EXACT`

Therefore v1-C META layer is fully reconstructed and no longer a black box.

### Remaining v1-C reconstruction

Still unresolved:
1. Stage1:
   generation of `lambda_home_base / lambda_away_base`

2. Match Strength layer:
   generation of `ms_p_home / ms_p_draw / ms_p_away`

Do not generate 1654 P_base until both are reproduced and validated.

### ABSOLUTE NEXT STEP — Step22k

Audit:
`data/features/footystats_csv_prediction_features_2026_redownload_v2.csv`

Join it to:
`data/predictions/score_model_v1c_stacked_toto1650.csv`

Goal:
identify exact Stage1 inputs responsible for:
- lambda_home_base
- lambda_away_base

Then reconstruct Stage1 and Match Strength.

Required validation order:
1650 exact reproduction
-> 1653 exact reproduction
-> generic v1-C builder
-> Round1654 P_base generation.

### Current project position

MATCH KARTE v1:
FROZEN / READY.

Round1654:
metadata + official event context staged.
Probabilities intentionally still NULL.

v1-C:
META layer = EXACTLY RECONSTRUCTED.
Stage1 + Match Strength = NEXT.

Production rule remains:
Historical OOF validation first.
No newly acquired source feature may alter P_final without validation.


## 2026-09-14 STEP20 UPDATE — TOTO1654 FootyStats acquisition pipeline COMPLETE

### Step20aa — Full FootyStats acquisition
- Round 1654 manifest-driven fetch completed.
- RAW HTML READY 39/39.
- 13 matches x {home, h2h, away}.
- No 429 termination.
- Final fetch log ended with:
  - READY 39/39
  - DONE

### Step20ab — RAW integrity
- FILES 39
- SMALL_LT10KB 0
- home 13 / h2h 13 / away 13
- BAD_MATCH_SETS 0
- PASS

### Step20ac–ae — FULL RAW parser
- Existing v01 was round-1653 hardcoded.
- Created generic:
  scripts/parse_footystats_round_full_v02.py
- Manifest-driven round definition.
- Round 1654 parsed successfully.
- FULL RAW JSON 13/13.
- BAD_PAGE_SETS 0.

Output:
data/parsed/footystats/toto1654_full_v02/

### Step20af — parser structure audit
Round 1654 table patterns:
- home: {8: 9, 51: 4}
- h2h: {36: 13}
- away: {8: 10, 51: 3}

Round 1653 showed the same mixed 8-table / 51-table structural families.
Therefore No10–13 structure was not treated as acquisition failure.

### Step20ag–aj — NORMALIZED
- Existing normalize v04 was round-1653 hardcoded.
- Created generic:
  scripts/normalize_footystats_round_v05.py

Output:
data/analysis/footystats_toto1654_normalized_v05.csv

QA:
- ROWS 13
- COLS 65
- schema identical to 1653 v04
- required venue xG/xGA NULL 0
- all primary venue xG/xGA values passed sanity checks
- PASS

### Step20ak–al — FEATURE BLOCK
Existing builder already round-generic:
scripts/build_footystats_feature_blocks_v02.py

Output:
data/analysis/footystats_toto1654_feature_blocks_v02.csv

QA:
- 13 x 93
- schema identical to 1653
- required matchup_xg fields present
- PASS

### Step20am–ao — SEMANTIC
Existing semantic v03 was round-generic but fixed to normalized_v04 and FULL RAW v01 paths.
Created/patched:
scripts/build_footystats_feature_semantic_v04.py

Changes:
- external normalized path
- external blocks path
- external raw-root path
- FULL RAW per-match version auto-detection

Output:
data/analysis/footystats_toto1654_feature_semantic_v04.csv

QA:
- ROWS 13
- COLS 69
- schema identical to 1653 semantic v03
- NULL_CELLS_1654 240
- explicit venue detail available 3/13
- xG crosscheck mismatch 0
- semantic splits NONE
- PASS

### STEP20 final status
TOTO1654 FootyStats pipeline:
RAW 39/39
-> FULL RAW 13/13
-> NORMALIZED 13x65
-> FEATURE BLOCK 13x93
-> SEMANTIC 13x69

STEP20aa–20ao COMPLETE.

### Next
Populate MATCH KARTE v1 with validated 1654 FootyStats fields.
Then continue remaining current-source acquisition / lineup-player power / exact v1-C reconstruction and simulation workflow.

## Step22 v1-C exact reconstruction COMPLETE

1650 saved production output was reproduced end-to-end.

Confirmed Stage1 v1-Bxg contract:
- training dataset: data/features/score_training_v1b.csv
- training rows: 8,742
- 32 features
- J.League base pre-match features + FootyStats HOME/AWAY pre-match xG
- jl_home_rest_days / jl_away_rest_days clipped upper=30
- SimpleImputer(strategy="median")
- StandardScaler
- separate HOME/AWAY PoissonRegressor
- alpha=0.20
- tol=1e-8
- production FootyStats xG source must use the nonzero redownload source

Confirmed Stage2:
- stacked Poisson meta model
- saved coefficients/intercepts reproduced exactly

Confirmed score engine:
- independent Poisson
- score grid 0..8
- 9x9 score matrix
- normalize matrix by total probability mass before deriving outputs
- 1X2 from normalized matrix
- score ranking probability descending
- top_score = rank1

Step22au 1650 end-to-end validation:
- lambda_home_base max diff: 2.220446049250313e-16
- lambda_away_base max diff: 2.220446049250313e-16
- lambda_home_final max diff: 2.220446049250313e-16
- lambda_away_final max diff: 2.220446049250313e-16
- score_p_home max diff: 1.110223024625157e-16
- score_p_draw max diff: 1.387778780781446e-16
- score_p_away max diff: 1.387778780781446e-16
- top_score_prob max diff: 8.326672684688674e-17
- top_score mismatch: 0

Conclusion:
- score_model_v1c_stacked architecture is exactly reconstructed.
- Exact reproduction gate for building Round1654 P_base is PASS.

## Step23 Round1654 P_base COMPLETE

Round1654 official toto card:
- DB registration: 13/13
- unique J.League IDs: 13/13

J.League pre-match features:
- data/features/jleague_pre_match_features_toto1654.csv
- target coverage: 13/13
- leak-safe builder
- prediction-season 2026

Round1654 RAW multisource:
- data/predictions/multisource_premarket_predictions_2026_toto1654.csv
- data/models/multisource_premarket_model_2026_toto1654.joblib
- data/reports/multisource_premarket_report_2026_toto1654.json
- rows: 13
- weights:
  - FootyStats 0.00
  - Team2 0.20
  - J.League 0.10
  - Elo 0.70
- probability sums validated
- no missing probabilities

Generic v1-C builder:
- scripts/build_score_model_v1c_round_v01.py
- Stage1 contract from Step22 exact reconstruction
- Stage2 stacked meta exact
- normalized 0..8 independent Poisson score matrix
- score rank 1..10

Regression test:
- rebuilt Round1650 from generic builder
- MAX_NUM_DIFF = 1.1102230246251565e-16
- SCORE_MISMATCH = 0
- PASS

Round1654 P_base output:
- data/predictions/score_model_v1c_stacked_toto1654.csv

P_base:
1 福岡 vs 広島     0.2697 / 0.2582 / 0.4722
2 浦和 vs 東京V   0.4858 / 0.2495 / 0.2647
3 清水 vs 千葉     0.4543 / 0.2675 / 0.2782
4 岡山 vs 京都     0.3745 / 0.2722 / 0.3533
5 FC東京 vs 名古屋 0.4733 / 0.2555 / 0.2712
6 長崎 vs C大阪    0.4147 / 0.2684 / 0.3170
7 横浜FM vs 水戸   0.4399 / 0.2611 / 0.2990
8 町田 vs 柏       0.3952 / 0.2699 / 0.3349
9 G大阪 vs 神戸    0.3777 / 0.2762 / 0.3460
10 山形 vs 富山    0.5194 / 0.2408 / 0.2398
11 藤枝 vs 大宮    0.3267 / 0.2718 / 0.4015
12 新潟 vs 磐田    0.3710 / 0.2799 / 0.3491
13 甲府 vs 徳島    0.3354 / 0.2808 / 0.3838

Conclusion:
- Round1654 production P_base is ready.
- Next stage is MATCH KARTE integration and P_final construction.

## Step24 Round1654 MATCH KARTE / P_final Initial Freeze COMPLETE

MATCH KARTE:
- data/analysis/match_karte/1654/toto1654_match_karte_v1_staging.csv
- P_base injected 13/13
- P_final initialized 13/13
- MAX_FINAL_BASE_DIFF = 0.0

Context coverage:
- event present: 6/13
- lineup_strength/status: currently unavailable
- source freshness populated
- no event-derived production probability delta applied

Adjustment audit:
WARNING_ONLY:
- No1 福岡 vs 広島
- No2 浦和 vs 東京V
- No3 清水 vs 千葉
- No8 町田 vs 柏

ADJUST_CANDIDATE but NO_VALIDATED_DELTA:
- No9 G大阪 vs 神戸
- No11 藤枝 vs 大宮

STRUCTURAL_RISK / TICKET_LAYER_ONLY:
- No4 岡山 vs 京都
- No12 新潟 vs 磐田
- No13 甲府 vs 徳島

NO_ACTION:
- No5 FC東京 vs 名古屋
- No6 長崎 vs C大阪
- No7 横浜FM vs 水戸
- No10 山形 vs 富山

Production adjustment gate:
- allowed probability deltas: 0/13
- source disagreement remains warning/routing signal only
- event information has no OOF-validated numeric delta
- structural risk is handled in ticket allocation, not P_final

Production probability:
P_final = P_base for all 13 matches.

Next:
Step25 100,000 simulation and finite-budget ticket optimization.

## 2026-09-15 SESSION UPDATE

### Step23 Round1654 P_base COMPLETE
Round1654 official toto card:
- DB registration: 13/13
- unique J.League IDs: 13/13

J.League pre-match features:
- data/features/jleague_pre_match_features_toto1654.csv
- target coverage: 13/13
- leak-safe builder
- prediction-season 2026

Round1654 RAW multisource:
- data/predictions/multisource_premarket_predictions_2026_toto1654.csv
- data/models/multisource_premarket_model_2026_toto1654.joblib
- data/reports/multisource_premarket_report_2026_toto1654.json
- rows: 13
- weights:
  - FootyStats 0.00
  - Team2 0.20
  - J.League 0.10
  - Elo 0.70
- probability sums validated
- no missing probabilities

Generic v1-C builder:
- scripts/build_score_model_v1c_round_v01.py
- exact Step22 Stage1 / Stage2 contract reused
- Round1650 regression:
  - MAX_NUM_DIFF = 1.1102230246251565e-16
  - SCORE_MISMATCH = 0
  - PASS

Round1654 P_base:
1 福岡 vs 広島       0.2697 / 0.2582 / 0.4722
2 浦和 vs 東京V     0.4858 / 0.2495 / 0.2647
3 清水 vs 千葉       0.4543 / 0.2675 / 0.2782
4 岡山 vs 京都       0.3745 / 0.2722 / 0.3533
5 FC東京 vs 名古屋   0.4733 / 0.2555 / 0.2712
6 長崎 vs C大阪      0.4147 / 0.2684 / 0.3170
7 横浜FM vs 水戸     0.4399 / 0.2611 / 0.2990
8 町田 vs 柏         0.3952 / 0.2699 / 0.3349
9 G大阪 vs 神戸      0.3777 / 0.2762 / 0.3460
10 山形 vs 富山      0.5194 / 0.2408 / 0.2398
11 藤枝 vs 大宮      0.3267 / 0.2718 / 0.4015
12 新潟 vs 磐田      0.3710 / 0.2799 / 0.3491
13 甲府 vs 徳島      0.3354 / 0.2808 / 0.3838


### Step24 MATCH KARTE / P_final initial freeze COMPLETE
MATCH KARTE:
- data/analysis/match_karte/1654/toto1654_match_karte_v1_staging.csv
- P_base injected: 13/13
- P_final initialized: 13/13
- MAX_FINAL_BASE_DIFF = 0.0

Context coverage:
- event present: 6/13
- lineup_strength/status: not yet populated
- source freshness populated
- event-derived numeric probability delta NOT approved

Adjustment classes:
WARNING_ONLY:
- No1 福岡 vs 広島
- No2 浦和 vs 東京V
- No3 清水 vs 千葉
- No8 町田 vs 柏

ADJUST_CANDIDATE but NO_VALIDATED_DELTA:
- No9 G大阪 vs 神戸
- No11 藤枝 vs 大宮

STRUCTURAL_RISK / TICKET_LAYER_ONLY:
- No4 岡山 vs 京都
- No12 新潟 vs 磐田
- No13 甲府 vs 徳島

NO_ACTION:
- No5 FC東京 vs 名古屋
- No6 長崎 vs C大阪
- No7 横浜FM vs 水戸
- No10 山形 vs 富山

Production adjustment gate:
- allowed probability deltas: 0/13
- source disagreement remains warning/routing signal only
- current event information has no OOF-validated numeric delta

Current production probability:
- P_final = P_base for all 13 matches


### Step25 preliminary simulation / budget work
A simple Monte Carlo engine was created:
- scripts/simulate_toto_round_v01.py
- data/simulations/toto1654_pfinal_100k_v01.csv
- 100,000 draws
- seed = 1654
- GLOBAL_MAX_ABS_ERROR = 0.002858
- PASS

IMPORTANT:
This simulation is only:
P_final -> random 1/0/2 draws

It is NOT the intended final 90-minute match simulation.

A pure-probability budget optimizer was also created:
- scripts/optimize_toto_budget_v01.py
- data/analysis/toto1654_budget_optimal_v01.csv

Budgets tested:
- 2,400 yen / 24 lines
- 4,800 yen / 48 lines
- 9,600 yen / 96 lines

This optimizer is currently AUXILIARY ONLY.
Ticket optimization work is PAUSED until the real match-simulation layer exists.


## SYSTEM DIRECTION REFINED

The intended TOTO LABO architecture is now:

1. Broad source acquisition
2. FootyStats HOME / H2H / AWAY deep analysis
3. Football LAB detailed tactical/statistical analysis
4. J.League official / toto official / toto One / Sportsnavi /
   Soccer Critique Web / transfer / injury / suspension / national-team news
5. Predicted starting XI
6. Player-level power calculation and lineup-strength comparison
7. Matchup-specific attack vs defense interaction
8. 90-minute match-state simulation
9. 100,000 simulated matches per toto card
10. P_sim(1,0,2) + score distributions + match-flow distributions
11. Compare P_sim with existing statistical P_base
12. Construct final production judgement
13. Finite-budget toto ticket optimization

IMPORTANT:
The existing v1-C P_base is NOT discarded.
It remains the statistical baseline / anchor.

The future 100,000 simulation must be:
detailed match inputs -> simulated 90-minute matches -> P_sim

NOT:
P_final -> random result draws.


## FootyStats role
The FootyStats automatic acquisition pipeline created from Round1653 must be preserved.

Core principle:
For every toto match, analyze:
- HOME team HOME data
- H2H page
- AWAY team AWAY data

The analysis must NOT be reduced to matchup_xg alone.

Relevant FootyStats domains include:
- result / form / PPG
- attack
- defense
- xG / xGA
- shots / shots on target / shots off target
- shot conversion
- goals scored / conceded
- clean sheets
- failed to score
- BTTS
- over / under
- first-half / second-half
- first-score probability
- timing
- 10-minute goal distribution
- 10-minute scored distribution
- 10-minute conceded distribution
- 15-minute distributions
- corners
- cards
- possession / territory
- fouls
- offsides
- set-play / other
- player data
- odds where available
- H2H historical results and tendencies

The FootyStats deep analysis should produce an independent
FootyStats-only judgement for all 13 matches, then compare it with P_base.


## FootyStats Round1654 RAW inventory started

Inventory script:
- scripts/audit_footystats_1654_raw_inventory_v01.py

Output:
- data/analysis/footystats_1654_raw_inventory/

Initial inventory:
- actual match FULL RAW JSON: 13
- plus manifest JSON: 1
- actual round HTML: 39 = 13 matches x HOME/H2H/AWAY
- one unrelated FootyStats snapshot was also caught by broad HTML discovery
- normalized columns: 65
- feature-block columns: 93
- raw leaf paths observed: 152
- simulation-relevant candidate paths: 78
- possible currently-unmapped raw paths: ~100 heuristic

Important correction:
The first inventory reported JSON_FILES=14 and HTML_FILES_FOUND=40
because it included:
- toto1654_manifest_v02.json
- one unrelated FootyStats snapshot HTML

Actual target set is:
- 13 FULL RAW JSON
- 39 target HTML files


## FootyStats FULL RAW confirmed categories
Each HOME / H2H / AWAY page contains categories including:

- RESULT_FORM
- ATTACK
- DEFENSE
- XG
- SHOTS
- GOALS_TOTALS
- HALF
- TIMING
- CORNERS
- CARDS
- TERRITORY
- SETPLAY_OTHER
- H2H
- PLAYERS
- ODDS

Round1654 No1 sample confirmed that RAW contains substantially more
information than current 65-column normalized / 93-column feature block.

Examples confirmed:
HOME/AWAY team pages:
- xG all/home/away
- opponent xG / xGA all/home/away
- shots
- shots on target
- shots off target
- fouls
- offsides
- possession
- BTTS + win
- first/second-half scoring
- first/second-half over rates
- average goals first/second half
- goals per minute
- conceded per minute
- form / PPG
- home advantage
- clean-sheet / score / concede information
- full-time scoreline distributions
- total-goal distributions
- 10-minute goal distributions
- corner/card sections
- player per-90 information

H2H page sample confirmed:
- historical H2H W/D/L
- historical scores
- Over 1.5 / 2.5 / 3.5
- BTTS
- clean sheets
- HOME / AWAY form comparison
- xG/xGA
- first-score probability
- 10-minute / 15-minute scored-conceded timing information
- shots
- shot conversion
- shots on target / off target
- shots per goal
- first/second-half W/D/L tendencies
- corners / cards sections
- other matchup data

This confirms that FootyStats has enough raw material for a much
deeper Round1654 HOME/H2H/AWAY analysis than the current feature block.


## NEXT SESSION — PRIORITY ORDER

Do NOT resume ticket optimization first.

1. Finish FootyStats Round1654 FULL RAW inventory.
2. Parse/structure all useful HOME/H2H/AWAY raw fields.
3. Build a FootyStats Deep Match Profile for all 13 matches.
4. Produce FootyStats-only detailed prediction for Round1654.
5. Compare FootyStats judgement vs existing P_base.
6. Inventory Football LAB fields needed for match simulation.
7. Build predicted-lineup / player-strength layer.
8. Design the real 90-minute simulation engine.
9. Run 100,000 simulated matches per card.
10. Only after that resume finite-budget ticket optimization.

Round1654 purchase deadline:
- 2026-09-19 17:50 JST


## 2026-09-15 AM SESSION UPDATE

### FootyStats Round1654 deep analysis progressed substantially

Completed:
- FULL RAW / HTML inventory
- bilingual JA/EN parser strategy established
- venue xG/xGA 13/13
- scored/conceded 13/13
- W/D/L rates 13/13
- clean sheet / failed to score 13/13
- shots / shots on target / possession 13/13
- H2H deep comparison integrated
- FootyStats-only Round1654 prediction finalized
- 10-minute scored/conceded timing bins extracted 13/13
- first-score coverage 12/13
- FootyStats simulation-ready match-level lambda prototype created

Important files:
- data/analysis/footystats_1654_deep/footystats_toto1654_core_profile_v04.csv
- data/analysis/footystats_1654_deep/footystats_toto1654_deep_comparison_v01.csv
- data/analysis/footystats_1654_deep/footystats_toto1654_prediction_v01.csv
- data/analysis/footystats_1654_deep/footystats_toto1654_timing_bins_v01.csv
- data/analysis/footystats_1654_deep/footystats_toto1654_sim_input_v01.csv
- data/analysis/footystats_1654_deep/footystats_toto1654_sim_input_v03.csv

### FootyStats-only Round1654 prediction

AGREE with P_base:
1 福岡 vs 広島 -> 2
2 浦和 vs 東京V -> 1
3 清水 vs 千葉 -> 1
4 岡山 vs 京都 -> 1
5 FC東京 vs 名古屋 -> 1
6 長崎 vs C大阪 -> 1
11 藤枝 vs 大宮 -> 2

MIXED:
7 横浜FM vs 水戸
8 町田 vs 柏
10 山形 vs 富山
12 新潟 vs 磐田

DISAGREE with P_base:
9 G大阪 vs 神戸
- P_base: HOME slight
- FootyStats: AWAY_STRONG

13 甲府 vs 徳島
- P_base: AWAY
- FootyStats: HOME_STRONG

FootyStats strongest directional signals:
- No5 FC東京 HOME
- No6 長崎 HOME
- No13 甲府 HOME
- No1 広島 AWAY
- No9 神戸 AWAY
- No11 大宮 AWAY

### Timing / 90-minute simulation preparation

Timing coverage:
- H2H TIMING: 13/13
- 10-minute scored bins: 13/13
- 10-minute conceded bins: 13/13
- first-score: 12/13
- HALF first/second information exists broadly, but JA/EN extraction is incomplete

Important interpretation:
FootyStats 10-minute percentages are distributions of historical goals by time,
NOT direct per-bin goal probabilities.

Therefore:
match-level expected goals lambda
x timing distribution
must be used to create time-bin hazards.

Initial timing allocation v01 preserved total lambda correctly:
- max weight error ~2.22e-16
- max lambda error ~4.44e-16

However v01 produced excessive concentration in some bins because historical 0%
was treated almost as impossible.

A smoothing layer was added.
A bug in HALF merge caused all half targets to default to 0.45 and was detected.

Fixed v03:
- lambda sums preserved exactly
- HALF information now actually applied where available

Current HALF status:
- No1-9 mostly available
- No10 partial
- No11-13 currently fallback 0.45 because English HALF parser not yet built

Current v03 is computationally correct but NOT YET approved for production simulation.

### Next mandatory step

Build English-template HALF parser for No10-13:
- First Half Scored
- First Half Conceded
- HT Win/Draw/Loss
- first/second-half tendencies

Then:
1. HALF coverage 13/13
2. rebuild smoothing v04
3. validate timing shape
4. only then build 90-minute simulation prototype

Do NOT run the final 100,000-match simulator yet.


## 2026-09-16 NIGHT — STATE-8 to STATE-13c

### STATE-8 EXACT MATCH ENGINE
- FootyStats timing + empirical score-state matrix を用いた exact dynamic probability engine 完成。
- Monte Carlo乱数なしで90分のscore distributionを展開。
- No.1 validation PASS。
- 1654全13試合 exact PASS。
- probability mass ≈ 1.0 全試合。
- score-state effect は穏当:
  - CONS max abs ≈ 0.008
  - FULL max abs ≈ 0.0063
- score-state は勝敗を大きく反転する主因ではなく、試合展開の微調整層。

### SCORE-STATE CALIBRATION
- 2018-2025 J.League 8741 matches。
- strength-adjusted Poisson GLM + time_bin x score_state interaction。
- 76-90分・1点リード側の得点hazard低下が有意:
  - HOME_LEAD_1 home mult 0.623 [0.557,0.696]
  - AWAY_LEAD_1 away mult 0.685 [0.609,0.771]
- walk-forward OOF 2022-2025:
  - score-state model better 4/4 folds
  - total delta NLL = -40.692
- arbitrary state multipliersは廃止。

### STATE-9/10 P_BASE vs P_SIM
Correct production P_base columns:
- score_p_home
- score_p_draw
- score_p_away

P_base vs FootyStats exact sim:
- AGREE 7/13
- DISAGREE: No.7,8,9,10,12,13
- largest probability difference No.10: 0.2159

Lambda edge conflict:
- No10 edge shift -0.948
- No4 +0.536
- No9 -0.485
- No8 -0.411
- No7 -0.351
- No13 +0.334

### STATE-11 P_BASE DECOMPOSITION
Production P_base reconstruction exact:
STAGE2_MAX_ERR = 0.0

1654 input files:
- data/features/jleague_pre_match_features_toto1654.csv
- data/features/footystats_csv_prediction_features_2026_redownload_v2.csv
- data/predictions/multisource_premarket_predictions_2026_toto1654.csv

Conflict patterns:
A) Stage1 -> multisource reversal:
- No6
- No7
- No11
- No13

B) Stage1 itself vs FootyStats deep conflict:
- No8
- No9

C) Same direction but strength difference:
- No4

No10:
- Stage1 H=1.677 A=1.350
- Final H=1.694 A=1.071
- not a direction reversal
- multisource strongly reinforces Yamagata and suppresses Toyama
- FootyStats deep strongly favors Toyama
- major unresolved conflict

### STATE-12 MULTISOURCE REVERSAL OOF
OOF 2023-2025, 3428 matches.
Stage1 -> Final reversals:
- 468 cases
- Stage1 acc 0.3056
- Final acc 0.4145
- RESCUED 194
- BROKEN 143
- delta LL -6.782
- delta Brier -0.01072
- Final better all 2023/2024/2025.

10-20pt reversal bin:
- N=144
- Stage1 acc 0.2986
- Final acc 0.4236
- delta LL -3.1211

1654 true reversals:
- No6 shift +0.1033
- No7 +0.1878
- No11 -0.1061
- No13 -0.1113
All in historically supported ~10-20pt region.

### STATE-13 HISTORICAL FOOTYSTATS VENUE OOF
footystats_csv_matches:
- 2018-2025 historical actual xG full coverage 8767/8767
- season_final snapshots MUST NOT be used for historical OOF due leakage risk.

Leak-free rolling venue model built from prior matches only:
- home venue xG/xGA
- away venue xG/xGA
- fs_mu_home
- fs_mu_away

2023-2025 OOF conflict audit:
- JOINED_READY 2826
- conflicts 651
- P_base acc 0.4086
- FootyStats venue acc 0.3272
- P_base wins 266
- FS wins 213
- FS-vs-base delta LL +9.619 => P_base better overall

Conflict blend OOF:
- best FS weight 0.05
- delta LL -0.00003
- delta Brier -0.00003
- no FS weight improved LL in every season
=> no robust numerical blend approved.

### CURRENT PRODUCTION PRINCIPLE
- P_base remains numeric anchor.
- FootyStats deep/exact sim is NOT mechanically blended into P_final.
- FootyStats is used as independent audit/risk layer:
  - disagreement flag
  - double/triple candidate
  - latest-news recheck target
- score-state matrix is OOF-supported simulation layer.
- No arbitrary probability delta.

### CURRENT 1654 RISK VIEW
High-confidence agreement:
- No1,3,5,6,11
Agreement but strength mismatch:
- No4
Near toss-up:
- No12
Conflict/risk:
- No7,8,9,10,13
Highest-priority unresolved:
- No10 Yamagata vs Toyama
- No9 G Osaka vs Kobe
- No13 Kofu vs Tokushima

### NEXT
STATE-14:
Integrate:
- P_base
- FootyStats deep
- exact sim
- multisource reversal OOF
- current injuries/suspensions/ACL/travel
- toto official / totoONE / Football LAB / current J.League news
into final risk classes:
AGREE / SOFT_CONFLICT / STRONG_CONFLICT / TRIPLE_RISK

Then update provisional budget tickets.
Do NOT perform naive P_base + FootyStats probability averaging.

## 2026-09-16 Daily Finish — STATE-15t〜16p

### 完了
- STATE-15t JLeague player identity assets: PASS
  - ローカルに信頼できる `jleague_player_id ↔ FootyStats英字名` bridgeなし
  - canonical keyは `jleague_player_id` に固定
- STATE-15u player strength input schema: PASS
  - 51列、直前lineup投入用schema完成
- STATE-15v team strength aggregation: READY
  - totoONE lineup待ち
- STATE-16a dynamic simulation schema: PASS
  - 13試合×10時間帯=130行
- STATE-16b FootyStats timing → 10bin: PASS
  - 全13試合で総μ完全保存
  - max error 4.44e-16
- STATE-16c score-state lookup: PASS
- STATE-16d 10bin dynamic exact engine: PASS
  - massほぼ1.0
  - max score-state delta 0.005544
  - score-stateは主役ではなく微調整層
- STATE-16e player matchup edges: READY
  - lineup/team strength待ち
- STATE-16f player OOF coverage: PASS
  - player資産は1648/1649/1650の3ラウンドのみ
- STATE-16g〜16p player historical validation監査
  - 独立カードは38試合
  - 2026 actualを既存公式DBからjoin不可
  - DBは2025-12-06まで
  - 1649 `total_match_results` はactualではなく予測集計
  - PLAYER→lambda production係数のOOF承認は現時点で不可

### AI学習 / 設計確定
- PLAYER strengthは未検証係数でP_baseを直接動かさない
- 1654ではPLAYER layerを audit / risk / sensitivity layer として使用
- FootyStats未名寄せ選手は0扱い禁止
  - `footystats_available=0`
  - Fansaka + JLeague officialをfallback
- FootyStats timingは総μを変えず時間分布のみ変更
- score-state効果はOOF支持ありだが確率への影響は小さい
- exact engineを基本とし、1M MCはlineup/substitution/availability/tactics等の不確実性導入後に使用
- P_baseは引き続き数値アンカー

### 次回
1. STATE-16q PLAYER multiplier sensitivity grid
   - weak / medium / strong のprototypeのみ
   - production係数にはしない
2. totoONE 1654予想スタメン取得後
   - player staging投入
   - jleague_player_id join
   - Fansaka/JLeague official join
   - absence/suspension確認
   - team strength生成
   - player matchup edge生成
3. Football LAB tactical matchup接続
4. ACL後の柏・神戸の出場時間/負傷/疲労更新
5. playerなしsim vs player sensitivity sim比較
6. 最終的にP_baseとの乖離・risk matrixを再評価

### 現在地点
P_base / FootyStats timing / empirical score-state / 10bin exact dynamic engine まで接続済み。
PLAYER layerはschema・集約・matchup設計まで完成し、現在は1654 lineup入力待ち。
PLAYER→lambda係数は歴史OOF不足のためproduction未承認。

### 絶対に次やること
STATE-16q PLAYER multiplier sensitivity grid。
その後、1654 totoONE lineupを取得次第PLAYER pipelineを実データで通す。

### 保留
- 2026 FootyStats player current data取得
- FootyStats player ↔ jleague_player_id explicit alias map
- PLAYER→lambda production OOF校正
- 1,000,000 MC本番実行
- Football LAB tactical placementのsimulation接続
- 最終P_final / ticket再最適化

---

# 2026-09-17 UPDATE — STATE-17n3

## FootyStats 2026 player strength
STATE-17c PASS.

- 1654 target players: 694
- clubs: 26
- six axes:
  - fs_attack_power
  - fs_finishing_power
  - fs_build_up_power
  - fs_width_carry_power
  - fs_defensive_power
  - fs_keeper_power
- keeper N=67
- status: PROTOTYPE_CURRENT_2026

Source:
data/players/footystats_2026_toto1654_player_strength_v01.csv

## JLeague canonical player identity
Canonical asset:
data/jleague/2026_27/j123_players_stats_v1.csv

1654 overlap legacy seed:
data/players/player_master_seed_1654_overlap_v01.csv

Overlap:
- 225 players
- 21 clubs
- canonical JLeague ID match: 225/225
- position available: 225/225

Position:
- MF 86
- DF 79
- FW 41
- GK 19

## FootyStats <-> JLeague crosswalk

Initial club-only candidates:
6024

After position:
1799

STATE-17j:
club + position + shirt exact
- 207/225 unique
- collisions 0

STATE-17m:
remaining 18 were position ontology mismatches.
club + shirt exact ignoring position:
- matched 18/18
- unique 18
- collisions 0
- no match 0

Final methods:
- CLUB_POSITION_SHIRT_EXACT: 207
- CLUB_SHIRT_EXACT_POSITION_MISMATCH: 18

## STATE-17n3 FINAL
PASS.

Final file:
data/players/player_master_footystats_2026_crosswalk_1654_final_v03.csv

Results:
- ROWS 225
- UNIQUE_JLEAGUE_IDS 225
- FS_STRENGTH_VALID_ROWS 692
- FS_IDENTITY_DUP_ROWS 0
- FS_IDENTITY_COLLISION_KEYS 0

Six-axis coverage:
- fs_reliability 225
- fs_attack_power 225
- fs_finishing_power 225
- fs_build_up_power 225
- fs_width_carry_power 225
- fs_defensive_power 225
- fs_keeper_power 19

IDENTITY_STATUS APPROVED
STRENGTH_STATUS PROTOTYPE_CURRENT_2026

Important:
Identity crosswalk is approved.
Player strength -> lambda coefficient is NOT production approved.
Historical OOF is still required.
Production player multiplier remains 0.

## NEXT
STATE-17o:
Integrate the approved 225-player crosswalk + six-axis FootyStats strength into:

data/analysis/match_karte/1654/toto1654_players_v2_staging.csv

Then:
1. fill player/source/strength fields
2. identify missing 1654 clubs/new players
3. acquire totoONE 1654 predicted lineups when available
4. estimate starter/sub minutes
5. run scripts/build_team_strength_from_players_v01.py
6. run scripts/build_player_matchup_edges_v01.py
7. use player effects only for risk/sensitivity until OOF approval

Production constraints:
- Keep P_base fixed.
- Do not mechanically blend FootyStats into P_base.
- Do not apply unvalidated player strength directly to lambda.
- Missing != zero.
- totoONE mainly informs who is likely to play.
- Avoid duplicate source counting.
- 1M simulation only after model assumptions are fixed.


---

## 2026-09-18 05:13 JST — toto1654 state update

### Production anchor
- `P_production = P_base`
- source: `data/predictions/score_model_v1c_stacked_toto1654.csv`
- anchor: `data/predictions/toto1654_production_anchor_v01.csv`
- fixture join: exact `toto_no -> match_no` 1..13
- fuzzy identity used: 0
- row-order inference used: 0

### Production coefficients
- PLAYER = 0
- TACTICAL = 0
- score-state transport = 0
- fatigue/rest context = 0
- unvalidated dynamic wholesale replacement = 0

### Score-state
- method OOF: PASS
- 2022-2025 walk-forward: total NLL improved 4/4 years
- aggregate NLL delta: -40.692211703135
- lookup provenance: PASS
- production lookup reproduced: 40/40 cells
- `P_base + (state - none)` transport OOF: NOT ESTABLISHED
- therefore score-state transport into P_final remains 0

### PLAYER
- totoONE: status information available, predicted XI/formation unavailable
- confirmed suspension hard-unavailable:
  - 千葉 エリソン
  - 岡山 宮本英治
  - 町田 明本考浩
- other absence/difficult evidence remains sensor-only unless calibrated
- player production coefficient = 0

### Football LAB tactical
- CBP semantic coverage: 26/26
- formation: 0/26
- attack direction: 0/26
- positional matchup: 0/26
- tactical production coefficient = 0

### Dynamic / timing
- current: `data/analysis/toto1654_dynamic_exact_v01.csv`
- FootyStats timing unchanged from prior artifact
- no dynamic recompute required
- dynamic whole-probability surface does not replace P_base

### Fatigue / rest
- historical assets:
  - `data/evaluation/fatigue_context_v1_summary_2023_2025.csv`
  - `data/evaluation/fatigue_context_v1_audit_2023_2025.csv`
- 2025 confirmation did not support a stable mechanical fatigue penalty
- production coefficient = 0

### Latest gates
- MAIN-51R: score-state method OOF PASS
- MAIN-54: lookup reproduction 40/40 PASS
- MAIN-55R: P_base + state_delta OOF NOT ESTABLISHED
- MAIN-56RR: production anchor == P_base PASS
- MAIN-57: contextual asset inventory PASS
- MAIN-58/59: fatigue/rest review PASS, no promotion

### Current safe state
- `P_final` not modified
- `P_production = P_base`
- purchase final not fixed yet

### Next
Audit historical evidence for:
1. ACL / AFC / continental congestion
2. travel / distance
3. substitution / bench effects

Do not modify P_base or production coefficients without historical OOF approval.

---

## 2026-09-19 09:15 JST — toto1654 deadline-day update

Deadline: 2026-09-19 17:50 JST

### Last completed
- MAIN-86 PASS
- production-only budget optimizer verified
- `P_production = P_base`
- purchase final still not fixed

### totoONE predicted XI
- 13 match PDFs acquired
- predicted XI coverage: 26/26 sides
- predicted formation coverage: 26/26 sides
- confirmed suspensions remain:
  - 千葉 エリソン
  - 岡山 宮本英治
  - 町田 明本考浩
- suspension status is consistent with predicted XI
- player production coefficient remains 0

### New continental context
- 京都: ACL Elite 09/15 away
- G大阪: ACL Elite 09/15 home vs Cong An Hanoi
- 柏: ACL Elite 09/16 away
- 神戸: ACL Elite 09/16 away Thailand
- 町田: ACL2 09/17 home
- contextual information remains production coefficient 0

### Football LAB current state
- CBP / semantic coverage: 26/26 sides
- feature blocks: 13 matches
- full Football LAB acquisition is NOT complete
- hot-zone integration: NOT established
- attack-direction integration: 0/26
- positional-matchup integration: 0/26
- preview/midokoro structured ingestion: NOT yet proven

### Simulation state
- current exact dynamic uses FootyStats timing + validated score-state lookup
- predicted-XI player-strength transport is NOT yet built/OOF-approved
- Football LAB hot-zone x totoONE time-bin simulator is NOT yet built
- any new lineup/hot-zone simulator must remain research/shadow only until OOF

### Deadline-day next
1. materialize totoONE XI player table
2. exact join to player parameter master
3. calculate research XI strength ratios
4. audit Football LAB hot-zone / preview assets
5. build research shadow simulation
6. refresh official market / availability before final ticket optimization

## 2026-09-19 MAIN-128〜140 checkpoint

- Football LAB hotzone: 13 matches / 26 teams / 54 cells each = 1,404 cells.
- MAIN128 PASS: all 26 hotzone tables are 6x9, no missing.
- MAIN133: DOM order established as TABLE1=HOME, TABLE2=AWAY.
- MAIN134 PASS:
  data/analysis/football_lab_toto1654_hotzone_cells_raw_v01.csv
  ROWS=1404, RGBA missing=0.
- MAIN135 PASS: RGB palette is monotonic; 43 unique RGB levels.
- MAIN137 PASS: Football LAB CSS directly confirms light=low play share, dark=high play share.
- Alpha differs by HOME/AWAY for same RGB, so alpha is not used as intensity.
- MAIN138 PASS:
  data/analysis/football_lab_toto1654_hotzone_cells_ordinal_v01.csv
  ordinal 1..43, 0..1 shadow scale.
  HOME attack direction=LR 13/13.
  AWAY attack direction=RL 13/13.
- MAIN139 PASS:
  data/analysis/football_lab_toto1654_hotzone_cells_normalized_v01.csv
  data/analysis/football_lab_toto1654_hotzone_features_v01.csv
  attack direction normalized to own-side col0 -> opponent-goal-side col8.
- XI strength shadow completed earlier:
  data/analysis/toto1654_xi_strength_shadow_v02.csv
  Football LAB XI + totoONE XI, 26 sides each, 11 players each.
  player production coefficient remains 0.
- Hotzone production coefficient remains 0.
- MAIN140 PASS:
  data/analysis/toto1654_mc_1m_per_match_pbase_control_v01.csv
  1,000,000 simulations per match / 13,000,000 total.
  max MC error=0.00095233.
  This is P_base control only, not XI/hotzone-adjusted production.
- P_base remains production anchor.
- XI/player/hotzone layers remain research/shadow only until historical OOF approval.

## 2026-09-19 MAIN-141〜149 shadow sensor checkpoint

- MAIN141 PASS: production / XI strength / hotzone schemas confirmed.
- MAIN142 PASS:
  data/analysis/toto1654_shadow_signal_v01.csv
  13 matches, 77 columns.
  P_base fixed; XI and hotzone reference-only.
  player/hotzone probability transport = 0.
- MAIN143 PASS:
  data/analysis/toto1654_shadow_signal_audit_v01.csv
  P_base vs XI:
  AGREE 5/13
  DISAGREE 8/13
  disagree matches = 4,6,7,8,10,11,12,13.
- MAIN144 PASS:
  data/analysis/toto1654_shadow_pattern_v01.csv
  ALL_SAME = 1,2,3
  XI_HZ_SAME_PBASE_OPPOSITE = 6,8,10,12,13
  PBASE_HZ_SAME_XI_OPPOSITE = 4,7,11
  PBASE_XI_SAME_HZ_OPPOSITE = 5,9
  Hotzone remains structural signal, not an outcome vote.
- MAIN145 PASS:
  data/analysis/toto1654_shadow_dashboard_v01.csv
  NO_PROBABILITY_MIX=1.
- MAIN147 PASS:
  data/analysis/toto1654_shadow_dashboard_external_v01.csv
  Added official market, totoONE, Soccer Hihyo Web and context as separate sensors.
  YOU/T.S. are same-media and count as one site sensor, not two votes.
  external/context probability coefficients remain 0.
  purchase_final_fixed=0.
- MAIN148 PASS:
  data/analysis/toto1654_shadow_dashboard_external_v02.csv
  Context shadow supplemented:
  No4 KYOTO_ACL_AWAY_0915
  No8 MACHIDA_ACL2_0917_HOME + KASHIWA_ACLE_0916_AWAY
  No9 GAMBA_ACL_HOME_0915 + KOBE_ACLE_0916_AWAY
  context coefficient remains 0.
- MAIN149 PASS:
  data/analysis/toto1654_shadow_sensor_matrix_v01.csv
  Final independent shadow matrix completed.
  Governance zero all = 1.
  Hihyo YOU/T.S. same-media one-sensor policy = 1.
  No probability mixing / no probability transport / purchase not final.


## MAIN-191 FINAL PURCHASE LOCK
- timestamp: 2026-09-19T13:17:39+09:00
- round: 1654
- plan: PURE_PBASE
- cost_yen: 9600
- tickets: 96
- unique_tickets: 96
- duplicates: 0
- global_structures_checked: 10296
- global_pbase_rank: 1
- pbase_mass_pct: 0.094221514
- simulation_used: 0
- direct_calculation: 1
- shadow_production_coeff: 0
- purchase_final_fixed: 1
- final_plan_file: data/analysis/toto1654_9600_purchase_final_v01.csv
- final_expanded_file: data/analysis/toto1654_9600_purchase_final_expanded_96_v01.csv
- sha256_file: data/analysis/toto1654_9600_purchase_final_v01.sha256.txt
- picks: 2 / 1 / 1 / 1|2 / 1 / 1 / 1 / 1|2 / 1|2 / 1 / 1|2 / 1|2 / 1|0|2


## MAIN-192 SEMANTIC CORRECTION
- timestamp: 2026-09-19T13:28:15+09:00
- round: 1654
- purpose: MODEL_DEVELOPMENT_AND_PAPER_EVALUATION
- prediction_snapshot_fixed: 1
- purchase_final_fixed: 0
- actual_purchase: 0
- evaluation_mode: PAPER_ONLY
- note: MAIN-191 plan is retained as a pre-match frozen prediction snapshot, not an actual purchase commitment.
- snapshot_file: data/analysis/toto1654_9600_prediction_snapshot_v01.csv


## MAIN-193 PAPER EVALUATION CONTRACT
- timestamp: 2026-09-19T13:29:17+09:00
- round: 1654
- evaluation_mode: PAPER_ONLY
- prediction_snapshot_fixed: 1
- actual_purchase: 0
- outcome_status: PENDING
- metrics_after_results: TOP1_ACCURACY | BRIER_SCORE | LOG_LOSS | CALIBRATION
- snapshot_sha256: c01b4d5db4cfb7df54fca7e14a28e210a847774705a41f0696ad52d227a9a7cf
- contract_sha256: f8debda8438bd24cbd8286753a9ff68919c68a3d795a9be8cec99d8285a338a3
- contract_file: data/analysis/toto1654_paper_evaluation_contract_v01.csv


## MAIN-195 MODEL EXPERIMENT REGISTRY
- round: 1654
- model_id: score_model_v1c_stacked
- prediction_snapshot_fixed: 1
- actual_purchase: 0
- results_known_at_freeze: 0
- evaluation_mode: PAPER_ONLY
- player_production_coeff: 0
- hotzone_production_coeff: 0
- score_state_transport_coeff: 0
- shadow_probability_mixing: 0
- registry_file: data/analysis/toto_model_experiment_registry_v01.csv

---

# HANDOFF CHECKPOINT — 2026-09-19 17:47 JST

This section is APPEND ONLY. Preserve all earlier state/history above.

## Round 1654 — current frozen production state

- Round: `toto1654`
- Production anchor remains: `P_production = P_base`
- `P_base` source: `data/predictions/score_model_v1c_stacked_toto1654.csv`
- Production anchor: `data/predictions/toto1654_production_anchor_v01.csv`
- Do not alter the frozen round-1654 `P_base` after this checkpoint.
- Player/XI, hot-zone, fatigue, tactical/context, external-site signals remain non-production unless an exact historical OOF transport method passes.
- `PREDICTION_SNAPSHOT_FIXED=1`
- `PURCHASE_FINAL_FIXED=0`
- `ACTUAL_PURCHASE=0`
- `EVALUATION_MODE=PAPER_ONLY`
- Do not infer that a real ticket was purchased unless the user explicitly says so.

## Exact P_base 1X2

| No | Home | Away | P(H) | P(D) | P(A) |
|---:|---|---|---:|---:|---:|
| 1 | 福岡 | 広島 | 0.269681 | 0.258165 | 0.472155 |
| 2 | 浦和 | 東京Ｖ | 0.485790 | 0.249474 | 0.264736 |
| 3 | 清水 | 千葉 | 0.454291 | 0.267468 | 0.278241 |
| 4 | 岡山 | 京都 | 0.374527 | 0.272163 | 0.353310 |
| 5 | FC東京 | 名古屋 | 0.473290 | 0.255534 | 0.271176 |
| 6 | 長崎 | Ｃ大阪 | 0.414672 | 0.268374 | 0.316954 |
| 7 | 横浜FM | 水戸 | 0.439851 | 0.261101 | 0.299048 |
| 8 | 町田 | 柏 | 0.395169 | 0.269903 | 0.334928 |
| 9 | Ｇ大阪 | 神戸 | 0.377721 | 0.276238 | 0.346042 |
| 10 | 山形 | 富山 | 0.519409 | 0.240793 | 0.239798 |
| 11 | 藤枝 | 大宮 | 0.326671 | 0.271827 | 0.401502 |
| 12 | 新潟 | 磐田 | 0.370961 | 0.279903 | 0.349136 |
| 13 | 甲府 | 徳島 | 0.335401 | 0.280805 | 0.383795 |

## Phase ⑤ shadow probability transport — completed

### MAIN-234〜238
Historical XI/player/hot-zone data audit completed.

### MAIN-239
Simple XI/player directional transport tested by strict walk-forward OOF.

- P_base Log Loss: `1.076315879`
- Shadow Log Loss: `1.086733810`
- Delta Log Loss: `+0.010417931`
- P_base Brier: `0.651977388`
- Shadow Brier: `0.656978021`
- Delta Brier: `+0.005000632`
- Final beta: `0.000000`
- `SHADOW_ACCEPTED=0`

Conclusion:
XI/player probability transport worsened both proper scoring metrics.
Production/shadow coefficient remains `0`.

### MAIN-240
Directional + draw transport also rejected.

- P_base Log Loss: `1.076315879`
- Shadow Log Loss: `1.104148452`
- Delta Log Loss: `+0.027832573`
- P_base Brier: `0.651977388`
- Shadow Brier: `0.668346492`
- Delta Brier: `+0.016369104`
- Final beta: `0.000000`
- Final gamma: `-1.500000`
- `SHADOW_ACCEPTED=0`

Do not use gamma=-1.5 in production.

### MAIN-241
Historical hot-zone data sufficient for comparable multi-round OOF calibration was not found.

- hot-zone production coefficient = `0`
- hot-zone shadow probability coefficient = `0`
- reason = `NO_HISTORICAL_OOF_DATA`

### MAIN-242
Shadow transport contract fixed.

Artifact:
`data/analysis/toto1654_shadow_probability_transport_contract_v01.csv`

Contract:
- XI/player coefficient = `0.0`
- hot-zone coefficient = `0.0`
- production coefficient = `0.0`
- XI/player reason = `OOF_REJECTED_LOGLOSS_AND_BRIER_WORSE`
- hot-zone reason = `NO_HISTORICAL_OOF_DATA`
- transport rule = `P_SHADOW_EQUALS_P_BASE`
- status = `SHADOW_RULE_FIXED_V01`
- rows = 13
- max abs difference P_shadow vs P_base = `0.0`

### MAIN-243
1,000,000 shadow simulations per match completed.

Artifact:
`data/analysis/toto1654_mc_1m_per_match_shadow_v01.csv`

- matches = 13
- simulations per match = 1,000,000
- total categorical draws = 13,000,000
- RNG seed = 1654
- maximum absolute Monte Carlo error vs input probability = `0.000952330`
- `MAIN243_PASS=1`

Important:
`P_shadow = P_base` is the validated result of the fixed zero-transport rule.
It does NOT mean that the shadow investigation or simulation was skipped.

MAIN-234〜243 are completed.
Do not rerun them unless explicitly requested for reproduction/audit.

## Phase ⑥ — external/current information governance

A pre-deadline external refresh was performed on 2026-09-19.

Current rules:
- same-media forecasts are not independent votes
- totoONE predicted XI is not automatically a result vote
- FootyStats/current external context is reference unless historically calibrated
- external/current context coefficient = 0 unless OOF approved
- do not mechanically blend external directions into `P_base`
- time-sensitive claims must be searched again when used as current facts

Current/latest:
- news
- confirmed/predicted lineups
- injuries/absences/suspensions
- toto voting rates
- odds
- match results

must be rechecked on the web at the time they are needed.

## Phase ⑦ — frozen 9600-yen-equivalent prediction snapshot

Frozen `PURE_PBASE` standard-multi structure:

| No | Picks |
|---:|---|
| 1 | 2 |
| 2 | 1 |
| 3 | 1 |
| 4 | 1|2 |
| 5 | 1 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1|2 |
| 9 | 1|2 |
| 10 | 1 |
| 11 | 1|2 |
| 12 | 1|2 |
| 13 | 1|0|2 |

- 96 unique combinations
- nominal structure value = 9600 yen
- model joint coverage under independent-match assumption = `0.094221514%`
- global maximum among the tested class of standard 96-ticket structures:
  1 triple + 5 doubles, selecting highest-P_base outcomes inside each selected match
- snapshot:
  `data/analysis/toto1654_9600_prediction_snapshot_v01.csv`
- expanded tickets:
  `data/analysis/toto1654_9600_pure_pbase_expanded_96_v01.csv`

This is a frozen prediction snapshot only.

Do not overwrite this snapshot because of later live discussion.

If an actual purchase occurs:
- record it separately
- only set `ACTUAL_PURCHASE=1` after explicit user confirmation

Current purchase state remains:

`PURCHASE_FINAL_FIXED=0`
`ACTUAL_PURCHASE=0`
`EVALUATION_MODE=PAPER_ONLY`

## Longitudinal evaluation contract

After Round 1654 results become final:

1. Do not alter the pre-match Round-1654 prediction snapshot.
2. Score:
   - Top1 accuracy
   - Brier Score
   - Log Loss
3. Do not judge calibration from only 13 matches.
4. Append Round-1654 results to:
   `data/analysis/toto_longitudinal_evaluation_ledger_v01.csv`
5. Register future model experiments separately in:
   `data/analysis/toto_model_experiment_registry_v01.csv`
6. Any future XI/player/hot-zone model must pass historical OOF validation before affecting a production anchor.

## Immediate next-chat behavior

- Treat this checkpoint and all earlier history as authoritative.
- Do not redo MAIN-234〜243 unless explicitly asked.
- `P_production = P_base`.
- Round-1654 `P_base` is frozen and immutable.
- XI/player coefficient = 0.
- hot-zone coefficient = 0.
- `P_shadow = P_base` is a completed validation result.
- MAIN-243 completed 13,000,000 total shadow draws.
- Frozen PURE_PBASE snapshot = 96 combinations / nominal 9600 yen.
- `PREDICTION_SNAPSHOT_FIXED=1`
- `PURCHASE_FINAL_FIXED=0`
- `ACTUAL_PURCHASE=0`
- `EVALUATION_MODE=PAPER_ONLY`
- Never state that a real ticket was purchased unless explicitly confirmed by the user.
- For latest/current information, re-search the web.
- After final results, freeze prediction and score Top1 / Brier / Log Loss, then append to the longitudinal ledger.


---

# INTERIM POSTMATCH CHECKPOINT — 2026-09-19 21:29 JST

## Round 1654 — 11/13 matches completed, provisional review

IMPORTANT:

- This is an INTERIM postmatch checkpoint.
- 11 of 13 matches are currently recorded as completed from the user-provided live result screen.
- No final Round1654 scoring should be performed until all 13 results are final and rechecked.
- Do NOT alter the frozen pre-match `P_base`.
- Do NOT alter the frozen 9600-yen-equivalent prediction snapshot.
- `PREDICTION_SNAPSHOT_FIXED=1`
- `PURCHASE_FINAL_FIXED=0`
- `ACTUAL_PURCHASE=0`
- `EVALUATION_MODE=PAPER_ONLY`
- Results below are provisional/user-provided at this checkpoint, not the final web-verified result ledger.

## Current visible results — 11/13

| No | Match | Score | Outcome |
|---:|---|---:|:---:|
| 1 | 福岡－広島 | 0-1 | 2 |
| 2 | 浦和－東京V | 3-1 | 1 |
| 3 | 清水－千葉 | 2-1 | 1 |
| 4 | 岡山－京都 | 1-2 | 2 |
| 5 | FC東京－名古屋 | 1-0 | 1 |
| 6 | 長崎－C大阪 | 1-1 | 0 |
| 7 | 横浜FM－水戸 | 2-1 | 1 |
| 8 | 町田－柏 | pending | pending |
| 9 | G大阪－神戸 | pending | pending |
| 10 | 山形－富山 | 0-2 | 2 |
| 11 | 藤枝－大宮 | 1-1 | 0 |
| 12 | 新潟－磐田 | 2-1 | 1 |
| 13 | 甲府－徳島 | 0-1 | 2 |

## Provisional P_base Top1 status

Frozen Round1654 P_base Top1 predictions:

1. 福岡－広島 -> 2
2. 浦和－東京V -> 1
3. 清水－千葉 -> 1
4. 岡山－京都 -> 1
5. FC東京－名古屋 -> 1
6. 長崎－C大阪 -> 1
7. 横浜FM－水戸 -> 1
8. 町田－柏 -> 1
9. G大阪－神戸 -> 1
10. 山形－富山 -> 1
11. 藤枝－大宮 -> 2
12. 新潟－磐田 -> 1
13. 甲府－徳島 -> 2

Among the 11 currently completed matches:

- Top1 correct = 7
- Top1 incorrect = 4
- provisional Top1 accuracy = 7/11 = 63.64%

Current Top1 misses:

- No4 岡山－京都: P_base Top1 = 1 / actual = 2
- No6 長崎－C大阪: P_base Top1 = 1 / actual = 0
- No10 山形－富山: P_base Top1 = 1 / actual = 2
- No11 藤枝－大宮: P_base Top1 = 2 / actual = 0

IMPORTANT:
This provisional 7/11 is NOT the final Round1654 score.
Final Top1 / Brier / Log Loss must wait for all 13 matches.

## Frozen 9600 PURE_PBASE ticket status

Frozen snapshot:

`2 / 1 / 1 / 1|2 / 1 / 1 / 1 / 1|2 / 1|2 / 1 / 2|1 / 1|2 / 1|0|2`

Among completed matches, the frozen structure already has three uncovered outcomes:

### No6 長崎－C大阪

Frozen ticket:
`1`

Actual:
`0`

P_base:
- 1 = 0.414672
- 0 = 0.268374
- 2 = 0.316954

Interpretation:

- Home 1 was Top1 but only 41.5%.
- Draw probability was 26.8%, not negligible.
- The match was not truly a high-confidence single.
- Under the later 19,200-yen illustrative structure, `1|2` would also have missed because draw `0` was omitted.

This is a key finite-budget allocation failure candidate.

### No10 山形－富山

Frozen ticket:
`1`

Actual:
`2`

P_base:
- 1 = 0.519409
- 0 = 0.240793
- 2 = 0.239798

Interpretation:

- 山形1 was the strongest P_base Top1 in the round at about 51.9%.
- 富山2 was about 24.0%.
- Draw and away probabilities were virtually identical.
- Away 2 was effectively completely uncovered in all practical budget structures discussed.

This is not a zero-probability model surprise.
It is a case where a roughly 24% tail direction was accepted as budget risk because Top1 exceeded 50%.

### No11 藤枝－大宮

Frozen ticket:
`2|1`

Actual:
`0`

P_base:
- 1 = 0.326671
- 0 = 0.271827
- 2 = 0.401502

Interpretation:

- Both win directions were covered.
- Draw 0 at 27.2% was the only omitted outcome.
- Actual result landed exactly on the omitted draw.

This is another important draw-allocation failure candidate.

## User observations at this checkpoint

The user emphasized that the painful failures include the complete omission of outcomes that still had meaningful P_base probability.

In particular:

- 山形－富山: 富山2 was effectively "no mark" despite P_base around 24%.
- 長崎－C大阪: draw 0 was completely uncovered despite P_base around 26.8%.
- The user noted the practical toto lesson:
  "引き分けを制するものはtotoを制する"

Treat this as a research observation, NOT as a production rule.

There was also a verbal comment in chat:
"痛恨はNo7とNo11"

However, the concrete examples immediately supplied were No10 山形－富山 and No6 長崎－C大阪.

Do NOT silently reconcile or rewrite this numbering discrepancy.
Recheck the intended match numbers during the full postmatch review after all 13 results are final.

## Model error vs ticket allocation error

Keep these separate.

### Model layer

Current provisional P_base Top1:
7/11 correct.

Therefore the current evidence does NOT support saying that the entire probability model collapsed.

However:

- No10 was a relatively strong Top1 miss.
- No6 and No11 were lower-confidence / higher-entropy situations.
- Proper scoring evaluation is still required.

Final model evaluation must use:

- Top1 accuracy
- Brier Score
- Log Loss

and must use the frozen pre-match probabilities unchanged.

### Ticket / finite-budget layer

The frozen 9600 structure has already failed because:

- No6 actual 0 was not covered
- No10 actual 2 was not covered
- No11 actual 0 was not covered

Therefore the paper ticket is already eliminated regardless of No8/No9.

This should NOT be confused with the probability-model evaluation.

## Postmatch research hypotheses — DO NOT ADOPT YET

These are hypotheses for historical OOF testing only.

### Hypothesis A — strong Top1 but symmetric residual tails

Example:
No10 山形－富山

P:
- Top1 = 51.9%
- remaining = 24.1% / 24.0%

Question:

When Top1 exceeds 50% but the two residual outcomes are nearly symmetric,
is SINGLE fixation still optimal under finite toto budgets?

Test historically before changing allocation policy.

Possible diagnostic variables:

- top1 probability
- top1 minus top2 gap
- P(draw)
- P(third)
- residual entropy
- ratio between second and third probabilities
- expected portfolio coverage gain from DOUBLE/TRIPLE expansion

### Hypothesis B — weak Top1 + meaningful draw probability

Example:
No6 長崎－C大阪

P:
- 1 = 41.5%
- 0 = 26.8%
- 2 = 31.7%

Question:

For matches with approximately:

- Top1 < 45%
- P(draw) around 26% or higher
- relatively small three-way gaps

does finite-budget performance improve by protecting draw rather than mechanically selecting the two highest probabilities?

Compare historically:

- Top1 single
- Top2 probability double
- Top1 + draw double
- triple

Do NOT infer from Round1654 alone that `1|0` is better than `1|2`.

### Hypothesis C — draw omission risk in two-win-direction doubles

Example:
No11 藤枝－大宮

P:
- 1 = 32.7%
- 0 = 27.2%
- 2 = 40.2%

Frozen structure:
`2|1`

Actual:
`0`

Question:

When draw probability is close to the weaker win direction,
should a standard double always use the two highest raw probabilities,
or should draw-risk / portfolio diversification sometimes change the chosen pair?

This must be tested historically with finite-budget OOF evaluation.

## Governance for tomorrow's full review

After all 13 matches are final:

1. Recheck all Round1654 results from current web sources.
2. Freeze result truth.
3. Do not alter any pre-match prediction.
4. Calculate final Top1 accuracy.
5. Calculate final multiclass Brier Score.
6. Calculate final Log Loss.
7. Compare model error vs ticket-allocation error.
8. Audit every frozen SINGLE / DOUBLE / TRIPLE.
9. Identify which misses were:
   - MODEL_TOP1_ERROR
   - BUDGET_CONSTRAINED_UNCOVERED
   - DRAW_OMISSION
   - TAIL_DIRECTION_OMISSION
   - COVERED_DESPITE_TOP1_ERROR
10. Only after that formulate historical OOF experiments.
11. Do not convert Round1654-specific hindsight into a production rule.
12. Append finalized Round1654 evaluation to:
    `data/analysis/toto_longitudinal_evaluation_ledger_v01.csv`

## Current status

`ROUND1654_RESULTS_FINAL=0`

`COMPLETED_MATCHES=11`

`PENDING_MATCHES=2`

`PREDICTION_SNAPSHOT_FIXED=1`

`P_BASE_MUTATED=0`

`PURCHASE_FINAL_FIXED=0`

`ACTUAL_PURCHASE=0`

`EVALUATION_MODE=PAPER_ONLY`

`FINAL_BRIER_PENDING=1`

`FINAL_LOGLOSS_PENDING=1`

`FINAL_LEDGER_APPEND_PENDING=1`


---

# NIGHT CLOSE CHECKPOINT — 2026-09-19 — EWA PHASE-1

## Round1654 current state

Round1654 pre-match prediction remains frozen.

- P_production = P_base
- PREDICTION_SNAPSHOT_FIXED=1
- P_BASE_MUTATED=0
- PURCHASE_FINAL_FIXED=0
- ACTUAL_PURCHASE=0
- EVALUATION_MODE=PAPER_ONLY

Do NOT modify the frozen Round1654 P_base or frozen 9600 PURE_PBASE snapshot.

Current postmatch status remains provisional until all 13 results are final and web-rechecked.

## Main finding tonight

The current TOTO LABO bottleneck is not primarily lack of collected data.

The main problem is:

DATA
-> EVIDENCE
-> WARNING
-> ALLOCATION

was not sufficiently connected.

FootyStats / Football LAB / XI / hot-zone / event / external sensors were collected,
but because many layers had no approved historical OOF probability transport,
they often failed to influence final finite-budget review.

Important correction of architecture:

"not approved to modify P_base"
must NOT mean
"ignore the information when reviewing ticket allocation."

Unvalidated evidence may remain probability coefficient = 0 while still being used as:

- warning
- routing
- review trigger
- omitted-outcome audit
- research feature

subject to historical OOF validation before production hard rules.

## No6 長崎-C大阪 audit

Frozen P_base:

- HOME 0.414672
- DRAW 0.268374
- AWAY 0.316954

Pre-match evidence structure:

- FootyStats: HOME support / strong directional signal
- Football LAB process: opposition to HOME direction
- XI strength: opposition to P_base direction
- hot-zone: opposition to P_base direction
- totoONE: HOME single, but 1|0 protection existed

Interpretation:

This does NOT prove that DRAW 0 should have been predicted.

However, it does show that the match should not have passed as simple NO_ACTION / confident HOME single without a source-split review.

Research classification candidate:

SOURCE_SPLIT
SINGLE_REVIEW
DRAW_RECHECK_CANDIDATE

Do NOT convert this into a production rule from Round1654 alone.

## No11 藤枝-大宮 audit

Frozen P_base:

- HOME 0.326671
- DRAW 0.271827
- AWAY 0.401502

Pre-match evidence structure:

- FootyStats: AWAY support
- Football LAB process: AWAY support
- hot-zone: AWAY structural support
- XI strength: opposition toward HOME side
- MATCH KARTE: ADJUST_CANDIDATE
- totoONE single: DRAW 0
- totoONE buy: 0|2
- FootyStats timing/HALF completeness had fallback limitations

Frozen 9600 selection:
2|1

Omitted:
0

Omitted P_base probability:
0.271827

Interpretation:

AWAY as main direction was defensible from multiple sources.

However, removing DRAW while retaining HOME requires explicit re-review because:
- DRAW probability was meaningful
- XI opposed AWAY consensus
- totoONE explicitly protected DRAW
- MATCH KARTE already flagged ADJUST_CANDIDATE
- some FootyStats timing information was incomplete/fallback

This is a strong candidate for OMITTED_OUTCOME_RISK research.

Do NOT claim that DRAW was certain or that totoONE should automatically override P_base.

## EVIDENCE / WARNING / ALLOCATION formal direction

New standard architecture:

P_base
-> EVIDENCE
-> WARNING
-> OMITTED OUTCOME AUDIT
-> ALLOCATION

P_base remains independently frozen unless an exact historical OOF probability transport method is approved.

WARNING means:
REVIEW REQUIRED

WARNING does NOT mean:
AUTOMATIC PICK CHANGE

## EWA v0.1 primary warning variables

Initial formal research variables:

1. PBASE_ISOLATION
2. SOURCE_SPLIT
3. DRAW_PRESS
4. HIGH_ENTROPY
5. DATA_QUALITY_WARNING
6. DRAW_SENSOR
7. OMITTED_OUTCOME_RISK

Mandatory supporting fields include:

- top_prob
- gap_top2
- entropy_norm
- opposing_sources_n
- draw_support_n
- review_required
- warning_level
- pbase_structure
- candidate_outcomes
- omitted_outcome
- omitted_prob
- allocation_reason
- probability_modified
- oof_status

## Historical evidence already known

Existing historical work must remain authoritative.

LOW_GAP and DRAW_PRESS already have historical diagnostic evidence.

Historical BASELINE96 already absorbs much endogenous uncertainty.

External opposition has historical value as an error-warning concept.

However:

warning validity != allocation validity

Historical external-consensus hard allocation did not establish sufficient improvement to replace BASELINE probability allocation.

Therefore EWA must first operate as a review/audit layer.

## Data-quality principle

From now on distinguish:

DATA_EXISTS
from
DATA_IS_RELIABLE

Track explicitly:

- small sample
- missing values
- parser incompleteness
- fallback values
- temporal availability
- source independence
- historical comparability
- OOF status

A fallback/incomplete source must not silently receive a LOW_RISK interpretation.

Exact thresholds require historical validation.

## Planned formal files

Specification target:

docs/TOTO_LABO_EVIDENCE_WARNING_ALLOCATION_SPEC_v01.md

Round1654 table target:

data/analysis/match_karte/1654/toto1654_evidence_warning_allocation_v01.csv

These are PLANNED.
Do not claim they exist until actually created.

## EWA Phase-1 next session

Absolute next task:

1. Freeze EWA v0.1 column schema.
2. Build Round1654 13-match EWA table using PREMATCH DATA ONLY.
3. No outcome/result fields may participate in warning construction.
4. Reproduce warnings for all 13 matches.
5. Inspect especially No6 / No10 / No11.
6. Separate warning generation from allocation action.
7. Define historical-reconstructable variables.
8. Rebuild on historical 61 toto rounds / 793 matches where possible.
9. Evaluate:
   - SINGLE failure rate
   - omitted-outcome hit rate
   - DOUBLE omitted-direction failure
   - hit13
   - hit12+
   - hit11+
   - portfolio model coverage
10. Use nested / walk-forward OOF where required.
11. Do not promote a warning into a production allocation rule without evidence.

## Historical availability constraints

XI/player simple probability transport has already been OOF tested and rejected.

Hot-zone comparable historical multi-round data is currently insufficient.

Therefore:

- XI probability coefficient remains 0
- hot-zone probability coefficient remains 0
- neither may silently alter P_base

They may remain EWA research/warning sensors.

DRAW_SENSOR history may be incomplete and should be accumulated prospectively if causal historical reconstruction is unavailable.

## Simulation status

1,000,000-per-match simulation work is NOT abandoned.

However deeper match-flow simulation is deferred until the data-to-decision layer is improved.

Future target:

prematch data
-> calibrated match parameters
-> 90-minute match-flow simulation
-> score distribution
-> flow distribution
-> 1X2
-> EWA
-> finite-budget allocation

Do not run a more complicated Monte Carlo merely to reproduce unchanged P_base probabilities.

## Current conclusion

Tonight's most important learning:

TOTO LABO has become good at collecting data,
but needs a formal mechanism to ensure collected evidence reaches final review without being confused with unvalidated probability modification.

The EWA layer is intended to solve this.

EWA_PHASE1_STATUS=SPEC_DIRECTION_FIXED
EWA_V01_SCHEMA_FIXED=0
EWA_1654_TABLE_CREATED=0
EWA_HISTORICAL_OOF_STARTED=0
DEEP_1M_MATCHFLOW_SIM_DEFERRED=1


---

# EWA V0.2 FORMALIZATION CHECKPOINT — 2026-09-20

## Purpose

Formalize the new TOTO LABO decision layer:

P_base
-> EVIDENCE
-> WARNING
-> WARNING TARGET AUDIT
-> ALLOCATION REVIEW

The purpose is to prevent collected prematch evidence from disappearing
between probability generation and finite-budget allocation.

## Governance

Round1654 remains frozen.

- P_base mutated = 0
- probability_modified = 0
- P_production = P_base
- prediction snapshot fixed = 1
- actual purchase = 0
- evaluation mode = PAPER_ONLY

WARNING does NOT mean automatic pick change.

WARNING means:
the current ticket structure must be checked against the specific outcome
that the warning is pointing toward.

## EWA v0.2 artifacts created

Builder:

scripts/build_toto_ewa_v02.py

Specification:

docs/TOTO_LABO_EVIDENCE_WARNING_ALLOCATION_SPEC_v02.md

Round1654 table:

data/analysis/match_karte/1654/toto1654_evidence_warning_allocation_v02.csv

Builder QA:

- ROWS = 13
- ALLOCATION_REVIEW = 8
- DATA_REVIEW = 5
- EWA_V02_QA = PASS

## Critical v0.2 distinction

These two concepts are now formally separate:

1. structure_expanded
2. warning_target_absorbed

Example:

selection = 2|1
warning target = 0

means:

structure_expanded = 1
warning_target_absorbed = 0

Therefore DOUBLE/TRIPLE status alone must never be interpreted as
"the warning has been absorbed."

## Round1654 allocation review matches

Current frozen 9600 PURE_PBASE structure generates allocation review for:

- No3 清水 vs 千葉
- No4 岡山 vs 京都
- No6 長崎 vs C大阪
- No7 横浜FM vs 水戸
- No9 G大阪 vs 神戸
- No10 山形 vs 富山
- No11 藤枝 vs 大宮
- No12 新潟 vs 磐田

No8 町田 vs 柏 was corrected during v0.2 formalization.

totoONE:
- single = 1
- buy = 1|2

Therefore No8 does NOT have totoONE draw protection.
Its opposing WIN direction is already covered by frozen 1|2,
so current EWA v0.2 allocation_review_required = 0.

## Warning families

Current operational/research fields include:

- SOURCE_SPLIT
- PBASE_ISOLATION_CANDIDATE
- LOW_GAP
- DRAW_PRESS
- TOTOONE_DRAW_PROTECTION
- HOTZONE_OPPOSITION_RESEARCH
- DATA_QUALITY_WARNING

Supporting fields include:

- warning_target_outcomes
- structure_expanded
- warning_target_absorbed
- unabsorbed_warning_outcomes
- unabsorbed_opposition
- unabsorbed_draw_press
- omitted_outcomes
- omitted_prob_total
- omitted_max_prob
- omitted_draw_prob
- allocation_review_required
- data_review_required
- overall_review_required

## Historical OOF facts already established

Historical finite-budget population:

- 61 complete toto rounds
- 793 matches
- 2023 = 20 rounds
- 2024 = 20 rounds
- 2025 = 21 rounds

BASELINE96:

- fixed structure = 7 singles + 5 doubles + 1 triple
- hit13 = 1
- hit12+ = 2
- hit11+ = 5
- mean model coverage approximately 0.001232

Existing warning diagnostics:

LOW_GAP:
- threshold: top1-top2 < 0.03
- useful historical error-warning region
- BASELINE96 already expanded all historical LOW_GAP cases in the prior audit

DRAW_PRESS:
- threshold: P(draw) >= 0.27
- historical draw-risk diagnostic
- must not be converted directly into an automatic DRAW allocation rule

Historical external opposition:
- 2+ opposition matches = 135
- BASELINE96 allocation:
  SINGLE = 15
  DOUBLE = 91
  TRIPLE = 29
- structural expanded rate = 120/135 = 0.8889

IMPORTANT:

STRUCTURAL EXPANSION is NOT the same as WARNING TARGET ABSORPTION.

Do not reuse the historical 120/135 expansion number as proof that
the actual opposing outcome was selected.

Exact historical warning_target_absorbed reconstruction remains a
separate EWA validation task.

## Safety correction

Do NOT record or promote any unverified claim such as:

"2+ opposition unabsorbed = 16 and 13/16 failed"

unless it is reproduced under a prespecified definition of:
- warning target outcome
- source consensus/tie handling
- allocation absorption

and validated from the historical dataset.

## Current interpretation

EWA is not a probability transport layer.

It is currently a decision-audit layer that asks:

"What prematch outcome is the evidence warning about,
and is that exact outcome present in the current finite-budget structure?"

This allows unvalidated current signals to remain probability coefficient = 0
while still preventing collected evidence from disappearing before allocation review.

## Next task

1. Reconstruct historical EWA target definitions using the 61-round / 793-match portfolio dataset.
2. Predefine exact target logic for historical external opposition.
3. Measure:
   - warning_target_absorbed
   - actual omitted hit
   - omitted probability
   - draw omission
   - opposition omission
4. Separate:
   WARNING VALIDITY
   from
   ALLOCATION VALIDITY.
5. Use DESIGN 2023-2024 for rule development.
6. Keep 2025 as confirmation / holdout where applicable.
7. Do not alter Round1654 frozen P_base or snapshot.

EWA_V02_SPEC_FIXED=1
EWA_V02_1654_TABLE_CREATED=1
EWA_V02_QA_PASS=1
EWA_HISTORICAL_TARGET_ABSORPTION_VALIDATION=NEXT
P_BASE_MUTATED=0


---

# MORNING CLOSE CHECKPOINT — 2026-09-20 — EWA HISTORICAL TARGET ABSORPTION

## Current EWA state

EWA v0.2 remains the formal current specification.

Created and QA-passed:

- scripts/build_toto_ewa_v02.py
- docs/TOTO_LABO_EVIDENCE_WARNING_ALLOCATION_SPEC_v02.md
- data/analysis/match_karte/1654/toto1654_evidence_warning_allocation_v02.csv

Round1654:

- ROWS = 13
- ALLOCATION_REVIEW = 8
- DATA_REVIEW = 5
- EWA_V02_QA = PASS
- probability_modified = 0
- P_base remains frozen and unchanged
- ACTUAL_PURCHASE = 0
- EVALUATION_MODE = PAPER_ONLY

## Historical portfolio dataset

Historical finite-budget population was reloaded from:

- data/evaluation/portfolio_oof_clean_matches_2023_2025.csv
- data/evaluation/portfolio_oof_clean_rounds_2023_2025.csv

Exact population:

- rounds = 61
- matches = 793
- 2023 = 20 rounds
- 2024 = 20 rounds
- 2025 = 21 rounds

BASELINE96 was exactly reproduced.

Per round structure:

- SINGLE = 7
- DOUBLE = 5
- TRIPLE = 1
- combinations = 96

Across 61 rounds:

- SINGLE rows = 427
- DOUBLE rows = 305
- TRIPLE rows = 61

Reproduced portfolio results:

- hit13 = 1
- hit12+ = 2
- hit11+ = 5
- mean model coverage = 0.001231539756

2025 confirmation:

- hit13 = 0
- hit12+ = 1
- hit11+ = 3
- mean model coverage = 0.001490535083

## Historical external-opposition target definition

Historical external sources:

1. FootyStats
2. team2
3. JLeague
4. Elo

For each match:

- determine v1-C P_base Top1
- determine each external source Top1
- opposition_count =
  number of external Top1 directions different from P_base Top1

For opposition_count >= 2:

- collect the opposing source outcomes
- warning_target_outcome =
  modal opposing outcome
- if the modal count is tied, preserve all tied target outcomes

warning_target_absorbed = 1
only if all target outcomes are included in the BASELINE96 selection.

This definition is prematch/result-blind.

## Historical target absorption result

2+ external opposition:

- total = 135 matches

Warning target absorption:

- absorbed = 120
- unabsorbed = 15

For the 15 unabsorbed matches:

- BASELINE96 ticket failed = 13/15
- failure rate = 0.866667
- actual result equaled one of the warning target outcomes = 8/15
- target-hit rate = 0.533333

Temporal split:

DESIGN 2023-2024:
- unabsorbed = 10
- ticket failures = 9/10

CONFIRM 2025:
- unabsorbed = 5
- ticket failures = 4/5

Interpretation:

UNABSORBED_OPPOSITION is a strong candidate
for identifying dangerous current ticket structures.

However:

- sample size is small
- warning target is not the actual result in every failure
- therefore it is NOT an automatic opposite-pick rule
- it is NOT an automatic DOUBLE rule
- it remains an allocation-review priority signal

Important corrected exact result:

2+ opposition:
- absorbed 120
- unabsorbed 15
- unabsorbed failures 13/15

Do not use the earlier informal 16-case figure.

## DRAW_PRESS target audit

DRAW_PRESS definition remains:

P_base(draw) >= 0.27

Historical 793-match population:

- DRAW_PRESS = 274 matches

Among those 274:

- DRAW 0 was actually included in BASELINE96 = 58
- draw-target absorption rate = 58/274 = 0.211679

Historical DOUBLE rows:

- total DOUBLE = 305
- DOUBLE selections containing DRAW 0 = 0

Therefore historical BASELINE96 DOUBLE structures always omitted DRAW.

Actual DRAW rate among DOUBLE rows:

P(draw) < 0.27:
- n = 151
- actual draw rate = 0.231788

P(draw) >= 0.27:
- n = 154
- actual draw rate = 0.298701

2025 confirmation DOUBLE rows:

P(draw) < 0.27:
- n = 60
- actual draw rate = 0.216667

P(draw) >= 0.27:
- n = 45
- actual draw rate = 0.288889

Interpretation:

DRAW_PRESS identifies a higher-draw-risk region even within DOUBLE rows.

However:

DRAW_PRESS -> automatic DRAW insertion
is NOT approved.

Warning validity and allocation validity remain separate.

## Main learning from this morning

The key EWA concept is now:

STRUCTURE EXPANDED
is not the same as
WARNING TARGET ABSORBED.

The operational question is:

"What exact outcome is the prematch evidence warning about,
and does the current finite-budget ticket actually contain that outcome?"

This allows TOTO LABO to use collected evidence
without forcing unvalidated signals into P_base.

## Production decision

Current production policy remains unchanged:

P_production = P_base
-> finite-budget BASELINE probability optimization

EWA is currently:

DECISION_AUDIT / REVIEW_PRIORITY

not:

AUTOMATIC_ALLOCATION_OVERRIDE

No automatic opposite-pick rule is approved.
No automatic DRAW rule is approved.
No automatic DOUBLE rule is approved.

## EWA v0.3 status

EWA v0.3 is a RESEARCH_CANDIDATE only.

Candidate priority signals:

- UNABSORBED_OPPOSITION
- UNABSORBED_DRAW_PRESS

Specific priority-bonus magnitudes are NOT fixed in this checkpoint.

Any bonus/priority rule must be:

1. implemented reproducibly
2. chosen using DESIGN 2023-2024 only
3. tested once on 2025 CONFIRM
4. compared at the same ticket budget
5. judged on:
   - hit13
   - hit12+
   - hit11+
   - mean hits
   - model coverage
   - warnings rescued
   - protections displaced elsewhere

Do not tune repeatedly against 2025.

## Absolute next task

1. Materialize a historical EWA target-absorption artifact for all 793 matches.
2. Save exact columns:
   - opposition_count
   - warning_target_outcomes
   - warning_target_absorbed
   - unabsorbed_opposition
   - draw_press
   - draw_target_absorbed
   - omitted_outcomes
   - omitted probabilities
   - actual result
   - actual omitted hit
3. Build a reproducible EWA v0.3 allocation-priority experiment.
4. Use 2023-2024 DESIGN only for selection/tuning.
5. Keep 2025 as untouched confirmation for the fixed candidate.
6. Do not modify frozen Round1654 P_base or snapshot.

EWA_V02_SPEC_FIXED=1
EWA_V02_1654_TABLE_CREATED=1
EWA_V02_QA_PASS=1
EWA_HISTORICAL_TARGET_ABSORPTION_VALIDATED=1
UNABSORBED_OPPOSITION_RESEARCH_SIGNAL=1
UNABSORBED_DRAW_PRESS_RESEARCH_SIGNAL=1
EWA_V03_STATUS=RESEARCH_CANDIDATE
EWA_V03_BONUS_FIXED=0
PRODUCTION_BASELINE96_UNCHANGED=1
P_BASE_MUTATED=0



# 2026-09-21 — NIGHT CLOSE CHECKPOINT
## ROUND1656 / VARIABLE-BUDGET EWA / DATA-USAGE AUDIT

### 1. ROUND TARGET CORRECTION

- Round1655 is NOT the main 13-match toto target for the next full analysis.
- Round1655 work created during this session must not be reused as the formal 13-match production/audit target.
- Next full 13-match TOTO LABO target = Round1656.
- Round1655 13-row skeleton generated earlier is retained only as an implementation test artifact.
- Do not treat the Round1655 skeleton as a valid Round1655 match dataset.
- Round1656 manifest / source acquisition is NEXT.

Flags:

ROUND1656_MAIN_TARGET=1
ROUND1655_13ROW_SKELETON_PRODUCTION_VALID=0
ROUND1655_SKELETON_STATUS=IMPLEMENTATION_TEST_ONLY


### 2. VARIABLE-BUDGET ALLOCATION DESIGN

Round1656 finite-budget analysis will NOT be fixed to 96 lines.

Standard research budget ladder:

- 100 yen = 1 line
- 200 yen = 2 lines
- 300 yen = 3 lines
- 400 yen = 4 lines
- 500 yen = 5 lines
- 600 yen = 6 lines
- 700 yen = 7 lines
- 800 yen = 8 lines
- 1200 yen = 12 lines
- 2400 yen = 24 lines
- 4800 yen = 48 lines
- 7200 yen = 72 lines
- 9600 yen = 96 lines
- 14400 yen = 144 lines

Primary allocation representation:

LINE_SET

Reason:
arbitrary line counts such as 5 / 7 lines cannot always be represented cleanly
as a standard rectangular SINGLE / DOUBLE / TRIPLE product.

Comparison plans:

- PURE_PBASE
- EWA_SHADOW

Core architecture:

DATA
-> SENSOR MATRIX
-> WARNING
-> WARNING TARGET
-> BUDGET-SPECIFIC LINE_SET
-> TARGET ABSORPTION AUDIT
-> FINAL CANDIDATE

Governance:

- P_base remains the probability anchor.
- Warning validity != allocation validity.
- Warning signals do not automatically modify probability.
- Research-only signals remain probability coefficient 0.
- EWA_SHADOW is an allocation/review research layer.
- probability_modified = 0
- probability_transport_status = P_BASE_UNCHANGED


### 3. GOOGLE SHEETS AUDIT DESIGN

Google Sheets compatible workbook design was created for:

DATA -> WARNING -> ALLOCATION

Main logical sheets:

- Match_Audit
- Line_Set
- Budget_Audit
- Budget_Summary
- README

Match_Audit is intended to contain:

- P1 / P0 / P2
- PbaseTop
- Gap
- FootyStats direction
- Football LAB direction
- XI direction
- market direction
- totoONE
- Soccer Hihyo
- hotzone
- data-quality fields
- LOW_GAP
- DRAW_PRESS
- SOURCE_SPLIT
- PBASE_ISOLATION_CANDIDATE
- TOTOONE_DRAW_PROTECTION
- warning_target_outcomes

Budget_Audit checks whether each budget-specific LINE_SET actually absorbs
the warning target outcomes.

Important:

structural expansion != warning-target absorption.


### 4. MATCH AUDIT AUTO-BUILDER

Created:

scripts/build_toto_match_audit_v01.py

Local execution was confirmed for Round1655 implementation test:

ROWS=13
PBASE_COMPLETE=0/13
WARNING_TARGET_ROWS=0
DATA_QUALITY_WARNING_ROWS=13
PROBABILITY_MODIFIED_SUM=0
QA_CORE=PASS

Output test artifacts:

data/analysis/match_karte/1655/toto1655_data_warning_allocation_audit_v01.csv
data/analysis/match_karte/1655/toto1655_data_warning_allocation_audit_v01.qa.json

Interpretation:

- Builder itself ran successfully.
- P_base was not found.
- Optional sources were not found.
- No values were fabricated.
- DATA_QUALITY_WARNING=13 at skeleton stage reflects missing inputs,
  not evidence that all 13 matches have genuinely poor data quality.

This Round1655 output is now implementation-test-only because the main
13-match target has been corrected to Round1656.


### 5. FOOTYSTATS / FOOTBALL LAB DATA-USAGE POLICY

Problem identified:

Collecting rich FootyStats / Football LAB data is insufficient if the final
decision layer collapses everything into only one source direction.

Required architecture:

RAW DATA
-> SEMANTIC BLOCK
-> BLOCK SIGNAL
-> SOURCE SUMMARY
-> WARNING
-> ALLOCATION REVIEW

Every collected data block must terminate in an explicit usage status:

- USED_PBASE
- USED_WARNING
- USED_ALLOCATION_REVIEW
- USED_DATA_QUALITY
- RESEARCH_ONLY
- BLOCKED_BY_OOF
- BLOCKED_BY_MISSING

No collected feature should silently disappear from the decision audit.


### 6. FOOTYSTATS USAGE PRINCIPLES

FootyStats should preserve semantic families rather than treating correlated
metrics as independent votes.

Representative semantic families:

- VENUE_PROCESS
- VENUE_FORM
- MATCH_CONTEXT
- MATCHUP_XG
- MARKET

Raw / supporting families include:

- ATTACK
- DEFENSE
- xG
- SHOTS
- HALF
- TIMING
- H2H
- PLAYERS
- ODDS

Rules:

- xG / shots / SOT / conversion are NOT independent votes merely because
  separate columns exist.
- MATCHUP_XG is recombined/algebraic evidence, not an independent source vote.
- MARKET is not a generic independent vote.
- missing data must not be fabricated.
- semantic SPLIT must remain SPLIT.
- SPLIT must not be converted into an opposing HOME/AWAY vote.


### 7. FOOTBALL LAB USAGE PRINCIPLES

Preserve Football LAB components separately:

- BUILD_UP
- WIDTH_CARRY
- FINISHING
- RECOVERY
- PROCESS
- DEFENSIVE_LAST_LINE
- HOTZONE
- XI

Critical rules:

- process_internal_split=1 -> PROCESS direction = SPLIT.
- Do NOT force HOME/AWAY from process_mean when process_internal_split=1.
- DEFENSIVE_LAST_LINE is contextual pressure information,
  not currently a directional win-strength vote.
- hotzone remains structural / research-only.
- XI/player probability transport remains blocked by OOF evidence.
- XI/hotzone may still be used for disagreement / review routing.
- correlated Football LAB axes are not independent source votes.


### 8. FEATURE USAGE AUDIT SCRIPT STATUS

A separate prototype was created:

build_toto_feature_usage_audit_v01.py

Purpose:

FootyStats x Football LAB semantic-block usage audit.

However:

- it was NOT successfully installed/executed in the local repository tonight.
- workflow became unnecessarily complicated by adding a second script.

Decision:

DO NOT require the user to run multiple audit scripts in normal Round1656 work.

NEXT IMPLEMENTATION:

merge Feature Usage Audit functionality into the main Round audit builder so
normal operation can be reduced to approximately one command.

Desired future command:

python scripts/build_toto_match_audit_v01.py --round 1656

That single command should eventually handle:

- source discovery
- Match_Audit generation
- FootyStats semantic usage audit
- Football LAB semantic usage audit
- WARNING generation
- usage-status audit
- QA output


### 9. ROUND1656 NEXT ACQUISITION

NEXT SESSION START:

1. Create / confirm Round1656 13-match manifest.
2. Confirm fixture identity.
3. Check FootyStats Round1656 page freshness.
4. Acquire FootyStats:
   13 matches x HOME / H2H / AWAY = target 39/39 pages.
5. Preserve RAW HTML.
6. Run integrity QA.
7. Parse / normalize / semanticize using existing round-generic pipeline.
8. Check Football LAB freshness for Round1656.
9. Acquire available Football LAB match/team data.
10. Preserve process / CBP / hotzone / XI-related source layers separately.
11. Feed collected evidence into the unified Match_Audit builder.
12. Do not modify P_base from unvalidated current-source evidence.

FootyStats known reusable pipeline from prior rounds:

scripts/fetch_footystats_round_3html_v02.py
scripts/parse_footystats_round_full_v02.py
scripts/normalize_footystats_round_v05.py
scripts/build_footystats_feature_blocks_v02.py
scripts/build_footystats_feature_semantic_v04.py

Target FootyStats integrity:

HOME 13/13
H2H 13/13
AWAY 13/13
TOTAL 39/39
BAD_MATCH_SETS=0

On HTTP 429:

STOP.
Preserve downloaded pages.
Resume later.
Do not bypass rate limiting.


### 10. GOVERNANCE CARRYOVER

Existing frozen Round1654 artifacts remain untouched.

Round1656 development must preserve:

P_BASE_MUTATED=0

External/current-only signals may be:

WARNING
ALLOCATION_REVIEW
DATA_QUALITY
RESEARCH_ONLY

until historical validation supports stronger use.

No new current-source feature may silently become a production probability
coefficient.


### NIGHT CLOSE STATUS

ROUND1656_MAIN_TARGET=1
VARIABLE_BUDGET_EWA_DESIGN_FIXED=1
GOOGLE_SHEETS_AUDIT_DESIGN_CREATED=1
MATCH_AUDIT_BUILDER_IMPLEMENTED=1
MATCH_AUDIT_BUILDER_TEST_PASS=1
FEATURE_USAGE_AUDIT_CONCEPT_FIXED=1
FEATURE_USAGE_SECOND_SCRIPT_LOCAL_EXECUTED=0
UNIFIED_ONE_COMMAND_BUILDER=NEXT
ROUND1656_MANIFEST=NEXT
ROUND1656_FOOTYSTATS_39_PAGE_ACQUISITION=NEXT
ROUND1656_FOOTBALL_LAB_REFRESH_ACQUISITION=NEXT
P_BASE_MUTATED=0



# 2026-09-21 — MATCH ENGINE DIRECTION CHECKPOINT
## ROUND1656 — FULL FOOTYSTATS + FOOTBALL LAB 90-MINUTE SIMULATION

### 1. CORE OBJECTIVE

Round1656 の主要研究目標を次に固定する。

FootyStats と Football LAB から取得可能な全パラメータを広く取り込み、
単純な HOME / DRAW / AWAY vote に圧縮せず、

RAW DATA
-> SEMANTIC PARAMETER
-> MATCHUP
-> MATCH FLOW
-> 90-MINUTE SIMULATION
-> SCORE DISTRIBUTION
-> P(1/0/2)

へ変換する。

最終目標:

- 各対象試合について90分の試合展開を文字通り生成する。
- 得点時刻・先制・追いつき・逆転・試合状態変化を扱う。
- 最終スコアを生成する。
- 同一カードを最大 1,000,000 回シミュレーションする。
- P(HOME), P(DRAW), P(AWAY) を算出する。
- 0-0, 1-0, 1-1, 2-1, 1-2 等のscore distributionを算出する。
- P_base と P_sim を比較する。
- 最後に有限予算TOTO allocationへ接続する。

IMPORTANT:

1,000,000 simulations do NOT improve a bad match model.

まず「1回の90分シミュレーションがサッカーの試合として妥当であること」
を確認し、その後に 10K -> 100K -> 1M と増やす。


### 2. FOOTYSTATS ROLE

FootyStats は主として:

"WHAT HAPPENED / HOW MUCH"

を表すデータ源として扱う。

対象例:

- RESULT / FORM / PPG
- ATTACK
- DEFENSE
- xG / xGA
- HOME / AWAY venue xG
- goals scored / conceded
- shots
- shots on target
- shots off target
- shot conversion
- shots per goal
- clean sheets
- failed to score
- BTTS
- Over / Under
- first-half / second-half
- first-score
- 10-minute timing
- 15-minute timing
- scored timing
- conceded timing
- possession
- territory
- corners
- cards
- fouls
- offsides
- set-play / other
- H2H
- player per90
- odds / market
- other FULL RAW fields

FootyStats full data must NOT be reduced to MATCHUP_XG alone.

xG / shots / SOT / conversion etc. are correlated and must NOT be
counted as independent votes.


### 3. FOOTBALL LAB ROLE

Football LAB は主として:

"HOW THE MATCH IS PLAYED"

を表すデータ源として扱う。

CBP examples:

- attack CBP
- pass CBP
- cross CBP
- dribble CBP
- receive CBP
- shoot CBP
- goal CBP
- ball-winning CBP
- defence CBP
- save CBP

Team Style examples:

- attack set play
- left-side attack
- central attack
- right-side attack
- short counter
- long counter
- opposition-half possession
- own-half possession
- physical contact
- line-break run
- high pressing
- middle pressing
- counter press
- high block
- middle block
- low block

Player Style / XI examples:

- finishing
- shooting
- pass response
- pass chance creation
- cross chance creation
- dribble chance creation
- build-up
- attacking aerial
- defensive aerial
- defending
- ball winning

Spatial layer:

- HOTZONE
- 6 x 9 = 54 cells per team
- attack direction normalized before matchup use

Football LAB data must NOT be compressed prematurely into only:

HOME / AWAY / SPLIT.

PROCESS summary may remain diagnostic,
but original component values must remain traceable.


### 4. ALL-PARAMETER USAGE PRINCIPLE

"Use all parameters" does NOT mean:

every column = one vote.

Instead:

ALL RAW PARAMETERS
-> SEMANTIC GROUPS
-> MATCH ENGINE LATENT PARAMETERS

Candidate latent / engine parameters:

- ATTACK_CREATION
- DEFENSIVE_RESISTANCE
- BUILD_UP
- PRESS_RESISTANCE
- PRESSING
- WIDTH_ATTACK
- CENTRAL_ATTACK
- TRANSITION_ATTACK
- COUNTER_RISK
- SHOT_VOLUME
- SHOT_QUALITY
- FINISHING
- KEEPER_EFFECT
- SETPLAY_THREAT
- TEMPO
- FIRST_SCORE_STRENGTH
- EARLY_GAME_STRENGTH
- LATE_GAME_STRENGTH
- SCORE_STATE_RESPONSE
- CLEAN_SHEET_STRENGTH
- COLLAPSE_RISK
- DRAW_RESISTANCE
- PLAYER_XI_POWER
- DATA_UNCERTAINTY

Every collected field should have a traceable status:

- USED_MATCH_STRENGTH
- USED_MATCHUP
- USED_MATCH_FLOW
- USED_PLAYER_XI
- USED_UNCERTAINTY
- RESEARCH_ONLY
- BLOCKED_BY_OOF
- BLOCKED_BY_MISSING

No collected parameter should silently disappear.


### 5. MATCHUP PRINCIPLE

The key new layer is:

HOME ATTACK
x
AWAY DEFENSE

and

AWAY ATTACK
x
HOME DEFENSE.

Examples:

FootyStats HOME xG
x
Football LAB AWAY block structure

Football LAB HOME high press
x
AWAY own-half possession / build-up

HOME left-side attack
x
AWAY right-side defensive structure

HOME line-break runs
x
AWAY last-line behaviour

HOME possession
x
AWAY counter strength

HOME timing / first-score
x
AWAY early conceded timing

HOTZONE attacking cells
x
opponent defensive / positional structure

Predicted XI
x
player Football LAB / FootyStats power


### 6. MATCH FLOW ENGINE

The intended simulation is NOT:

P_base
-> random 1/0/2 draw.

The intended simulation is:

MATCH START
-> possession
-> progression
-> pressure / press resistance
-> attacking zone
-> chance creation
-> shot
-> shot quality
-> goal / no goal
-> score-state update
-> tactical / risk response
-> next phase
-> 90 MINUTES
-> FINAL SCORE

Important:

After a goal, the process must change.

Example:

HOME leads 1-0

HOME:
- may reduce attacking risk
- may lower tempo
- may increase defensive protection

AWAY:
- may increase attacking risk
- may push possession higher
- may increase shot volume
- may also expose counter risk

The match after 1-0 is not identical to the match at 0-0.


### 7. HISTORICAL FEEDBACK — WINS / LOSSES

Past wins and failures must be fed back into the new engine.

However:

DO NOT create hindsight rules such as:

"FootyStats was right once, therefore always trust FootyStats."

Past results should be converted into:

MISSED MATCH-FLOW PATTERNS.

Candidate feedback templates:

#### PBASE_ISOLATION

P_base points one way while multiple independent/external structures
point elsewhere.

Simulation use:

increase probability mass assigned to credible opposing match-flow scenarios,
without automatically replacing P_base.


#### HIDDEN_DRAW

DRAW does not always come from an explicit DRAW signal.

A draw can emerge because:

HOME win path
and
AWAY win path

cancel each other.

Simulation use:

preserve 0-0 / 1-1 / equalizing-goal paths when attack advantages are offset.


#### PROCESS_VS_RESULT_SPLIT

Historical result numbers and current process indicators may disagree.

Simulation use:

represent both pathways rather than collapsing to one direction.


#### FINISHING_OVERPERFORMANCE

Observed goals materially exceed chance quality.

Simulation use:

do not blindly extrapolate current scoring rate;
allow finishing regression.


#### FINISHING_UNDERPERFORMANCE

Chance quality is good but goals have been poor.

Simulation use:

preserve positive regression scenarios.


#### PRESS_BUILDUP_MISMATCH

One side's pressing directly attacks the opponent's build-up weakness.

Simulation use:

modify progression success,
turnover location,
chance creation,
and transition probability.


#### COUNTER_EXPOSURE

Possession / territorial dominance may create vulnerability to counters.

Simulation use:

high possession does NOT automatically imply lower defeat probability.


#### SCORE_STATE_EFFECT

Already validated score-state effects should remain a core layer.

Historical score-state calibration indicated that late in matches,
teams protecting a one-goal lead reduce scoring hazard.

Do not use arbitrary state multipliers where historical calibration exists.


#### LINEUP_POWER_DROP

Predicted XI and absences can change:

- creation
- finishing
- build-up
- defending
- keeper
- pressing

Player information should modify the relevant latent ability,
not simply create an extra HOME/AWAY vote.


#### DATA_TEMPLATE_RISK

Missing HALF / timing / venue / parser fields must increase uncertainty.

Missing data must never be silently replaced and presented as observed data.


### 8. HISTORICAL LESSONS TO PRESERVE

Historical analysis showed:

- LOW_GAP identifies a higher-error region.
- DRAW_PRESS has structural information.
- external opposition contains directional information.
- warning validity != automatic allocation validity.
- hard warning -> automatic DOUBLE/TRIPLE is not justified.
- P_base remains a valuable statistical anchor.
- FootyStats disagreement alone must not mechanically replace P_base.
- external consensus alone must not mechanically replace P_base.
- correlated features must not become multiple artificial votes.

Therefore:

Past feedback enters the MATCH ENGINE primarily through:

SCENARIO GENERATION
and
SCENARIO WEIGHTING,

not through ad-hoc final probability overrides.


### 9. ROUND1654 LESSON

Round1654 demonstrated that the important misses were not solved by
running more Monte Carlo draws from P_base.

The prior 1,000,000-per-match control simulation mainly reproduced P_base.

Therefore:

OLD:
P_base
-> 1M random outcomes

is NOT the target system.

NEW:
FootyStats full parameters
+
Football LAB full parameters
+
historical match-flow lessons
+
score-state model
+
XI / availability
+
matchup structure
-> 90-minute match simulation
-> 1M final score outcomes

is the target.


### 10. P_BASE ROLE

P_base is NOT discarded.

P_base becomes:

STATISTICAL ANCHOR / CONTROL MODEL.

For each Round1656 match compare:

- P_base
- P_sim
- score distribution
- top scorelines
- first-score probabilities
- draw pathways
- upset pathways
- source/matchup explanation

Large P_base vs P_sim disagreement must trigger forensic review,
not automatic replacement.


### 11. REQUIRED OUTPUT PER MATCH

For each Round1656 match produce at minimum:

- P_base 1/0/2
- P_sim 1/0/2
- P_sim - P_base
- expected home goals
- expected away goals
- top scorelines
- 0-0 probability
- 1-1 probability
- BTTS probability
- Over2.5 probability
- HOME first-score probability
- AWAY first-score probability
- scoreless-through-HT probability
- HOME lead-at-HT probability
- AWAY lead-at-HT probability
- equalizer probability
- comeback probability
- clean-sheet probability
- favorite survival probability
- favorite fail probability
- DRAW_PATH probability
- LOSS_PATH probability
- primary match-flow explanation
- major uncertainty sources


### 12. DEVELOPMENT ORDER FOR ROUND1656

Do NOT start from ticket optimization.

Required order:

1. Confirm Round1656 official 13-match manifest.
2. Acquire FootyStats HOME / H2H / AWAY = target 39/39.
3. Preserve FULL RAW.
4. Inventory all usable FootyStats parameters.
5. Acquire latest Football LAB data for all available teams/matches.
6. Inventory all usable Football LAB parameters.
7. Build parameter registry.
8. Build semantic groups.
9. Build HOME-vs-AWAY matchup matrix.
10. Integrate historical win/loss feedback templates.
11. Build one-match 90-minute simulator.
12. Validate a single simulated match manually.
13. Run 10,000 simulations.
14. Run 100,000 simulations.
15. Check convergence.
16. Run 1,000,000 simulations where justified.
17. Compare P_sim against P_base.
18. Only then perform finite-budget allocation.


### 13. NEXT SESSION PRIMARY GOAL

PRIMARY:

ROUND1656 FULL-DATA MATCH ENGINE.

Specifically:

FootyStats full parameter registry
+
Football LAB full parameter registry
+
historical win/loss feedback
+
matchup engine
+
90-minute score simulation.

Flags:

ROUND1656_MAIN_TARGET=1
FOOTYSTATS_FULL_PARAMETER_USE=TARGET
FOOTBALL_LAB_FULL_PARAMETER_USE=TARGET
FULL_PARAMETER_ONE_VOTE_EACH=0
MATCHUP_ENGINE=NEXT
MATCH_FLOW_ENGINE=NEXT
HISTORICAL_FAILURE_FEEDBACK=REQUIRED
HISTORICAL_FEEDBACK_AS_HARD_RULE=0
SCORE_STATE_VALIDATED_LAYER=PRESERVE
PBASE_ROLE=STATISTICAL_ANCHOR
PBASE_MUTATED=0
OLD_PBASE_ONLY_MONTE_CARLO=REJECTED_AS_FINAL_ENGINE
SIMULATION_TARGET_MAX=1000000
FINAL_SCORE_SIMULATION=TARGET
FINITE_BUDGET_ALLOCATION=AFTER_MATCH_ENGINE


# 2026-09-21 — MATCH ENGINE MORNING CHECKPOINT
## ROUND1656 — PROCESS EVENT BASELINE v02 COMPLETE

### CURRENT ROUND
Target:
- toto Round1656
- 13 matches

Card:
1. 山形 vs 鳥栖
2. 富山 vs 横浜FC
3. 徳島 vs 栃木C
4. 大宮 vs 甲府
5. 宮崎 vs 札幌
6. 秋田 vs 新潟
7. いわき vs 仙台
8. 磐田 vs 八戸
9. 今治 vs 湘南
10. 大分 vs 藤枝
11. 群馬 vs 熊本
12. 福島 vs 長野
13. 栃木SC vs 松本

---

## 2026-09-21 — ROUND1656 PROCESS EVENT BASELINE v02 CHECKPOINT

### ENGINE DIRECTION

Final target remains:

FootyStats full available parameters
+
Football LAB full available parameters
+
historical win/loss feedback
+
predicted XI / availability
+
validated score-state calibration
+
matchup structure
        ↓
90-minute match-flow engine
        ↓
final score
        ↓
10K -> 100K -> 1M simulations
        ↓
score distribution
+
P(HOME/DRAW/AWAY)
+
first score / equalizer / comeback / draw path / upset path
        ↓
compare with P_base
        ↓
finite-budget toto allocation

Important:
- P_base remains statistical anchor / control.
- New simulator must model match process, not sample 1/0/2 directly from P_base.
- Historical failure feedback is scenario/risk evidence, not hard override rules.
- Validated score-state layer must be preserved.
- Ticket optimization is after match engine completion.
- Maximum intended simulation scale = 1M per match.
- Do NOT jump to 1M before model/mapping validation.

---

### FOOTYSTATS ROUND1656 — COMPLETE

Standard pipeline:
- RAW 39/39 PASS
- FULL RAW 13/13 PASS
- normalized 13x65 PASS
- feature block 13x93 PASS
- semantic 13x69 PASS
- venue xG/xGA missing 0

Files:
- data/analysis/footystats_toto1656_normalized_v05.csv
- data/analysis/footystats_toto1656_feature_blocks_v02.csv
- data/analysis/footystats_toto1656_feature_semantic_v04.csv

Deep pipeline:
- core_profile_v04 COMPLETE
- timing_bins_v01 COMPLETE
- sim_input_v01 COMPLETE
- half_profile_v01 COMPLETE
- sim_input_v04 COMPLETE
- sim_input_v05 COMPLETE

Final deep QA:
- ROWS = 13
- COLS = 205
- fs_mu_home 13/13
- fs_mu_away 13/13
- home_half_share_target 13/13
- away_half_share_target 13/13
- PASS

Half-share clipping:
- HOME clipped 7/13
- AWAY clipped 5/13
- any clipping 8/13

Interpret clipping as DATA_UNCERTAINTY, not strong football signal.

---

### FOOTYSTATS PROCESS FIELDS — COMPLETE

Confirmed 13/13:
- shots
- SOT
- off-target
- shot conversion
- shots per goal
- possession

Explicit venue-detail process sublayer:
- unavailable for Round1656
- do NOT fabricate venue-detail values

Process transport into engine:
- data/analysis/toto1656_match_engine_input_v02.csv
- data/analysis/toto1656_match_engine_parameter_matrix_v02.csv
- data/analysis/toto1656_match_engine_parameter_readiness_v02.csv
- data/analysis/toto1656_match_engine_parameter_contract_v03.csv

QA:
- INPUT_V02_ROWS = 13
- INPUT_V02_COLS = 289
- MATRIX_V02_ROWS = 13
- MATRIX_V02_COLS = 160
- all required process fields NULL = 0
- MATCH_ENGINE_PARAMETER_MATRIX_V02_QA=PASS

---

### FOOTBALL LAB ROUND1656 — COMPLETE THROUGH MATCHUP MATRIX

2026/27 J2 + J3 CBP:
- 20 raw category pages
- team CBP tables joined
- player top30 ranking preserved as limited-coverage source

Lossless extract:
- data/analysis/football_lab_2026_27_1656_cbp_cells_raw_v01.csv
- data/analysis/football_lab_2026_27_1656_cbp_schema_v01.csv

Team / match artifacts:
- data/analysis/football_lab_2026_27_1656_team_cbp_long_v01.csv
- data/analysis/football_lab_2026_27_1656_team_cbp_wide_v01.csv
- data/analysis/football_lab_2026_27_1656_player_cbp_top30_long_v01.csv
- data/analysis/football_lab_toto1656_team_cbp_v01.csv
- data/analysis/football_lab_toto1656_feature_blocks_raw_v01.csv
- data/analysis/football_lab_toto1656_team_semantic_z_v01.csv
- data/analysis/football_lab_toto1656_matchup_matrix_v01.csv

QA:
- target team slots = 26
- unmatched = 0
- match rows = 13
- matchup NULL cells = 0
- PASS

Important:
- defense/save/gain CBP may represent workload/exposure.
- They are not direct defensive-strength votes.
- J2/J3 axes are standardized within own league.
- Cross-league contrasts remain RESEARCH_UNCALIBRATED.

---

### MATCH ENGINE INPUT / PARAMETER MATRIX

Match Engine Input v01:
- data/analysis/toto1656_match_engine_input_v01.csv
- 13 rows
- 269 cols
- Football LAB NULL cells = 0
- PASS

Parameter Matrix v01:
- 13 rows
- 128 cols
- timing cols = 54
- PASS

Parameter Matrix v02:
- 13 rows
- 160 cols
- FootyStats shots/SOT/quality/possession restored into engine layer
- PASS

Current major inputs available:
- xG
- timing
- first score
- first-half profile
- shots
- SOT
- shot-quality descriptors
- possession
- Football LAB attack/build-up/width/shot/finishing
- Football LAB matchup contrasts
- validated historical score-state lookup

Pending:
- PLAYER_XI_POWER
- calibrated transport coefficients for research process/matchup signals

---

### VALIDATED SCORE-STATE LAYER — PRESERVE

Lookup:
- data/analysis/score_state_lookup_v01.csv

Structure:
- 20 rows
- 4 time bands
- 5 score states

Time bands:
- 00-30
- 31-60
- 61-75
- 76-90

Score states:
- DRAW
- HOME_LEAD1
- AWAY_LEAD1
- HOME_LEAD2P
- AWAY_LEAD2P

Historical validation:
- 2018-2025 J.League
- n = 8741 matches
- strength-adjusted Poisson GLM
- time_bin x score_state
- walk-forward OOF 2022-2025 improved all 4 folds
- total delta NLL = -40.692

Late one-goal leader effects:
- 76-90 HOME_LEAD1 home mult = 0.623
- 76-90 AWAY_LEAD1 away mult = 0.685

Arbitrary score-state multipliers remain rejected.

---

### ROUND1656 DYNAMIC EXACT CONTROL — COMPLETE

Artifacts:
- data/analysis/toto1656_dynamic_sim_input_v01.csv
- data/analysis/toto1656_dynamic_sim_input_v02_timing.csv
- data/analysis/toto1656_dynamic_exact_control_v01.csv
- data/analysis/toto1656_dynamic_score_distribution_control_v01.csv

Structure:
- 13 matches
- 10 timing bins per match
- 130 rows

Timing conservation:
- MAX_HOME_MU_ERR = 6.66e-16
- MAX_AWAY_MU_ERR = 4.44e-16
- timing shares sum approximately 1

Exact score-state engine:
- probability sum machine-precision valid
- score distribution mass machine-precision valid
- MAX_SCORE_STATE_DELTA = 0.007579

Conclusion:
- score-state remains a moderate match-flow adjustment layer.
- It is not a large arbitrary outcome-flipping mechanism.

QA:
- TOTO1656_DYNAMIC_CONTROL_QA=PASS

---

### 10-BIN MONTE CARLO CONTROL — COMPLETE

Artifact:
- data/simulations/toto1656_dynamic_mc_control_10k_v01.csv

10K per match:
- total simulations = 130,000
- MAX_ABS_EXACT_MC_DIFF = 0.010301
- MAX_Z = 2.191
- probability sums valid

QA:
- TOTO_DYNAMIC_MC_CONTROL_QA=PASS

This simulator is not P_base categorical resampling.
It generates goals across time bins and derives final 1/0/2 from final score.

---

### MINUTE MATCH FLOW CONTROL — COMPLETE

Artifact:
- data/simulations/toto1656_minute_matchflow_control_10k_v01.csv
- data/simulations/toto1656_minute_matchflow_score_dist_10k_v01.csv
- data/simulations/toto1656_minute_matchflow_trace_match01_10k_v01.csv

Minute engine:
- 90 minute steps
- score-state reevaluated every minute
- goal-event ordering retained
- first score tracked
- equalizers tracked
- comeback wins tracked
- lead-to-loss paths tracked
- HT state tracked
- score distribution tracked

10K QA:
- MAX_NONE_EXACT_MC_DIFF = 0.010062
- MAX_NONE_Z = 2.181
- FIRST_SCORE_SUM_MAX_ERR approximately 0
- HT_SUM_MAX_ERR = 0
- SCORE_DIST_MASS_MAX_ERR = 0
- PASS

Trace manually inspected:
- score_before / score_after valid
- state_before / state_after valid
- next-minute hazard changes with score-state lookup
- PASS

Important:
minute timing currently uses:
- UNIFORM_WITHIN_10BIN

This is 1-minute simulation resolution.
It does NOT imply FootyStats observes true 1-minute hazard.

---

### MINUTE EXACT CONTROL — COMPLETE

Artifacts:
- data/analysis/toto1656_minute_exact_control_v01.csv
- data/analysis/toto1656_minute_exact_score_distribution_control_v01.csv

QA:
- MAX_NONE_EXACT_DELTA = 1.67e-16
- MAX_TRUE_RESOLUTION_DELTA = 0.001993
- state probability sum valid
- score distribution mass valid
- MC10K vs minute exact max diff = 0.008472
- MC10K vs minute exact max Z = 2.010
- PASS

Interpretation:
- splitting identical Poisson intensity into minutes changes nothing without score-state.
- pure 10-bin -> minute score-state resolution effect is small, max about 0.20 percentage points.

---

### MINUTE MONTE CARLO 100K — COMPLETE

100K per match:
- total simulations = 1,300,000

Minute MC vs minute exact:
- MAX_ABS_DIFF = 0.002998
- MAX_Z = 1.988

QA:
- TOTO1656_MINUTE_MC_100K_QA=PASS

Conclusion:
- CONTROL Monte Carlo implementation is stable.
- Future changes can be attributed to added process layers rather than simulator implementation noise.

---

### PROCESS SIGNAL AUDIT — COMPLETE

Artifacts:
- data/analysis/toto1656_process_signal_matrix_v01.csv
- data/analysis/toto1656_process_signal_registry_v01.csv
- data/analysis/toto1656_process_signal_correlation_v01.csv
- data/analysis/toto1656_process_signal_highcorr_v01.csv

Signals:
- total = 32
- Football LAB diagnostic only = 6
- Football LAB research transport candidates = 20
- FootyStats research transport candidates = 6

Candidate QA:
- transport candidates = 26
- NULL cells = 0
- max |Z13| = 2.7725
- PASS

Strong redundancy confirmed:
- FL ATTACK vs BUILD approximately 0.99
- many PM vs R5 axes approximately 0.9+
- FS SHOTS vs SOT = 0.819
- FS SOT_RATE vs CONVERSION = 0.811

Rule:
- correlated process metrics are NOT independent votes.

---

### PROCESS TRANSPORT CONTRACT / LOCAL SENSITIVITY — COMPLETE

Artifacts:
- data/analysis/toto1656_process_transport_contract_v01.csv
- data/analysis/toto1656_process_local_sensitivity_detail_v01.csv
- data/analysis/toto1656_process_local_sensitivity_summary_v01.csv

Research-only sensitivity-active representatives:
- FL_MATCHUP_BUILD_RECOVERY_PM
- FL_MATCHUP_WIDTH_DEFENSE_PM
- FL_MATCHUP_FINISH_KEEPER_PM
- FS_SHOTS_EDGE
- FS_SOT_RATE_EDGE
- FS_POSSESSION_EDGE

Blocked/shadow:
- Football LAB direct process axes
- R5 duplicates
- correlated SHOT_DEFENSE / ATTACK_DEFENSE matchup axes
- FS SOT
- FS conversion
- FS shots-per-goal
- activity/load metrics remain diagnostic only

All:
- production_beta = 0
- research beta probe = 0.01 only for sensitivity-active signals

Local sensitivity QA:
- BETA_ZERO_CONTROL_MAX_ERR = 8.33e-17
- probability sums machine-precision valid
- detail rows = 78
- PASS

Important interpretation:
- local sensitivity ranking is NOT predictive-value ranking.
- all signals used same symmetric goal-hazard perturbation in this diagnostic.
- observed differences mainly reflect |Z13| and match-specific engine elasticity.

---

### PROCESS CHANNEL CONTRACT — COMPLETE

Artifacts:
- data/analysis/toto1656_process_channel_contract_v01.csv
- data/analysis/toto1656_process_sensitivity_structure_audit_v01.csv
- data/analysis/toto1656_process_sensitivity_concentration_v01.csv

Same-channel probe:
- MAX_WITHIN_MATCH_ELASTICITY_SPREAD = 2.48e-05
- confirms previous sensitivity ranking was mostly transport geometry / |Z| effect

Six semantic channels:

1.
FL_MATCHUP_BUILD_RECOVERY_PM
-> CHANCE_CREATION
-> BUILD_UP_VS_RECOVERY

2.
FL_MATCHUP_WIDTH_DEFENSE_PM
-> CHANCE_CREATION
-> WIDTH_ENTRY

3.
FL_MATCHUP_FINISH_KEEPER_PM
-> SHOT_QUALITY
-> FINISHING_VS_KEEPER

4.
FS_SHOTS_EDGE
-> SHOT_VOLUME
-> SHOT_GENERATION

5.
FS_SOT_RATE_EDGE
-> SHOT_QUALITY
-> SHOT_ON_TARGET_RATE evidence

6.
FS_POSSESSION_EDGE
-> POSSESSION_TEMPO
-> BALL_SHARE

For all six:
- direct_goal_hazard_transport = 0
- production_beta = 0
- research only
- coefficient uncalibrated

QA:
- ACTIVE_CHANNEL_SIGNALS = 6
- PASS

---

### PROCESS EVENT BASELINE v01 — REJECTED

Attempted hard chain:

shot
-> SOT
-> goal

with:

P(goal | SOT) = fs_mu / SOT

This failed probability feasibility for one case.

Diagnostic:
- Match 3 徳島 vs 栃木C
- fs_mu_home = 1.695
- fs_sot_home = 1.67
- fs_mu / SOT = 1.01497

Therefore:
- xG-derived fs_mu cannot be interpreted as goals generated only through observed SOT count.
- SOT cannot be a mandatory hard gate in the current aggregate data model.

v01 is rejected as event semantics.
Do not revive without a properly calibrated shot-quality / xG-by-shot model.

---

### PROCESS EVENT BASELINE v02 — COMPLETE

Artifacts:
- data/analysis/toto1656_process_event_baseline_v02.csv
- data/analysis/toto1656_process_event_minute_baseline_v02.csv
- data/analysis/toto1656_process_event_channel_bindings_v02.csv

Revised CONTROL process:

shot arrival
        ↓
P(goal | shot)
        ↓
goal

SOT:
- retained as shot-quality evidence / descriptor
- NOT a mandatory hard gate for goal event

CONTROL identity:

shots * P(goal | shot) = fs_mu

where:

P(goal | shot) = fs_mu / shots

Probability feasibility:
- p_sot_given_shot home BAD = 0
- p_sot_given_shot away BAD = 0
- p_goal_given_shot home BAD = 0
- p_goal_given_shot away BAD = 0
- possession priors BAD = 0

Match reconstruction:
- MAX_MU_RECON_ERR = 2.22e-16
- MAX_SOT_RECON_ERR = 8.88e-16
- possession prior sum error = 2.22e-16

Minute reconstruction:
- shots home max err = 5.33e-15
- shots away max err = 7.11e-15
- SOT home max err = 2.66e-15
- SOT away max err = 1.78e-15
- mu home max err = 6.66e-16
- mu away max err = 6.66e-16
- minute goal lambda max err = 6.94e-18

Rows:
- MATCH_ROWS = 13
- MINUTE_ROWS = 1170
- BINDING_ROWS = 6

Channel bindings v02:

FL_MATCHUP_BUILD_RECOVERY_PM
-> CHANCE_CREATION
-> shot_lambda
-> LOG_RATE_SHIFT
-> production_weight 0

FL_MATCHUP_WIDTH_DEFENSE_PM
-> CHANCE_CREATION
-> shot_lambda
-> LOG_RATE_SHIFT
-> production_weight 0

FS_SHOTS_EDGE
-> SHOT_VOLUME
-> shot_lambda
-> LOG_RATE_SHIFT
-> production_weight 0

FS_SOT_RATE_EDGE
-> SHOT_QUALITY
-> p_goal_given_shot
-> QUALITY_EVIDENCE_LOGIT_SHIFT
-> production_weight 0
-> SOT_NOT_HARD_GATE

FL_MATCHUP_FINISH_KEEPER_PM
-> SHOT_QUALITY
-> p_goal_given_shot
-> LOGIT_SHIFT
-> production_weight 0

FS_POSSESSION_EDGE
-> POSSESSION_TEMPO
-> possession_prior
-> LOGIT_SHIFT
-> production_weight 0
-> NO_DIRECT_GOAL_EFFECT

QA:
- TOTO1656_PROCESS_EVENT_BASELINE_V02_QA=PASS

---

### CURRENT MODEL GOVERNANCE

Validated / active:
- FootyStats fs_mu
- FootyStats v05 timing
- validated historical score-state lookup

Current CONTROL process representation:
- shot_lambda
- P(goal|shot)
- SOT quality evidence
- possession prior

Research-only / coefficient zero:
- Football LAB matchup signals
- FS shot-volume modifier
- FS SOT-rate quality modifier
- FS possession modifier

Blocked from independent-vote treatment:
- highly correlated Football LAB axes
- PM/R5 duplicates
- shots/SOT/conversion redundancies

Pending:
- historical OOF calibration of process transports where feasible
- XI/player-power layer
- uncertainty shrinkage policy
- P_base Round1656 generation/comparison

P_base Round1656:
- NOT YET GENERATED

---

### NEXT START POINT

DO NOT jump to PROCESS weights or 1M yet.

Next exact task:

PROCESS EVENT BASELINE v02
        ↓
shot Poisson
        ↓
goal Binomial thinning
        ↓
validated score-state
        ↓
100K PROCESS-EVENT CONTROL
        ↓
compare with minute exact CONTROL

Required next gate:

process-event CONTROL 100K
vs
data/analysis/toto1656_minute_exact_control_v01.csv

Expected:
- process-event CONTROL reproduces existing minute CONTROL within Monte Carlo error
- shot totals reproduce FootyStats expectation
- goal totals reproduce fs_mu expectation before score-state effects
- score distribution / 1X2 probability sums valid

Only after this PASS:

CONTROL
        ↓
research PROCESS v01
        ↓
CHANCE_CREATION
SHOT_VOLUME
SHOT_QUALITY
POSSESSION_TEMPO
        ↓
CONTROL difference analysis
        ↓
10K
        ↓
100K
        ↓
eventually 1M

Do not assign production coefficients merely from Round1656 Z13 sensitivity.

---

### CANONICAL HANDOFF

Canonical state file:
- /Users/tsujiyoshikazumbp/Desktop/toto_analysis/TOTO_LABO_STATE.md

This file remains the canonical project handoff.

Next conversation start phrase can be:

"Round1656 PROCESS EVENT BASELINE v02 PASS済み。
TOTO_LABO_STATE.mdの最新checkpointから、
process-event CONTROL 100K vs minute exact の検証を再開。"


## 2026-09-22 Round1656 forensic / OOF update

### P_base vs process divergence
- Round1656 P_base and match-flow CONTROL were compared.
- Large divergences were identified, especially matches 1, 2, 7, 13.
- 4 top-pick flips were observed: No1, No7, No9, No13.
- CONTROL is anchored closely to deep FootyStats fs_mu.
- P_base uses a different lambda-generation path:
  - Stage1 Poisson model with J.League + legacy FootyStats pre-match xG
  - Stage2 meta transform using Stage1 lambda + multisource 1X2 log-odds.

### Stage2 forensic
- Stage2 formula was fully decomposed.
- No7 flips from AWAY-favored at Stage1 to HOME-favored after multisource adjustment.
- No13 receives a strong HOME-side multisource shift.
- No1 and No9 already diverge materially at Stage1.

### FootyStats semantic split
legacy:
- fs_csv_home_team_pre_match_xg
- fs_csv_away_team_pre_match_xg

deep:
- fs_mu_home = (home_xg + away_xga) / 2
- fs_mu_away = (away_xg + home_xga) / 2

These are not the same metric and must not be treated as interchangeable.

Round1656 semantic audit:
- edge sign conflicts: 7 / 13
- HIGH or CRITICAL value-gap cases: 11 / 13
- max absolute value gap: 0.965

### Historical OOF comparison
Common population:
- 2826 matches
- 2023: 952
- 2024: 939
- 2025: 935

ALL:

P_base
- 1X2 logloss: 1.052290
- goal Poisson NLL: 2.880309
- goal MAE: 0.892600

legacy FootyStats pre-match xG
- 1X2 logloss: 1.071107
- goal Poisson NLL: 2.908494
- goal MAE: 0.915656

deep composite fs_mu
- 1X2 logloss: 1.066839
- goal Poisson NLL: 2.899779
- goal MAE: 0.908994

Composite minus legacy:
- 1X2 logloss: -0.004269
- goal NLL: -0.008715
- goal MAE: -0.006663

Interpretation:
- deep composite fs_mu is better than legacy FootyStats xG as a standalone FootyStats baseline.
- P_base remains better than both overall.

### Walk-forward stack test
Strict folds:
- train 2023 -> test 2024
- train 2023-2024 -> test 2025

After fixing an actual-result dtype bug:

ALL_WF 1874:
- P_base 1X2 logloss: 1.042950
- composite 1X2 logloss: 1.060641
- stack 1X2 logloss: 1.044748

Stack minus P_base:
- 1X2 logloss: +0.001798
- goal NLL: +0.008289
- goal MAE: +0.008600

Conclusion:
- No validated evidence that direct composite fs_mu stacking improves P_base.
- P_base remains the statistical anchor.
- deep fs_mu remains the mechanistic match-flow baseline.
- P_sim / P_base disagreement is a forensic trigger, not an override.
- production process weights remain 0.

### Current next step
Run historical P_base vs composite disagreement audit:
- EDGE_SIGN_FLIP
- PICK_CONFLICT
- ABS_GAP_GE_20PT

Goal:
Determine whether large disagreement subsets justify a PBASE_ISOLATION / forensic tag.

### Still pending
- XI / player availability layer
- historical feedback model
- OOF validation for process-channel transport
- production process weights
- 1M simulation
- ticket optimization


## 2026-09-22 Match-flow / XI / 1M Worlds roadmap update

### Current capability status

#### FootyStats
- MATCHES / PLAYERS / TEAMS / TEAMS2 are ingestible and structurally understood.
- Round1656 standard/deep inputs are already built.
- Deep Round1656 simulation input reaches 13 matches x 205 columns.
- Not every FootyStats field is production-ready.
- MATCHES is the main historical / causal / OOF backbone.
- PLAYERS is reserved for the future XI/player-strength layer.
- TEAMS / TEAMS2 contain useful current-context information but season-final aggregates must not be leaked into historical pre-match training.
- Correlated FootyStats fields must not be treated as independent votes.

#### Football LAB
- J2/J3 target-team data is joined for all 26 Round1656 team slots.
- Current semantic axes:
  - ATTACK_PROCESS
  - BUILD_UP
  - WIDTH_CARRY
  - SHOT_CREATION
  - FINISHING_PROCESS
  - RECOVERY_ACTIVITY
  - DEFENSIVE_ACTIVITY
  - KEEPER_ACTIVITY
- Matchup axes:
  - BUILD vs RECOVERY
  - WIDTH vs DEFENSE
  - SHOT vs DEFENSE
  - FINISH vs KEEPER
  - ATTACK vs DEFENSE
- Football LAB information is intended primarily to alter match process rather than directly vote on 1X2.
- Production process coefficients remain 0 until historical OOF validation.

### XI / player-strength layer

This is not complete yet.

Target architecture:

predicted XI
+
official J.League player information
+
FootyStats PLAYERS
+
Football LAB player/team context
+
fantasy-soccer related availability/value information
        ↓
player matching / role matching
        ↓
starting XI strength
        ↓
bench / replacement quality
        ↓
HOME XI vs AWAY XI

Desired effects to model:
- key striker absence
- goalkeeper change
- CB pairing change
- winger / fullback mismatch
- rotation
- youth replacement
- fatigue
- injury / suspension
- expected minutes
- replacement-level drop

The goal is not to count missing players but to estimate positional and functional strength loss.

### 1M simulation status

The minute-by-minute engine is already validated at 10K and 100K scale.

Current engine capabilities include:
- 90 one-minute steps
- goal timing
- first goal
- equalizer
- comeback
- halftime state
- score-state transitions
- validated historical score-state multipliers

The engine can technically be expanded to 1,000,000 simulations.

However, production 1M is intentionally postponed until:
- XI layer is stronger
- process coefficients are historically validated
- time-profile inputs are finalized
- zone / matchup transport is validated

Principle:
Do not run a wrong model 1,000,000 times merely to create false precision.

### 1,000,000 WORLDS concept

The final simulation should not be only:

HOME %
DRAW %
AWAY %

It should represent one million possible 90-minute match worlds.

Outputs should include:

#### Core outcome
- HOME / DRAW / AWAY
- score distribution
- expected goals
- exact-score frequency

#### Match path
- first-goal side
- equalizer probability
- comeback probability
- lead-protection probability
- late winner probability
- 0-0 path
- high-scoring path
- upset path

#### Story classification
Candidate story classes:
- HOME CONTROL
- AWAY CONTROL
- HOME PUNCH
- AWAY PUNCH
- COMEBACK
- CHAOS
- STALEMATE
- LATE DRAMA

Representative simulated worlds may be displayed as:

18' HOME GOAL
54' AWAY GOAL
79' AWAY GOAL
FT 1-2

Story:
AWAY COMEBACK

Frequency:
X / 1,000,000 simulations

### Time-profile integration

The future match-flow engine should use team-specific scoring and conceding tendencies by match period.

Candidate time bands:
- 0-15
- 16-30
- 31-45
- 46-60
- 61-75
- 76-90

The same overall expected-goal total can therefore produce different match stories.

Example:
- early-pressure team
- second-half team
- late-scoring team
- late-collapse team

Time-profile effects must be historically validated and should interact with score-state.

### Hot-zone / attack-route integration

Target spatial structure:

ATTACK ZONES
- LEFT
- CENTER
- RIGHT

PROCESS
- BUILD-UP
- WIDTH
- BOX ENTRY
- SHOT CREATION
- FINISHING

Example matchup:

HOME right-side attack strength
vs
AWAY left-side defensive weakness

        ↓
route-specific chance creation
        ↓
shot arrival
        ↓
shot quality
        ↓
goal probability

Only real available source data should be used.
Do not fabricate unavailable zone-level detail.

Candidate source inputs:
- Football LAB
- FootyStats
- J.League official data
- available player data

Possible inputs:
- attack direction
- crosses
- penalty-area entries
- shot location
- ball recovery area
- touches / possession area
- creation route

Unavailable fields remain UNAVAILABLE.

### Target Match DNA

Each team should eventually be represented through:

TIME
- 0-15
- 16-30
- 31-45
- 46-60
- 61-75
- 76-90

ZONE
- LEFT
- CENTER
- RIGHT

PROCESS
- BUILD_UP
- WIDTH
- SHOT_CREATION
- FINISHING
- DEFENSE
- KEEPER

STATE
- DRAW
- LEAD1
- TRAIL1
- LEAD2+
- TRAIL2+

XI
- STARTING_STRENGTH
- BENCH_STRENGTH
- AVAILABILITY
- ROLE_CHANGE
- FATIGUE

### Desired future simulation architecture

P_base
+
FootyStats
+
Football LAB
+
predicted XI
+
player strength
+
availability / fatigue
+
time-specific scoring/conceding profile
+
hot zones / attack routes
+
validated score-state calibration
+
matchup structure
        ↓
minute-by-minute 90-minute match-flow engine
        ↓
1,000,000 simulated match worlds
        ↓
HOME / DRAW / AWAY
+
score distribution
+
first goal
+
equalizer
+
comeback
+
late winner
+
upset
+
route of attack
+
match story
        ↓
finite-budget toto allocation

### Current priority order

1. Complete XI / player-strength layer
2. Build and validate time-profile layer
3. Define available hot-zone / attack-route inputs
4. Validate process transport historically / OOF
5. Keep production process weights at 0 until validated
6. Run production 1M simulation only after the above
7. Add 1M WORLDS / match-story presentation
8. Ticket optimization remains the final layer

### Core design principle

P_base remains the statistical anchor.

Match-flow is not allowed to override P_base merely because it produces a different answer.

Large P_sim vs P_base disagreement remains a forensic trigger.

The long-term target is not:
"draw 1/0/2 one million times."

The target is:
"simulate one million different 90-minute football matches from validated team, player, time, zone, matchup and score-state information."

---

## CHECKPOINT 2026-09-23 02:26 JST — HISTORICAL FS PROCESS OOF

### Daily Finish

■完了:
- Historical FootyStats prematch process v01 = PASS
- 2018–2025 MATCH_ROWS = 8767
- leakage violations = 0
- 2022–2025 candidate matches = 4522
- R5 complete = 4505
- R10 complete = 4505

- Historical P_base constructionを完全特定
  - source = lambda_home_final / lambda_away_final
  - Poisson goal grid = 0..12
  - HOME / DRAW / AWAYへ集約
  - renormalize
- 1874 historical referenceでexact identity PASS
- max abs diff = 2.7755575615628914e-16
- reference P_base LogLoss = 1.042949773

- V1C full historical P_base reconstructed
  - 2023–2025 = 3428 matches
  - ALL LogLoss = 1.056594
  - ALL Brier = 0.637020

- FootyStats process -> V1C bridge = PASS
  - matched = 3428 / 3428
  - unmatched = 0
  - score mismatch = 0
  - all team mappings HIGH
  - R5/R10 usable intersection = 3416

### R5 single-channel OOF

SHOT_GENERATION:
- aggregate n = 2274
- delta LogLoss = -0.002107
- delta Brier = -0.001488
- improved in both 2024 and 2025

POSSESSION:
- aggregate delta LogLoss = -0.000346
- aggregate delta Brier = -0.000315
- improved in both folds

SOT_QUALITY:
- aggregate delta LogLoss = +0.000003
- no incremental value

### R10 single-channel OOF

SHOT_GENERATION:
- aggregate n = 2274
- P_base LogLoss = 1.046976
- model LogLoss = 1.044078
- delta LogLoss = -0.002898
- delta Brier = -0.002072
- improved in both 2024 and 2025
- beta sign stable
- stronger than R5

POSSESSION:
- delta LogLoss = -0.000549
- delta Brier = -0.000459
- improved in both folds

SOT_QUALITY:
- delta LogLoss = +0.000097
- beta sign unstable
- current candidate exclusion

### R10 SHOT + POSSESSION OOF

2024:
- train corr SHOT/POS = 0.404463
- joint SHOT beta = 0.021442
- joint POS beta = 0.012656
- BOTH vs SHOT delta LL = -0.000014
- BOTH vs SHOT delta Brier = -0.000011

2025:
- train corr SHOT/POS = 0.374918
- joint SHOT beta = 0.075125
- joint POS beta = 0.012658
- BOTH vs SHOT delta LL = -0.000108
- BOTH vs SHOT delta Brier = -0.000116

Aggregate:
- P_base LL = 1.046976
- SHOT LL = 1.044078
- SHOT + POSSESSION LL = 1.044017
- SHOT vs P_base delta LL = -0.002898
- BOTH vs P_base delta LL = -0.002959
- BOTH vs SHOT delta LL = -0.000061
- BOTH vs SHOT delta Brier = -0.000063

Interpretation:
- improvementの大部分は SHOT_GENERATION
- POSSESSIONには小さいincremental valueの可能性
- POSSESSION joint betaは非常に安定
  - 0.012656 -> 0.012658
- SHOT betaは符号安定だが強度は不安定
  - 0.021442 -> 0.075125
- production採用はまだしない

■AI学習:
- 現時点で最も再現性が高いFootyStats process signalは R10 SHOT_GENERATION
- R5/R10、2024/2025、LogLoss/Brierで同方向の改善
- POSSESSIONはSHOTと完全重複せず小さい追加情報を持つ可能性
- SOT_QUALITYは現仕様ではP_base改善に寄与しない
- current-card Z13はpredictive validationとして使わない
- P_baseは引き続きstatistical anchor

■次回:
- date-cluster bootstrap 20,000回
- SHOT vs P_base robustness確認
- SHOT+POSSESSION vs SHOT incremental robustness確認

■現在地点:
strict historical prematch data
-> canonical P_base reconstruction
-> exact match-id bridge
-> walk-forward OOF
-> R5/R10 single-channel validation
-> R10 SHOT + POSSESSION nested validation
-> NEXT: bootstrap robustness

■絶対に次やること:
- scripts/bootstrap_historical_fs_process_r10_robustness_v01.py を実行
- SHOT_LL_ROBUST_AGG を確認
- SHOT_BRIER_ROBUST_AGG を確認
- POS_INCREMENTAL_LL_ROBUST_AGG を確認
- POS_INCREMENTAL_BRIER_ROBUST_AGG を確認
- 95% CI上限が0未満か確認

■保留:
- totoONE Round1656 predicted XI recheck
- time-specific scoring/conceding profile
- hot-zone / attack-route layer
- XI historical prematch validation
- Football LAB long historical process validation
- 1M simulation
- finite-budget toto allocation
- ticket optimizationは最後

### Production Guards

- P_base mutated = False
- FS process production weight = 0
- player/XI production coefficient = 0
- target-card Z13 standardization used = False
- no process channel approved automatically
- 1M simulation postponed

---

## 本部報告

【本部報告】

■成果
・Historical FootyStats processをstrict prematch化し、leakage 0を確認。
・Historical P_base生成仕様を完全復元。
・1874試合でmachine-precision exact identityを確認。
・V1C P_base 3428試合を再生成。
・FS processとV1Cを3428/3428完全接続。
・R10 SHOT_GENERATIONが2024/2025の両foldでP_baseを改善。
・R10 SHOT aggregate delta LogLoss = -0.002898。
・POSSESSIONにも小さい追加改善を確認。
・SOT_QUALITYは現時点で候補から外す方向。
・production P_base / process weightは変更していない。

■AIが学習したこと
・最も再現性が高いprocess signalは現時点でSHOT_GENERATION。
・R10 windowはR5より強い。
・POSSESSIONは小さいがSHOTに対する追加情報を持つ可能性がある。
・SHOT係数は方向は安定しているが強度が年によって動く。
・平均改善だけでproduction採用せず、cluster bootstrapまで確認する必要がある。

■次回必ずやること
・date-cluster bootstrap 20,000回。
・SHOT vs P_baseの95% CI確認。
・SHOT+POSSESSION vs SHOTの95% CI確認。
・結果から次のresearch candidateを SHOT_ONLY または SHOT+POSSESSION に絞る。
・production weightは引き続き0。

【今日のAIからの一言】
今日は「現在カードでそれっぽく見えるsignal」から、
strict historical OOFでP_baseを実際に改善するsignalまで進んだ。

SHOT_GENERATIONは複数年・複数window・LogLoss/Brierで同方向。
次回のbootstrapが、次段階へ進めるかの重要な関門。




## CHECKPOINT 2026-09-24 — ROUND1656 EXACT FS R10 MATERIALIZED

### Objective reached

Round1656 current-card FootyStats R10 SHOT_GENERATION feature is now
materialized under the same temporal/measurement contract used in the
historical validation pipeline.

Historical builder contract confirmed directly from:
`scripts/build_historical_fs_prematch_process_v01.py`

Exact temporal contract:
- long table sorted by team, match_date, match_key
- groupby("team") only
- no season reset
- no league reset
- prior_match_n = group cumcount()
- lag1_match_date = group match_date shift(1)
- rolling feature = s.shift(1).rolling(10, min_periods=3).mean()
- current/target match excluded

Historical exact feature formula:

home_SHOT_GENERATION_r10 =
    0.5 * (
        home_shots_for_r10
        + away_shots_against_r10
    )

away_SHOT_GENERATION_r10 =
    0.5 * (
        away_shots_for_r10
        + home_shots_against_r10
    )

FS_SHOT_GENERATION_GAP_r10 =
    home_SHOT_GENERATION_r10
    - away_SHOT_GENERATION_r10

No target-card Z standardization is used.

### FootyStats current-data recovery

Canonical 2026 regular-league CSV/DB source was stale:
- 2026 valid actual rows before cutoff = 99
- stale regular-league source stopped in August
- future/skeleton rows contain shots=-1 and are excluded

Round1656 team pages exposed completed fixture IDs.

Missing-window fixture inventory:
- total unique completed matches = 59
- August missing matches = 15
- September missing matches = 44

FootyStats dynamic H2H endpoint discovered:
`https://footystats.org/jp/ajax_h2h_neo.php`

Request:
- method = POST
- zzzz = fixture ID
- z = away-team FootyStats club ID
- zz = home-team FootyStats club ID

Known parameter controls passed 4/4.

Historical measurement-contract control:
2025-09-14 Montedio Yamagata 3-0 Kataller Toyama
- canonical FootyStats MATCHES shots = 12 / 18
- Ajax match-level shots = 12 / 18
- exact match = True

Therefore Ajax match-level `シュート` is validated against the historical
FootyStats MATCHES shot definition used by the R10 OOF work.

Initial bulk GET+POST approach hit HTTP 429.
Recovery switched to:
- offline reconstruction of z/zz for 59/59 fixtures
- POST-only
- slow batched requests
- no retries on 429
- checkpoint/restart-safe raw storage

Final recovery:
- 59/59 raw files present
- 59/59 reparsed
- 59/59 score exact
- 59/59 shots exact
- 59/59 z/zz contract exact
- nonnegative shots 59/59
- integer shots 59/59
- historical measurement control exact
- ERROR_ROWS = 0

Final recovered source:
`data/analysis/footystats_2026_r10_missing_window_final_v01.csv`

### 2026 combined actual source

Historical DB actual rows before 2026-09-26 cutoff:
- DB_ACTUAL_ROWS_PRE_CUTOFF = 8770
- DB_2026_ACTUAL_ROWS_PRE_CUTOFF = 99
- DB duplicate shot conflicts = 0

Recovered:
- RECOVERED_ROWS = 59
- DB/recovered overlap keys = 0
- DB/recovered shot conflicts = 0

Combined 2026 actual:
- rows = 158
- max date = 2026-09-20

Output:
`data/analysis/footystats_2026_actual_plus_recovered_v01.csv`

Skeleton rows with shots=-1 are excluded.
Only match rows strictly before 2026-09-26 are eligible.

### Round1656 team R10 prematch materialization

Output:
`data/analysis/toto1656_fs_r10_team_prematch_v01.csv`

QA:
- TARGET_TEAMS = 26
- R10_COMPLETE = 26/26
- MIN_R10_OBS = 10
- MAX_R10_OBS = 10
- TARGET_LEAKAGE_VIOLATIONS = 0
- DIRECT_TAIL_MAX_ABS_DELTA = 0.0
- LATEST_PRIOR_MATCH = 2026-09-20

Thus the historical-builder rolling implementation and an independent
direct last-10 calculation agree exactly.

### Round1656 exact FS R10 SHOT_GENERATION feature

Output:
`data/analysis/toto1656_fs_r10_shot_generation_v01.csv`

13/13 complete:

1 山形 vs 鳥栖
FS_SHOT_GENERATION_GAP_r10 = -2.8500

2 富山 vs 横浜FC
FS_SHOT_GENERATION_GAP_r10 = +4.2500

3 徳島 vs 栃木C
FS_SHOT_GENERATION_GAP_r10 = -0.1500

4 大宮 vs 甲府
FS_SHOT_GENERATION_GAP_r10 = +4.1000

5 宮崎 vs 札幌
FS_SHOT_GENERATION_GAP_r10 = -1.5000

6 秋田 vs 新潟
FS_SHOT_GENERATION_GAP_r10 = -0.8500

7 いわき vs 仙台
FS_SHOT_GENERATION_GAP_r10 = -3.2000

8 磐田 vs 八戸
FS_SHOT_GENERATION_GAP_r10 = +0.8500

9 今治 vs 湘南
FS_SHOT_GENERATION_GAP_r10 = +1.5000

10 大分 vs 藤枝
FS_SHOT_GENERATION_GAP_r10 = -0.2000

11 群馬 vs 熊本
FS_SHOT_GENERATION_GAP_r10 = -1.1500

12 福島 vs 長野
FS_SHOT_GENERATION_GAP_r10 = +2.2000

13 栃木SC vs 松本
FS_SHOT_GENERATION_GAP_r10 = +0.8500

MATCH_ROWS = 13
MATCH_FEATURE_COMPLETE = 13/13

### Research / production status

Historical OOF status remains:

RESEARCH_CANDIDATE =
R10_SHOT_GENERATION_ONLY

Historical aggregate evidence:
- ΔLL = -0.002898
- ΔBrier = -0.002072
- date-cluster bootstrap aggregate CI excludes zero for both
- 2025-only CI slightly crosses zero
- subgroup effects heterogeneous
- no post-hoc subgroup transport rule allowed

SOT_QUALITY = DROP
POSSESSION = DROP

Current feature contract:
- historical FootyStats MATCHES measurement semantics
- strict lag
- rolling10/min_periods3
- groupby team
- no target-card Z
- no future rows
- no J.League shot substitution

FS_R10_PRODUCTION_WEIGHT = 0

Do not modify production match hazard or P_base yet.

Next step:
audit and reproduce the exact historical OOF scaling / coefficient lineage
for R10_SHOT_GENERATION, then attach it to Round1656 as research-only.
Production weight remains zero until that transport is explicitly validated.


## CHECKPOINT 2026-09-24 — R10 SHOT TRANSPORT + MORNING DATA REFRESH

### 1. Historical R10 SHOT_GENERATION lineage — COMPLETE

Historical feature:

`FS_SHOT_GENERATION_GAP_r10`

Confirmed exact walk-forward mechanics:

- standardization = TRAIN_FOLD_ONLY
- scaler = `(x - train_mean) / train_sd`
- `np.std(..., ddof=0)`
- intercept = 0
- beta fit objective = training LogLoss minimization
- optimizer = bounded scalar minimize
- beta bounds = [-2.0, 2.0]
- no current-card information used in beta fitting
- no target-card Z13 standardization
- P_base is used as probability/logit anchor

Exact directional probability transport:

`logP_home += beta * z`

`logP_draw += 0`

`logP_away -= beta * z`

then softmax normalization.

Historical folds:

2024 TEST:
- train years = 2023
- train n = 1142
- train mean = -0.0462216454007172
- train sd = 1.8137558896798192
- beta = 0.0265537391065798
- delta LogLoss = -0.0022386159690233
- delta Brier = -0.0016076587092143

2025 TEST:
- train years = 2023,2024
- train n = 2282
- train mean = -0.0501687638245482
- train sd = 1.876455385635473
- beta = 0.0798629050225103
- delta LogLoss = -0.0035608795409105
- delta Brier = -0.0025385770363949

Aggregate 2024+2025 OOF:

- test n = 2274
- P_base LogLoss = 1.046975744533
- SHOT model LogLoss = 1.044077741189
- delta LogLoss = -0.002898003344
- delta Brier = -0.002071889748
- beta sign stable
- LogLoss improved both folds
- Brier improved both folds

Research status remains:

`RESEARCH_CANDIDATE = R10_SHOT_GENERATION_ONLY`

`PRODUCTION_WEIGHT = 0`

---

### 2. 2026 forward research refit — COMPLETE

The confirmed expanding walk-forward lineage was extended forward:

2023 -> 2024 test

2023+2024 -> 2025 test

therefore 2026 deployment-style research refit uses:

2023+2024+2025 historical research rows only.

Output:

`data/evaluation/historical_fs_process_r10_shot_forwardfit_2026_v01.csv`

Exact parameters:

- train years = 2023,2024,2025
- train n = 3416
- train mean = -0.048943347830935666
- train sd = 1.9281054499915753
- beta = 0.08877536743520341
- train delta LogLoss = -0.00264485523451663
- train delta Brier = -0.001879304480683297

Important:

train metrics above are fit diagnostics,
NOT new OOF validation evidence.

Historical 2024/2025 parameters were reproduced from code
to floating-point precision before the forward refit was accepted.

No target-card standardization was used.

Production weight remains zero.

---

### 3. Round1656 canonical P_base score-grid contract audit

Canonical current Round1656 source:

`data/predictions/score_model_v1c_stacked_toto1656.csv`

Current round builder:

`scripts/build_score_model_v1c_round_v01.py`

Current Round1656 P_base contract confirmed from code:

- `g = np.arange(9)`
- score grid = goals 0..8
- independent Poisson matrix
- matrix renormalized
- HOME / DRAW / AWAY aggregation

Round1656 final lambda identity:

canonical prediction file vs forensic file = exact 13/13.

Round1656 P_base reconstruction from 0..8:

- exact identity 13/13
- max absolute delta = 1.1102230246251565e-16

Historical reconstructed P_base contract is different:

`scripts/reconstruct_v1c_full_pbase_oof_v01.py`

Historical contract:

- `goals = np.arange(13)`
- score grid = goals 0..12
- independent Poisson
- HOME / DRAW / AWAY aggregation
- renormalize

Historical output explicitly labels:

`PBASE_CONSTRUCTION = POISSON_GRID_0_12_RENORMALIZED`

Therefore a real implementation contract drift exists:

- historical OOF P_base = grid 0..12
- current Round1656 P_base = grid 0..8

Observed Round1656 impact:

- max base probability difference = 6.647449979568787e-05

This is recorded as an implementation difference.
Do NOT silently rewrite either historical OOF or current production builder.

---

### 4. Round1656 R10 SHOT research transport — COMPLETE

Current exact R10 feature source:

`data/analysis/toto1656_fs_r10_shot_generation_v01.csv`

Forward research scaler/beta source:

`data/evaluation/historical_fs_process_r10_shot_forwardfit_2026_v01.csv`

Research transport output:

`data/analysis/toto1656_fs_r10_shot_research_transport_v02_grid_sensitivity.csv`

Current canonical P_base 0..8 was used as the primary current-round anchor.

Historical 0..12 contract was also transported in parallel
for grid-sensitivity QA.

Research results:

- current8 top1 flips = 2
- hist12 top1 flips = 2
- top1 flip pattern mismatch = 0
- max abs research probability shift = 0.07446047220753471
- max abs logit shift = 0.19793537500165354
- current8 vs hist12 research max delta = 6.157883878543657e-05

Top1 flips under R10 SHOT research transport:

No7:
いわき vs 仙台
- P_base top = HOME
- research top = AWAY

No9:
今治 vs 湘南
- P_base top = AWAY
- research top = HOME

The score-grid contract drift does NOT change
the Round1656 R10 SHOT top1-flip pattern.

This remains research-only.

`PBASE_PRODUCTION_MUTATED = False`

`FS_PROCESS_PRODUCTION_WEIGHT = 0`

Do NOT promote the forward-refit beta directly to production.
Beta magnitude is not stable enough across historical folds
for automatic production use.

---

### 5. 2026-09-24 morning current-information review

Morning review targets included:

- toto official
- totoONE
- FootyStats
- Football LAB
- J.League / JFA information
- representative / age-group call-up and availability information
- 2026-09-23 Emperor's Cup effects
- Sportsnavi / football media information

Operational interpretation:

2026-09-23 Emperor's Cup must be treated primarily through:

- actual starters
- minutes played
- substitution timing
- rotation
- injury / availability
- recovery interval

Do NOT translate cup scoreline alone directly into
team-strength or production probability adjustment.

Representative / age-group absences and cup fatigue
remain separate current-information / Match_Audit layers
until integrated under an explicit contract.

totoONE Round1656 should be rechecked later
because morning publication timing may lag.

---

### 6. FootyStats Round1656 morning refresh — COMPLETE

Fresh RAW snapshot:

`data/raw/footystats/round_html_refresh_20260924_110914/1656`

Acquisition:

- HOME = 13/13
- H2H = 13/13
- AWAY = 13/13
- total = 39/39
- snapshot size approximately 11 MB

Original prior RAW was preserved.

Fresh parse output:

`data/parsed/footystats_refresh_20260924_110914/toto1656_full_v02`

Parse QA:

- matches = 13
- JSON count = 13
- HOME tables = 8 each
- H2H tables = 36 each
- AWAY tables = 8 each

Fresh normalized output:

`data/analysis/footystats_toto1656_normalized_v05_refresh_20260924_110914.csv`

Normalized QA:

- rows = 13
- cols = 65
- nonnull feature count = 61 each match
- old shape = 13 x 65
- new shape = 13 x 65
- matched rows = 13/13
- changed normalized columns = 22
- matches with priority prediction-related changes = 10/13

Priority updated fields include:

- home_xg_all
- home_xg_away
- home_xga_all
- home_xga_home
- home_xga_away
- away_xg_all
- away_xg_home
- away_xga_all
- away_xga_home
- home_xga_venue
- possession_away

Notable current-data movements include:

No1 山形 vs 鳥栖:
- 山形 xGA measures slightly improved

No2 富山 vs 横浜FC:
- 富山 xG slightly reduced

No3 徳島 vs 栃木C:
- 徳島 xGA improved in refreshed FootyStats data

No4 大宮 vs 甲府:
- 甲府 away-side xG measures reduced
- largest listed away_xg_home move:
  1.31 -> 1.19

No7 いわき vs 仙台:
- いわき xG slightly reduced
- away possession 46 -> 45

No10 大分 vs 藤枝:
- 藤枝 xG measures slightly increased

No12 福島 vs 長野:
- 長野 xG measures reduced

No9 今治 vs 湘南:
no priority normalized change detected in this refresh.

No11 群馬 vs 熊本:
no priority normalized change detected.

No13 栃木SC vs 松本:
no priority normalized change detected.

Important:

FootyStats morning refresh has NOT yet been propagated into:

- deep profile
- core profile
- half profile
- sim input
- match-engine parameter matrix

Those rebuilds are NEXT.

Old normalized file was not overwritten.

`PRODUCTION_PBASE_MUTATED = False`

---

### 7. Football LAB 2026 morning refresh — RAW ACQUISITION COMPLETE

Fetcher:

`scripts/fetch_football_lab_cbp_leagues_v01.py`

Important discovery:

the script has no argparse help contract.
Calling it with `--help` caused the actual fetch to run.

It fetched:

J1:
- offense
- pass
- cross
- dribble
- receive
- shot
- goal
- gain
- defense
- save

J2:
same 10 categories.

Acquisition QA:

- J1 = 10/10
- J2 = 10/10
- total = 20/20
- HTTP = 200
- category/table validation passed

Canonical RAW was refreshed under:

`data/raw/football_lab/cbp/2026`

Morning snapshot was immediately preserved as:

`data/raw/football_lab/cbp/2026_refresh_20260924_114138`

Snapshot QA:

- files = 22
- size approximately 1.7 MB
- 20 HTML category files
- manifest_v01.csv
- manifest_v01.json

Football LAB displayed source freshness:

J1 categories:
`2026.9.21 update`

J2 categories:
`2026.9.22 update`

Therefore the 2026-09-23 Emperor's Cup should NOT be assumed
to be reflected in the current Football LAB CBP snapshot.

Existing Round1656 Football LAB analysis artifacts remain available:

- `data/analysis/football_lab_2026_27_1656_cbp_cells_raw_v01.csv`
- `data/analysis/football_lab_2026_27_1656_cbp_schema_v01.csv`
- `data/analysis/football_lab_2026_27_1656_player_cbp_top30_long_v01.csv`
- `data/analysis/football_lab_2026_27_1656_team_cbp_long_v01.csv`
- `data/analysis/football_lab_2026_27_1656_team_cbp_wide_v01.csv`
- `data/analysis/football_lab_toto1656_feature_blocks_raw_v01.csv`
- `data/analysis/football_lab_toto1656_matchup_matrix_v01.csv`
- `data/analysis/football_lab_toto1656_team_cbp_v01.csv`
- `data/analysis/football_lab_toto1656_team_semantic_z_v01.csv`

Morning Football LAB RAW has NOT yet been re-parsed
into a fresh parallel analysis set.

Do NOT fetch Football LAB again before checking this snapshot.

---

### 8. NEXT START POINT

Next session starts here:

1. Parse the Football LAB morning snapshot
   `data/raw/football_lab/cbp/2026_refresh_20260924_114138`

2. Build fresh parallel Football LAB:
   - team CBP long/wide
   - semantic Z
   - Round1656 feature blocks
   - matchup matrix

3. Compare morning Football LAB analysis
   against the existing Round1656 analysis artifacts.

4. Rebuild FootyStats morning refresh through:
   - core profile
   - half profile
   - deep profile
   - sim input
   using the refreshed normalized/current RAW contract.

5. Recompute current Round1656 research inputs only after
   source-difference QA.

6. Integrate:
   - Emperor's Cup minutes / rotation / recovery
   - representative and age-group absences
   - injury / conditioning news
   into Match_Audit / availability layers.

7. Recheck totoONE Round1656 publication.

8. Recheck toto official / J.League / club availability news
   closer to kickoff.

9. Do NOT mutate P_base or production process weights
   from these current-only updates.

Current governance remains:

`P_BASE_MUTATED = 0`

`FS_PROCESS_PRODUCTION_WEIGHT = 0`

`TARGET_CARD_Z_STANDARDIZATION_USED = False`

Current-source updates may be used as:

- RESEARCH_ONLY
- WARNING
- DATA_QUALITY
- MATCH_AUDIT
- ALLOCATION_REVIEW

until historical validation supports stronger use.

---

### 9. CANONICAL HANDOFF

Canonical state file remains:

`/Users/tsujiyoshikazumbp/Desktop/toto_analysis/TOTO_LABO_STATE.md`

Next conversation start phrase:

"9/24朝 FootyStats refresh 39/39 + normalize差分確認済み。
Football LAB morning RAW snapshot 20260924_114138取得済み。
TOTO_LABO_STATE.md最新checkpointから、
Football LAB朝版の解析・差分監査を再開。"


## CHECKPOINT 2026-09-25 — ROUND1656 FS+FL COMBINED + CONTROL REPRO PASS

### STATUS

Round1656 research pipeline has reached the point where:

- latest isolated FootyStats refresh is materialized;
- latest isolated Football LAB refresh is materialized;
- both are combined into one research engine / parameter matrix;
- canonical engine / matrix remain unchanged;
- P_base remains unchanged;
- FS and FL production weights remain 0;
- current Round1656 timing / pre-state / exact-control formulas are fully reproducible;
- next step is to materialize refreshed Round1656 control TIMING / EXACT under new filenames.

This remains RESEARCH ONLY.

---

### ROUND1656 CARD

Scheduled 2026-09-26 17:00.

1 山形 vs 鳥栖
2 富山 vs 横浜FC
3 徳島 vs 栃木Ｃ
4 大宮 vs 甲府
5 宮崎 vs 札幌
6 秋田 vs 新潟
7 いわき vs 仙台
8 磐田 vs 八戸
9 今治 vs 湘南
10 大分 vs 藤枝
11 群馬 vs 熊本
12 福島 vs 長野
13 栃木SC vs 松本

13/13 linked and aligned.

---

### FOOTYSTATS 2026 ROUND1656 REFRESH

Fresh normalized source:

data/analysis/footystats_toto1656_normalized_v05_refresh_20260924_110914.csv

Fresh deep V05:

data/analysis/footystats_1656_deep_refresh_20260924_110914/footystats_toto1656_sim_input_v05.csv

Canonical FootyStats deep files were not overwritten.

Deep refresh result:

- shape = 13 x 205
- changed columns = 33
- changed cells = 33
- all deep V05 changes occur in match No1
- fs_mu_home unchanged all 13
- fs_mu_away changed only No1
- No1 fs_mu_away:
  1.740 -> 1.715
- half_share_target unchanged all 13

Current refreshed fs_mu:

1  1.465 / 1.715
2  2.195 / 1.560
3  1.695 / 1.645
4  1.920 / 1.210
5  1.465 / 1.280
6  1.605 / 1.570
7  1.410 / 1.585
8  1.905 / 1.200
9  1.335 / 1.265
10 1.520 / 1.180
11 1.460 / 1.575
12 1.615 / 1.425
13 1.515 / 1.585

---

### FOOTYSTATS V05 -> ENGINE CONTRACT

Audit result:

- V05 shape = 13 x 205
- engine shape = 13 x 289
- shared V05 -> engine columns = 205
- exact shared columns = 205
- nonidentical shared columns = 0
- V05 columns absent from engine = 0

Therefore all 205 V05 fields have exact same-name transport into the engine.

QA:

FOOTYSTATS_1656_V05_ENGINE_MATRIX_CONTRACT_AUDIT_QA=PASS

---

### FOOTYSTATS REFRESH -> PARAMETER MATRIX TRANSPORT

Changed V05 columns = 33.

Of these:

- mapped into parameter matrix = 27
- unmapped = 6

Unmapped changed V05 fields:

- home_xga
- xg_edge
- fs_mu_away
- away_lambda_sum
- away_lambda_sum_v04
- away_lambda_v05_sum

The 27 mapped changes are FootyStats timing lambda fields transported to:

FS_TIMING_*

Matrix-reaching refresh:

- changed cells = 27
- affected matches = [1]

QA:

ENGINE_CHANGED_V05_CONTRACT_REPRODUCED = True
MATRIX_CHANGED_V05_MAPPING_VERIFIED = True
FILES_MUTATED = False

FOOTYSTATS_1656_CHANGED_V05_MATRIX_TRANSPORT_AUDIT_QA=PASS

---

### FOOTYSTATS PROCESS FORMULA CONTRACT

Direct process fields reproduced exactly:

- shots
- SOT
- off target
- shot conversion
- shots per goal
- possession pct

Derived formulas recovered exactly:

fs_home_sot_rate =
    fs_home_sot / fs_home_shots

fs_away_sot_rate =
    fs_away_sot / fs_away_shots

fs_home_possession_share =
    fs_home_possession_pct / 100

fs_away_possession_share =
    fs_away_possession_pct / 100

Current refresh process effect:

match No7 いわき vs 仙台

fs_away_possession_pct:
46.00 -> 45.00

fs_away_possession_share:
0.46 -> 0.45

Engine process changed cells = 2
Engine process changed matches = [7]

Parameter matrix process changed cells = 3:

- fs_away_possession_pct
- fs_away_possession_share
- away_POSSESSION_FS

Process governance remains:

fs_process_status =
READY_CURRENT_1656_CONTEXT

fs_process_modifier_status =
RESEARCH_UNCALIBRATED

fs_process_modifier_weight =
0.0

fs_process_venue_detail_status =
EXPLICIT_VENUE_DETAIL_UNAVAILABLE

QA:

DIRECT_PROCESS_CONTRACT_REPRODUCED = True
SOT_RATE_FORMULA_RESOLVED = True
POSSESSION_SHARE_FORMULA_RESOLVED = True
MATRIX_PROCESS_FANOUT_AUDITED = True
FILES_MUTATED = False

FOOTYSTATS_1656_PROCESS_FORMULA_MATRIX_FANOUT_QA=PASS

---

### FOOTBALL LAB ROUND1656 REFRESH

Fresh J2/J3 source snapshot:

data/raw/football_lab/cbp/2026_27_1656_refresh_20260924_233151

Fresh downstream research artifacts include:

data/analysis/football_lab_2026_27_1656_team_cbp_wide_refresh_20260924_233151_v01.csv

data/analysis/football_lab_toto1656_team_semantic_z_refresh_20260924_233151_v01.csv

data/analysis/football_lab_toto1656_matchup_matrix_refresh_20260924_233151_v01.csv

data/analysis/football_lab_toto1656_feature_blocks_raw_refresh_20260924_233151_v01.csv

data/analysis/toto1656_match_engine_input_v02_flrefresh_20260924_233151.csv

data/analysis/toto1656_match_engine_parameter_matrix_v02_flrefresh_20260924_233151.csv

Football LAB refresh reached all 13 matches.

Downstream materialization:

- engine changed FL cells = 676
- matrix changed FL cells = 676
- non-FL changed cells = 0 during FL-only refresh
- production transport weight = 0
- research status unchanged

Football LAB remains RESEARCH_UNCALIBRATED.

---

### COMBINED FS + FL RESEARCH ENGINE

Combined engine:

data/analysis/toto1656_match_engine_input_v02_fsrefresh_20260924_110914_flrefresh_20260924_233151.csv

Combined parameter matrix:

data/analysis/toto1656_match_engine_parameter_matrix_v02_fsrefresh_20260924_110914_flrefresh_20260924_233151.csv

Shapes:

ENGINE = 13 x 289
MATRIX = 13 x 160

Combined engine changes vs canonical:

FL = 676 cells
FS_V05 = 33 cells
FS_PROCESS = 2 cells
OTHER = 0 cells

TOTAL = 711 changed cells

Combined matrix changes vs canonical:

FL = 676 cells
FS_TIMING = 27 cells
FS_PROCESS = 3 cells
OTHER = 0 cells

TOTAL = 706 changed cells

All 13 matches have at least one combined change due primarily to Football LAB refresh.

Key refresh checks:

No1 fs_mu_away = 1.715

No7 fs_away_possession_pct = 45.0

No7 fs_away_possession_share = 0.45

Governance:

ENGINE_FS_PROCESS_MODIFIER_WEIGHT = [0.0]

MATRIX_FS_PROCESS_MODIFIER_WEIGHT = [0.0]

MATRIX_FOOTBALL_LAB_TRANSPORT_WEIGHT = [0.0]

Canonical/source integrity:

ALL_SOURCE_AND_CANONICAL_FILES_UNCHANGED = True

PBASE_MUTATED = False
FS_PRODUCTION_PROCESS_WEIGHT = 0
FL_PRODUCTION_TRANSPORT_WEIGHT = 0
RESEARCH_ONLY = True

QA:

TOTO1656_COMBINED_FS_FL_REFRESH_RESEARCH_ENGINE_QA=PASS

---

### MINUTE MATCHFLOW CONSUMER CONTRACT

Simulator:

scripts/run_toto_minute_matchflow_control_v01.py

The simulator has a CLI but does NOT directly consume the combined engine or parameter matrix.

Its current Round1656 inputs are:

data/analysis/toto1656_dynamic_sim_input_v02_timing.csv

data/analysis/toto1656_dynamic_exact_control_v01.csv

data/analysis/score_state_lookup_v01.csv

Current TIMING:

shape = 130 x 28
10 bins per match x 13 matches

Important fields:

- base_lambda_home
- base_lambda_away
- fs_timing_share_home
- fs_timing_share_away
- timing_lambda_home
- timing_lambda_away
- lambda_home_pre_state
- lambda_away_pre_state
- process_mult_home
- process_mult_away
- matchup_mult_home
- matchup_mult_away
- player_xi_mult_home
- player_xi_mult_away

Current control multipliers:

process_mult_home = 1.0
process_mult_away = 1.0

matchup_mult_home = 1.0
matchup_mult_away = 1.0

player_xi_mult_home = 1.0
player_xi_mult_away = 1.0

Therefore current control uses FootyStats timing + score-state only.
FS/FL process and XI are not yet active modifiers.

---

### CURRENT ROUND1656 CONTROL FORMULA REPRODUCTION

Canonical inputs audited:

FS = 13 x 205
TIMING = 130 x 28
EXACT = 13 x 20
STATE = 20 x 4

FootyStats 9-bin V05 timing was successfully reproduced into current 10-bin timing.

Timing reproduction:

base_lambda_home BAD_CELLS = 0
base_lambda_away BAD_CELLS = 0
fs_timing_share_home BAD_CELLS = 0
fs_timing_share_away BAD_CELLS = 0
timing_lambda_home BAD_CELLS = 0
timing_lambda_away BAD_CELLS = 0

Pre-state contract:

lambda_home_pre_state BAD_CELLS = 0
lambda_away_pre_state BAD_CELLS = 0

Mu conservation:

MAX_HOME_ERR =
6.661338147750939e-16

MAX_AWAY_ERR =
4.440892098500626e-16

Exact control reproduction:

all none/state probability fields,
mass fields,
mean goal fields,
and delta fields reproduced.

TIMING_BAD_CELLS = 0
PRESTATE_BAD_CELLS = 0
EXACT_BAD_CELLS = 0

EXACT_MAX_ABS_DELTA =
6.661338147750939e-16

TIMING_FORMULA_REPRODUCED = True
PRESTATE_FORMULA_REPRODUCED = True
EXACT_CONTROL_REPRODUCED = True

FILES_MUTATED = False

QA:

TOTO1656_CURRENT_CONTROL_FORMULA_REPRODUCTION_QA=PASS

---

### XI / PLAYER LAYER

Round1656 predicted XI research layer already exists.

Fomelabo is the current primary XI source.

Expected starters:

26 teams x 11 players = 286 starters

Research XI matrix exists.

Player/XI effects remain:

RESEARCH ONLY
production coefficient = 0

Do not force-map unresolved player axes.

Future target is:

predicted XI
+ player parameters
+ availability/injury
+ suspension
+ fatigue
-> team XI strength
-> validated simulator modifier

---

### PUBLIC / CURRENT INFORMATION LAYER

Before final Round1656 simulation and toto allocation, re-check fresh public information from:

- toto official
- totoONE
- J.League official
- JFA / Japan national-team information
- Sportsnavi
- サッカー批評Web

Use these primarily for:

- official schedule / cancellation changes
- suspension
- national-team availability
- injury / condition
- predicted XI
- recent match load
- rotation
- fatigue context

Do not convert qualitative news directly into arbitrary probability adjustments.

Confirmed absence/availability information should first modify player/XI scenarios.

---

### SIMULATION TARGET

Final target remains:

FootyStats
+ Football LAB
+ predicted XI / player strength
+ availability / suspension
+ fatigue
+ validated process modifiers
+ time-specific scoring/conceding
+ score-state calibration
-> literal 90-minute match process
-> repeated simulation
-> score distribution
-> H/D/A
-> story/path metrics
-> P_base comparison
-> finite-budget toto allocation

Simulation progression:

10K
-> 100K
-> 1M

1M = 1,000,000 literal match simulations.

Do NOT treat repetition count as a substitute for model validation.

Old Round1654 1M sampled a mostly zero-process control and is not the final target architecture.

---

### P_BASE GOVERNANCE

P_base remains the canonical anchor/control.

Do not mutate P_base merely because current research signals disagree.

Large P_sim vs P_base disagreement requires forensic review.

Round1656 canonical P_base remains unchanged.

---

### NEXT WORK — RESUME HERE

1. Materialize refreshed Round1656 CONTROL TIMING from:

data/analysis/footystats_1656_deep_refresh_20260924_110914/footystats_toto1656_sim_input_v05.csv

under a NEW filename.

2. Recompute refreshed Round1656 CONTROL EXACT using:

- refreshed timing
- score_state_lookup_v01

under a NEW filename.

3. Compare refreshed control vs current canonical control.

Expected principal current-data effect:

- No1 away fs_mu/timing change
- canonical files remain untouched

4. Re-audit predicted XI 286 players.

5. Build explicit XI team-strength comparison for all 13 matches.

6. Add verified availability layer:

- injury
- suspension
- national-team absence
- predicted-starter uncertainty

7. Build fatigue evidence separately from unvalidated modifiers.

8. Re-check current public sources close to kickoff.

9. Run simulation validation progression:

10K
-> 100K
-> 1M

10. Compare:

- P_base
- refreshed control
- research process scenarios
- XI scenarios

11. Only after sufficient validation, perform finite-budget toto allocation.

Current previously used budget selections were heuristic only and must not be confused with a formal optimizer.

---

### NON-NEGOTIABLE GOVERNANCE

- canonical files must not be overwritten during research refreshes
- P_base remains unchanged unless model rebuild is explicitly intended
- FS production process weight remains 0
- FL production transport weight remains 0
- XI production coefficient remains 0
- no arbitrary probability mutation
- no fabricated player/venue/news data
- no 1M production claim before model/input validation
- preserve source lineage and auditability

---

### STORY LAYER / ENTERTAINMENT PRESENTATION

Round1656 entertainment/story presentation layer is fixed as a research-only utility.

Runner:

`scripts/run_toto_story_layer_v01.py`

Purpose:

- provide minute-by-minute representative match stories for presentation/entertainment
- preserve canonical probability governance
- avoid tracing all 1,000,000 statistical simulation paths

Architecture:

1. terminal H/D/A outcome is drawn from canonical P_base
2. a separate 2,000-path minute CONTROL story pool is generated per match
3. one actual CONTROL path is selected uniformly within the already-drawn terminal outcome
4. final-score rarity is classified using refreshed minute-exact score distribution
5. RARE paths are annotated, never rerolled

Contract:

TERMINAL_SOURCE = CANONICAL_P_BASE

PATH_SELECTION = UNIFORM_WITHIN_DRAWN_OUTCOME

RARITY_SOURCE = REFRESHED_MINUTE_EXACT

STORY_POOL_PER_MATCH = 2000

REROLL_RARE = False

PROBABILITY_MODIFIED = False

MINUTE_HAZARD_MODIFIED = False

R10_PRODUCTION_WEIGHT = 0

The story layer is presentation-only.

It must NOT:

- replace P_base
- alter minute hazards
- feed story rarity back into probabilities
- select paths by maximizing drama
- reroll rare or unattractive scorelines
- promote R10 or other research-only process signals into production

The 1M statistical engine and the story layer are separate:

1M x 13 matches
-> statistical simulation / distributions / diagnostics

2K x 13 matches
-> lightweight representative-story pool only

Round1656 QA:

- all 13 story outcome buckets had available paths
- minimum outcome-bucket size in 2K pool = 392
- zero outcome buckets = 0
- 26,000 total story paths completed in sub-second scale during benchmark
- story selection reproduced identically with fixed seeds
- Python compile PASS
- canonical runner unchanged before/after story execution

Reproducibility QA:

OUTPUT_IDENTICAL = True

CANONICAL_HASH_UNCHANGED = True

Canonical minute CONTROL runner SHA256:

`99c27ae7db8ff25ccbebe0512015951b459eebf035b6c56e585195da872ce8d1`

Story runner SHA256:

`f815a2fee6ef1651e37ac078194c0bb8f880a1ce3ae40536b95c3fd91b0ce4ff`

Round1656 presentation example produced:

- COMMON = 10 matches
- NORMAL = 2 matches
- RARE = 1 match

No2 富山 6-0 横浜FC was correctly retained as a genuine RARE path.

Refreshed minute-exact conditional probability within the HOME-win outcome:

0.9559719431783084%

Do not reroll such paths.

Label them as rare presentation outcomes instead.


---

### ROUND1656 MATCHDAY EXECUTION PLAN / 2026-09-26

Round1656 toto sales deadline:

2026-09-26 16:50 JST

Target working window:

09:00-15:00 JST = main analysis work

15:00-16:00 JST = final synthesis / budget allocation / QA

16:00-16:50 JST = final public-information check and purchase buffer

Do NOT plan core analysis up to the 16:50 deadline.

Matchday priority order:

1. refresh public information relevant to Round1656
2. refresh predicted starting XI
3. map expected starters to player parameters
4. calculate XI/team strength ratios
5. review meaningful changes from:
   - toto official
   - toto ONE
   - FootyStats
   - Football LAB
   - J.League official / club official information
   - Japan national-team related information where relevant
   - Sportsnavi
   - サッカー批評Web
   - other credible football sources if materially relevant
6. identify injuries, suspensions, absences, transfers, expected rotations, formation changes, manager comments and late availability news
7. keep source hierarchy explicit:
   official sources > primary club/league information > established media > secondary commentary
8. preserve canonical P_base governance
9. keep FootyStats / Football LAB / XI research signals separate unless historically validated for production use
10. run simulation progression:
    10K -> QA -> 100K -> QA -> 1M
11. final 1M target:
    1,000,000 literal simulations per match
    13 matches = 13,000,000 total match paths
12. run story/presentation layer separately after statistical simulation
13. generate finite-budget toto selections
14. produce short Google Sheets memo reasons for each selection

Budget-output format should include:

- match number
- selection
- short reason
- evidence category

Evidence categories may include:

AI
MARKET
FootyStats
Football LAB
XI
NEWS

Do not label a reason MARKET unless current market/toto support information has actually been refreshed and checked.

Current story-layer status:

PASS

Runner:

`scripts/run_toto_story_layer_v01.py`

Story layer is presentation-only and must not modify:

- P_base
- minute hazards
- production probabilities
- R10 production weight

Story architecture remains:

CANONICAL_P_BASE terminal draw
-> 2K minute CONTROL story pool
-> uniform path selection within drawn outcome
-> refreshed minute-exact rarity label

Importance-reweight research wrapper status:

PENDING

The pending wrapper is intended to support path-level research reweighting for metrics such as:

- equalizer
- comeback
- first goal
- halftime state
- lead-to-loss
- score/story metrics

Planned architecture:

CONTROL path
-> terminal H/D/A
-> target 1X2 importance weight
-> weighted score/story metrics

This research wrapper is NOT on the critical path for the Round1656 matchday forecast.

If time pressure develops, defer importance-reweight wrapper work until after the Round1656 betting workflow is complete.

ROUND1656 MATCHDAY CRITICAL PATH:

latest information
-> predicted XI
-> player parameters
-> team strength ratio
-> source-difference review
-> 10K
-> 100K
-> 1M
-> QA
-> budget allocation
-> final memo
-> final public-information check
-> purchase before 16:50 JST


---

## ROUND1656 POST-ACTUAL-LINEUP RESEARCH STATUS — 2026-09-26

Status:

PASS

This Round1656 session is research / testing only.

Actual starting XI integration:

- official J.League actual starting XI retrieved for all 13 toto matches
- 26 teams x 11 starters confirmed
- actual XI player-strength rows = 286
- empirical strength coverage = 277 / 286 = 96.9%
- canonical baseline imputation = 9 players
- production P_base mutated = False
- XI production coefficient = 0.0

Actual-XI strength outputs:

- `data/analysis/toto1656_actual_xi_player_strength_v01.csv`
- `data/analysis/toto1656_actual_xi_team_strength_v01.csv`
- `data/analysis/toto1656_actual_xi_match_strength_v01.csv`

Official toto market refresh:

- Round1656 official voting rates refreshed after actual XI publication
- 13 / 13 matches retrieved successfully
- market is treated as a research sensor only
- P_base remains canonical production anchor

Post-XI signal conflict matrix:

- `data/analysis/toto1656_post_actual_xi_signal_conflict_matrix_v01.csv`

Signal set:

- PBASE
- RESEARCH
- ACTUAL_XI
- MARKET

Conflict count is predictor disagreement only.
It is NOT win probability and NOT an independent risk probability.

Highest four-signal disagreement:

- No2 富山 vs 横浜FC: PBASE=1 / RESEARCH=1 / XI=0 / MARKET=2
- No9 今治 vs 湘南: PBASE=2 / RESEARCH=1 / XI=0 / MARKET=2
- No10 大分 vs 藤枝: PBASE=1 / RESEARCH=1 / XI=0 / MARKET=2

Notable structured conflicts:

- No1 山形 vs 鳥栖: PBASE+MARKET=1 vs RESEARCH+XI=2
- No13 栃木SC vs 松本: PBASE+MARKET=1 vs RESEARCH+XI=2
- No5 宮崎 vs 札幌: PBASE+RESEARCH+MARKET=1 vs XI=2
- No12 福島 vs 長野: PBASE+RESEARCH+XI=1 vs MARKET=2

Post-actual-lineup finalist snapshot:

- `data/analysis/toto1656_finalist_snapshot_post_actual_lineup_v01.csv`

Finalists retained:

1. CURRENT_INFO
   - role = MARKET_ORIENTED
   - ticket = `12 / 1 / 12 / 1 / 1 / 12 / 2 / 1 / 12 / 1 / 2 / 12 / 102`

2. BALANCED_TOP
   - role = PBASE_MODEL_WORST_ORIENTED
   - ticket = `12 / 1 / 12 / 1 / 1 / 12 / 12 / 1 / 12 / 1 / 2 / 1 / 102`

3. ACTUAL_XI_HEDGE5
   - role = ACTUAL_XI_INTEGRATED
   - ticket = `12 / 1 / 12 / 1 / 12 / 12 / 2 / 1 / 12 / 1 / 2 / 1 / 102`

All three finalists have 96 lines.

Final research decision matrix:

- `data/analysis/toto1656_final_research_decision_matrix_v01.csv`

Axis leaders:

- CURRENT_INFO = MARKET axis leader
- BALANCED_TOP = PBASE axis leader
- ACTUAL_XI_HEDGE5 = RESEARCH axis leader
- ACTUAL_XI_HEDGE5 = XI coverage axis leader
- ACTUAL_XI_HEDGE5 = uplift-balance axis leader

Pareto result:

- all 3 finalists are Pareto non-dominated
- no composite score used
- no new research weights introduced
- no single finalist is mechanically selected from the no-weight diagnostics

Governance:

- P_base remains canonical production anchor/control
- FootyStats research weight = 0 unless historically validated
- Football LAB research weight = 0 unless historically validated
- XI production coefficient = 0
- R10 / minute / story research layers do not mutate P_base
- actual XI findings are research-only until separately validated for production use

Round1656 actual-XI / latest-market research phase:

COMPLETE


---

# TOTO LABO — PARTICIPATION / POSTMORTEM HISTORY v0.1

## Purpose

This section preserves lessons from each formally analyzed toto round so that
postmortem findings cannot disappear before the next round.

Important governance:

- A single-round result may create a research observation or mandatory QA item.
- A single-round result must NOT directly create a production probability rule.
- P_base remains the canonical production anchor / control model.
- Warning validity and allocation validity must remain separate.
- Historical lessons must be checked before final ticket freeze.
- Post-hoc outcome fitting is prohibited.


## Participation history

Formal 13-match TOTO LABO participation / postmortem rounds currently confirmed:

1. Round1653
2. Round1654
3. Round1656

FORMAL_PARTICIPATION_COUNT = 3

Round1655 is NOT counted as a formal participation round.

Round1655 status:

- 13-row skeleton was created as an implementation test.
- It did not contain a complete production P_base dataset.
- It must not be treated as a formal Round1655 prediction or postmortem.
- ROUND1655_SKELETON_STATUS = IMPLEMENTATION_TEST_ONLY


# POSTMORTEM 1 — ROUND1653

## Main failures / observations

Known important misses included:

- No4 町田 vs 横浜FM
  - ticket = HOME single
  - actual = DRAW

- No9 今治 vs 鳥栖
  - ticket = AWAY single
  - actual = HOME

No3 G大阪 vs FC東京 was covered by DOUBLE and was structurally important:

- external/process evidence showed a credible LOSS PATH
- the opposing scenario was preserved in the allocation

## Main lesson

Do not classify a miss merely as an upset or random tail.

For every important miss, investigate whether a credible prematch loss path
already existed.

DRAW prediction is strategically central to toto.

DRAW does not always require an explicit DRAW signal.

A DRAW can emerge because:

HOME WIN PATH
+
AWAY WIN PATH
->
mutual cancellation / equalization
->
DRAW

Therefore preserve and investigate:

- LOSS_PATH
- FAVORITE_FAIL
- HIDDEN_DRAW
- equalizer paths
- opposing win-path cancellation

## Governance learned

External opposition is useful as a warning.

However:

- SOURCE_OPPOSITION -> automatic opposite pick = REJECTED
- SOURCE_OPPOSITION -> automatic DRAW = REJECTED
- external disagreement must not automatically replace P_base

Past feedback should enter mainly through:

SCENARIO GENERATION
+
SCENARIO WEIGHTING

not arbitrary final-probability overrides.


# POSTMORTEM 2 — ROUND1654

## Main allocation lesson

Important failures included outcomes with meaningful P_base probability
being completely omitted from the finite-budget ticket.

Examples investigated included:

- meaningful DRAW probability omitted
- approximately 24% opposite-win tail omitted
- both win directions covered while DRAW was the only omitted outcome

Practical observation:

"引き分けを制するものはtotoを制する"

This remains a research principle, NOT an automatic production rule.

## Model error vs allocation error

Always separate:

MODEL ERROR
from
TICKET / FINITE-BUDGET ALLOCATION ERROR

A match can be reasonably modeled while the ticket still fails because
a meaningful outcome was deliberately omitted under budget constraints.

Therefore:

STRUCTURAL EXPANSION
!=
WARNING TARGET ABSORPTION

A DOUBLE or TRIPLE is not automatically considered successful protection.

The exact prematch warned outcome must actually be present in the ticket.

## Historical warning lessons

Preserve:

- LOW_GAP = higher-error diagnostic region
- DRAW_PRESS contains structural information
- external opposition contains directional information
- warning validity != automatic allocation validity
- hard warning -> automatic DOUBLE/TRIPLE is not justified

## Simulation lesson

Round1654 also showed that simply drawing more Monte Carlo samples from P_base
does not solve the important misses.

OLD TARGET:

P_base
-> 1,000,000 categorical outcomes

This mainly reproduces P_base.

TARGET ARCHITECTURE:

FootyStats full parameters
+
Football LAB full parameters
+
historical match-flow lessons
+
score-state model
+
XI / availability
+
matchup structure
->
90-minute match simulation
->
final score distribution
->
1/0/2 probabilities

P_base remains:

STATISTICAL ANCHOR / CONTROL MODEL

Large P_base vs simulation disagreement triggers forensic review,
not automatic replacement.


# POSTMORTEM 3 — ROUND1656

## Final result

Round1656 actual:

1 / 0 / 1 / 1 / 1 / 0 / 2 / 2 / 2 / 0 / 2 / 1 / 2

Actual DRAW matches:

- No2
- No6
- No10

Actual draw count:

3 / 13

## Finalist ticket result

The three final 96-line candidates all covered 9/13.

Common misses:

- No2 = actual DRAW
- No6 = actual DRAW
- No8 = actual AWAY
- No10 = actual DRAW

The differences between the three finalist allocations did not cause
the four misses.

The common core did.

## DRAW warning failure

The three actual DRAW matches all had prematch reasons for review.

No6:

- P_base(draw) >= 0.27
- DRAW_PRESS

No10:

- P_base(draw) >= 0.27
- DRAW_PRESS
- actual-XI strength gap approximately EVEN

No2:

- DRAW probability was not DRAW_PRESS
- win-direction gap was small
- actual-XI strength gap was approximately EVEN

Therefore Round1656 was not simply:

"draws were impossible to identify."

More accurately:

"prematch DRAW-related warning evidence existed,
but the finite-budget allocation omitted DRAW."

## Historical draw-count audit

Historical clean toto population:

- rounds = 61
- matches = 793
- seasons = 2023-2025

Actual DRAW count per 13-match round:

- mean = 3.360656
- median = 3
- minimum = 1
- maximum = 7
- Q25 = 2
- Q50 = 3
- Q75 = 4
- Q90 = 5

Historical frequency:

- DRAW count >= 2 = 88.5246%
- DRAW count >= 3 = 70.4918%
- DRAW count <= 1 = 11.4754%
- zero-draw rounds = 0 / 61

## Round1656 model draw-count structure

Round1656 P_base:

EXPECTED_DRAW_COUNT = 3.344380
MODELED_MODE_DRAW_COUNT = 3

Poisson-binomial model:

P(DRAW_COUNT = 0) = 0.020876
P(DRAW_COUNT = 1) = 0.094158
P(DRAW_COUNT <= 1) = 0.115034

P(DRAW_COUNT >= 2) = 0.884966
P(DRAW_COUNT >= 3) = 0.689063

Actual:

DRAW_COUNT = 3

Thus P_base itself described Round1656 as a normal approximately-three-draw round.

## Round1656 portfolio mismatch

All three final 96-line candidates had DRAW available only at No13.

Therefore each generated line could express only:

- 0 draws
or
- 1 draw

Round1656 final portfolio:

ACHIEVABLE_DRAW_COUNTS = [0, 1]

DRAW_COUNT_SUPPORT_MASS = 0.115034
MODEL_MASS_EXCLUDED = 0.884966

This means the final ticket structurally excluded 88.4966% of the
P_base-implied draw-count scenarios.

This is a portfolio/model consistency failure.

## Historical BASELINE96 discovery

Historical BASELINE96 was exactly reproduced over all 61 rounds.

Known reproduction:

- 7 SINGLE
- 5 DOUBLE
- 1 TRIPLE
- 96 combinations
- hit13 = 1
- hit12+ = 2
- hit11+ = 5
- mean model coverage = 0.001231539756

Important new discovery:

Historical BASELINE96 also had:

MAX_DRAWS_PER_LINE = 1

for all 61 / 61 rounds.

Therefore the Round1656 problem is NOT unique to Round1656.

It exposes a structural limitation of the historical probability-mass
maximizing BASELINE96 architecture:

it optimizes joint selected probability mass,
but it does not adequately represent the round-level draw-count distribution.

## Negative experiment — do not create a bad hard rule

Historical experiments were run with constraints:

DRAW_CAP_GE2
DRAW_CAP_GE3

Results:

Forcing >=2 or >=3 draw-capable matches increased draw-count support mass,
but did NOT improve historical hit13.

Approximate model coverage cost:

DRAW_CAP_GE2:
- mean coverage ratio vs baseline ≈ 0.939

DRAW_CAP_GE3:
- mean coverage ratio vs baseline ≈ 0.871

Therefore:

DO NOT create:

- automatic minimum-2 DRAW rule
- automatic minimum-3 DRAW rule
- automatic DRAW_PRESS insertion
- automatic draw-count matching

These remain rejected.

## Durable Round1656 lesson

The correct lesson is NOT:

"force three draws into every ticket."

The correct lesson IS:

Before every final ticket freeze, calculate and print:

1. expected draw count = sum(P_base_draw)
2. Poisson-binomial draw-count distribution
3. modeled modal draw count
4. ticket achievable draw counts
5. DRAW_COUNT_SUPPORT_MASS
6. model mass excluded by ticket draw-count structure
7. DRAW_PRESS rows with DRAW omitted
8. other prematch DRAW warnings with DRAW omitted

Then explicitly review any major mismatch.

DRAW_COUNT_SUPPORT_MASS is a:

MANDATORY_FINAL_QA metric

It is NOT currently:

- a probability transport rule
- an automatic allocation rule
- an automatic draw insertion rule

## Round1656 simulation/process lesson

The validated minute simulation control proved the engine could reproduce
its intended minute-exact probabilities.

However:

CONTROL / VALIDATION simulation
must not be confused with
the target integrated match engine.

Target remains:

full prematch data
+
match-flow structure
+
score-state
+
timing
+
XI / availability
+
matchup interaction
->
90-minute simulation

Production coefficients for unvalidated research layers remain zero.


# CROSS-ROUND DURABLE LESSONS

The following principles must be checked in future rounds.

## 1. P_base anchor

P_base remains the canonical production statistical anchor.

Do not mutate P_base from a single postmortem or unvalidated current signal.


## 2. LOSS PATH review

For every important miss:

ask whether a credible prematch LOSS PATH existed.

Do not stop at:

"upset"
or
"unpredictable."


## 3. DRAW is strategic

DRAW is structurally important in toto.

But:

DRAW importance
!=
automatic DRAW insertion.


## 4. Warning target absorption

For every warning:

identify the exact warned outcome.

Then verify whether the final finite-budget ticket actually contains it.

STRUCTURAL EXPANSION
!=
WARNING TARGET ABSORPTION


## 5. Model vs allocation

Always score separately:

- probability model quality
- finite-budget ticket allocation quality


## 6. Round-level portfolio QA

Do not inspect only 13 matches independently.

Also inspect the structure of the full 13-match portfolio.

Mandatory current metric:

DRAW_COUNT_SUPPORT_MASS


## 7. Do not count-match mechanically

Historical draw-count distribution is a QA/reference distribution.

Do not change individual probabilities merely to make the ticket contain
the historical average number of draws.


## 8. Research-only evidence governance

FootyStats / Football LAB / XI / HOTZONE / other unvalidated research signals:

- may generate warnings
- may generate scenario paths
- may trigger review
- must not automatically modify production probability without OOF validation


## 9. Correlated signals

Correlated metrics must not be counted as multiple independent votes.

Preserve semantic groups and source meaning.


## 10. Missing data

Missing data increases uncertainty.

Never silently fabricate or substitute missing observations.


# FUTURE POSTMORTEM ENTRY RULE

After each formally analyzed toto round, append:

- round number
- frozen prematch ticket
- actual result
- misses
- MODEL ERROR findings
- ALLOCATION ERROR findings
- DRAW / LOSS / FAVORITE_FAIL findings
- historical validation performed
- rejected post-hoc rules
- durable QA lessons
- production changes approved / rejected

Every new lesson must receive one status:

- OBSERVATION
- RESEARCH_CANDIDATE
- MANDATORY_FINAL_QA
- OOF_VALIDATED_PRODUCTION_RULE
- REJECTED

No lesson may silently move from OBSERVATION to PRODUCTION RULE.


TOTO_LABO_POSTMORTEM_HISTORY_V01_FIXED=1
FORMAL_PARTICIPATION_COUNT=3
ROUND1655_FORMAL_PARTICIPATION=0
DRAW_COUNT_SUPPORT_MASS_MANDATORY_FINAL_QA=1
AUTO_DRAW_INSERTION_APPROVED=0
P_BASE_MUTATED_BY_POSTMORTEM=0

---

# CHECKPOINT 2026-09-27 11:09 JST — SEMANTIC UNDERSTANDING / REDUNDANCY AUDIT

## Purpose

Round1657 prediction work was intentionally paused before further acquisition/modeling in order to verify whether FootyStats and Football LAB data are actually understood, rather than merely extracted and transported through code.

Core corrective principle:

DATA ACQUIRED != DATA UNDERSTOOD != DATA VALIDATED != DATA SAFE FOR PRODUCTION

Before new research:
1. check whether the question was already answered historically;
2. distinguish source observations from TOTO LABO derived/recombined features;
3. identify duplicated/correlated information;
4. preserve explicit usage status;
5. do not re-run settled tests without genuinely new evidence.

---

## 1. EXISTING FOOTYSTATS KNOWLEDGE — RECONFIRMED

### Official / legacy pre-match xG

Historical FootyStats fields already exist locally:

- fs_csv_home_team_pre_match_xg
- fs_csv_away_team_pre_match_xg

These are already part of the reconstructed production P_base Stage1 architecture.

Stage1:
- J.League prematch features
- FootyStats HOME/AWAY prematch xG
- separate HOME/AWAY PoissonRegressor
- Stage2 stacked meta transform
- canonical P_base output

Therefore official prematch xG was NOT a newly discovered unused field.

### Deep fs_mu

Deep FootyStats composite:

fs_mu_home = (home_xg + away_xga) / 2
fs_mu_away = (away_xg + home_xga) / 2

This is a TOTO LABO derived match-flow proxy.

It is NOT the same metric as FootyStats official prematch xG.

### Historical OOF comparison already completed

Common population:
- 2826 matches
- 2023 = 952
- 2024 = 939
- 2025 = 935

P_base:
- 1X2 logloss = 1.052290
- goal Poisson NLL = 2.880309
- goal MAE = 0.892600

legacy FootyStats prematch xG:
- 1X2 logloss = 1.071107
- goal Poisson NLL = 2.908494
- goal MAE = 0.915656

deep composite fs_mu:
- 1X2 logloss = 1.066839
- goal Poisson NLL = 2.899779
- goal MAE = 0.908994

Interpretation:
- deep fs_mu > legacy FootyStats xG as standalone FootyStats baseline
- P_base remains better than both overall

### Walk-forward stacking already tested

Strict folds:
- train 2023 -> test 2024
- train 2023-2024 -> test 2025

ALL_WF = 1874

P_base 1X2 logloss = 1.042950
composite = 1.060641
stack = 1.044748

Stack minus P_base:
- 1X2 logloss = +0.001798
- goal NLL = +0.008289
- goal MAE = +0.008600

Conclusion:
- direct deep-fs_mu stacking does NOT have validated improvement over P_base
- do not repeat this test without new hypothesis/data
- P_base remains canonical statistical anchor
- deep fs_mu remains mechanistic match-flow / forensic baseline
- production process weight remains 0

Status:
- official prematch xG = OOF_VALIDATED / USED_PBASE
- deep fs_mu = OOF_VALIDATED / RESEARCH_ONLY
- direct fs_mu -> P_base stack = REJECTED

---

## 2. FOOTYSTATS SEMANTIC LINEAGE — RECONFIRMED

Deep lineage:

venue xG / xGA
-> fs_mu
-> timing distribution
-> lambda by time bin

These are one information lineage and must NOT be counted as independent votes.

Direct process observations include:
- shots
- SOT
- off target
- conversion
- shots per goal
- possession

Recovered derived formulas:

fs_home_sot_rate = fs_home_sot / fs_home_shots
fs_away_sot_rate = fs_away_sot / fs_away_shots

fs_home_possession_share = fs_home_possession_pct / 100
fs_away_possession_share = fs_away_possession_pct / 100

Correlated FootyStats process variables must not become artificial multiple votes.

Not every one of the 205 deep columns is an independent information source.

---

## 3. FOOTYSTATS TIMING V05 — EXACT FORMULA UNDERSTOOD

RHO = 0.50

For HOME and AWAY separately:

1. reconstruct first-half and second-half timing components;
2. normalize each half to sum to 1;
3. shrink each 5-bin half-distribution 50% toward uniform 20%;
4. redistribute fs_mu according to half_share_target;
5. reconstruct the shared 41-50 bin;
6. preserve total expected goals exactly.

Formula inside each half:

new_distribution
= (1 - RHO) * observed_distribution
  + RHO * uniform_distribution

with RHO = 0.50.

Critical interpretation:

TIMING V05 changes WHEN expected goals occur.

It does NOT change HOW MANY total expected goals occur.

home_lambda_v05_sum == fs_mu_home
away_lambda_v05_sum == fs_mu_away

---

## 4. FOOTBALL LAB — OFFICIAL CBP MEANING AUDIT

Important distinction established:

A. Football LAB official CBP calculation
B. Football LAB published CBP values
C. TOTO LABO semantic recombination

Most previous code audit focused on C.

The official-source semantic audit showed that TOTO LABO must not treat the published CBP categories as automatically independent football abilities.

Team-level CBP categories used by TOTO LABO:
- offense
- pass
- cross
- dribble
- shot
- goal
- gain
- defense
- save

receive:
- PLAYER-ONLY
- no team-level CBP fabrication allowed

Primary comparison scale:
- cbp_per_match

League standardization:
- league-internal mean / population SD
- leagues standardized separately
- cross-league raw totals must not be compared directly

---

## 5. CRITICAL FOOTBALL LAB REDUNDANCY FINDING

Football LAB official definition establishes an important containment relationship:

OFFENSE contains:
- PASS
- CROSS
- DRIBBLE

The old TOTO LABO semantic builder uses:

BUILD_UP:
- offense
- pass

WIDTH_CARRY:
- cross
- dribble

FINISHING:
- shot
- goal

RECOVERY:
- gain

DEFENSIVE_LAST_LINE:
- defense
- save

Then:

PROCESS =
mean(
  BUILD_UP,
  WIDTH_CARRY,
  FINISHING,
  RECOVERY
)

This means the old semantic construction contains structural information overlap.

Most important example:

BUILD_UP
= offense + pass

while offense already includes pass/cross/dribble information.

Therefore creation information is reused inside the old semantic structure.

Historical semantic audit had already shown very high correlation:

J1:
- offense x pass = +0.986
- shot x goal = +0.621

J2:
- offense x pass = +0.987
- shot x goal = +0.844

Earlier governance correctly said correlated CBPs must not be independent votes.

However, the semantic composite itself still retained overlapping information.

This is now an explicit design issue.

---

## 6. OLD FOOTBALL LAB PROCESS — STATUS CHANGE

Do NOT overwrite or delete old v01/v02 artifacts.

Reason:
- they are required for historical reproducibility
- historical cross-source / warning results depend on them

Old semantic should be considered:

LEGACY_RESEARCH_SEMANTIC

It must NOT automatically be reused as the Round1657 Football LAB semantic definition.

Current provisional Round1657 semantic philosophy:

PASS
- direct creation / progression channel

CROSS
- wide chance creation channel

DRIBBLE
- individual carry / penetration channel

SHOT
- shot-generation / shot-arrival channel

GOAL
- realized finishing outcome channel

GAIN
- ball recovery channel

DEFENSE
- defensive activity / exposure context
- NOT automatic defensive strength

SAVE
- goalkeeper activity / exposure context
- NOT automatic keeper strength

OFFENSE
- aggregate reference/context
- do not add as another independent creation vote

No new arbitrary weights are approved.

No new PROCESS composite is approved yet.

---

## 7. OLD PROCESS DOWNSTREAM DEPENDENCY AUDIT

Old semantic fields are referenced by:

- football_lab_parameter_registry_raw_v01.csv
- football_lab_parameter_registry_semantic_v01.csv
- football_lab_toto1653_semantic_v01.csv
- football_lab_toto1654_semantic_v01.csv
- historical_xi_process_reproducibility_v01.csv

Scripts:
- build_cross_source_semantic_v01.py
- build_football_lab_semantic_v01.py
- build_football_lab_toto1654_semantic_v01.py
- build_football_lab_toto1654_semantic_v02.py
- build_toto_ewa_v02.py
- build_toto_match_audit_v01.py

Therefore legacy PROCESS cannot simply be edited in place.

---

## 8. OLD PROCESS DECISION PATH — EXACT IMPACT

### Cross-source semantic layer

build_cross_source_semantic_v01.py uses:

- build_up_z_diff_home
- width_carry_z_diff_home
- finishing_z_diff_home
- recovery_z_diff_home
- process_mean_z_diff_home

It converts process_mean_z_diff_home into FL direction and compares it with:

- FootyStats venue process
- FootyStats match context
- FootyStats matchup xG
- FootyStats market

This produces:
- SAME_DIRECTION
- OPPOSITE_DIRECTION
- source split classifications

This threshold/classification is research-only and not outcome calibrated.

### EWA v02

build_toto_ewa_v02.py derives Football LAB direction from:

1. process_internal_split
2. process_mean_z_diff_home

If split:
- Football LAB direction = SPLIT

Otherwise:
- positive = HOME
- negative = AWAY
- zero = NEUTRAL

Football LAB direction is included among representative evidence axes:

- FootyStats
- Football LAB process
- XI
- official market
- totoONE
- Soccerhihyo

These axes feed:
- support count
- opposition count
- SOURCE_SPLIT
- PBASE_ISOLATION_CANDIDATE
- warning target outcomes
- allocation review

Therefore the old Football LAB PROCESS can indirectly affect WARNING / ALLOCATION REVIEW routing.

However:

- statistical independence is explicitly NOT assumed
- probability_modified = 0
- probability_transport_status = P_BASE_UNCHANGED
- warning != automatic pick change
- allocation review != automatic allocation change

Impact classification:

PRODUCTION PROBABILITY:
- NO DIRECT IMPACT

WARNING:
- YES, LEGACY PROCESS CAN AFFECT WARNING

ALLOCATION REVIEW:
- YES, INDIRECTLY THROUGH WARNING TARGETS / OPPOSITION COUNTS

### Generic Match Audit

build_toto_match_audit_v01.py:

- prefers direct FootballLAB direction if available
- otherwise derives direction from process_internal_split + process_mean_z_diff_home
- marks available Football LAB direction as USED_WARNING
- never changes P_base probability

Therefore old PROCESS is not harmless metadata.
It is a legacy warning input.

---

## 9. ROUND1657 GOVERNANCE AFTER THIS AUDIT

Do not use old Football LAB PROCESS blindly for Round1657.

Do not mutate historical v01/v02 files.

Preferred future path:

OLD FL semantic
-> freeze as LEGACY_RESEARCH_SEMANTIC
-> preserve for historical reproducibility

NEW FL semantic
-> new version / new filenames
-> official-definition-aware
-> no hidden offense/pass/cross/dribble duplication
-> defense/save exposure ambiguity preserved
-> no arbitrary weighting
-> no production probability coefficient without historical OOF

Before constructing a new composite:
- inspect independence/correlation
- define each source lineage
- verify time window / denominator
- determine historical prematch availability
- test OOF where possible

---

## 10. PROJECT KNOWLEDGE MANAGEMENT RULE — NEW

Before any new analysis:

QUESTION
->
HAS THIS ALREADY BEEN TESTED?
->
YES:
  use prior conclusion unless new evidence exists
NO:
  perform new audit/test

Every important feature/block must end in an explicit status:

- USED_PBASE
- USED_WARNING
- USED_ALLOCATION_REVIEW
- USED_DATA_QUALITY
- RESEARCH_ONLY
- BLOCKED_BY_OOF
- BLOCKED_BY_MISSING
- REJECTED
- OOF_VALIDATED
- CONFIRMED
- UNRESOLVED

Do not allow completed research to disappear and later be unknowingly repeated.

---

## 11. CURRENT SAFE STATE

P_base:
- remains canonical production anchor/control

FootyStats:
- legacy official prematch xG = production lineage already validated
- deep fs_mu = mechanistic / forensic research layer
- direct fs_mu stack into P_base = rejected
- process weight remains 0 unless separately validated

Football LAB:
- old PROCESS = legacy research semantic
- old PROCESS has structural redundancy concerns
- old PROCESS may affect WARNING / ALLOCATION REVIEW
- old PROCESS does NOT mutate P_base
- new Round1657 semantic not yet built
- production coefficient remains 0

XI:
- production coefficient remains 0 unless separately validated

No canonical production files were modified during the morning semantic audits.

---

## 12. ROUND1657 NEXT START POINT

Do NOT immediately fetch/analyze everything again.

Resume in this order:

1. Preserve legacy Football LAB semantic unchanged.
2. Design new Football LAB semantic v2 under new filenames.
3. Keep primitive CBP channels visible before creating composites.
4. Test correlation / redundancy before any weighting.
5. Validate exact H2H URLs before Round1657 39-page FootyStats acquisition.
6. Build Round1657 P_base using the already validated production architecture.
7. Use research sources as warning/review layers unless promoted by historical OOF.
8. Final portfolio QA must include DRAW_COUNT_SUPPORT_MASS and common-core fixed-sign risk.

SESSION STATUS:
MORNING SEMANTIC AUDIT COMPLETE

FILES MUTATED DURING AUDITS:
False

NEXT SESSION:
Resume from Football LAB semantic v2 design / lineage ledger before Round1657 source acquisition.


---

## 2026-09-28 — Football LAB semantic v2 / Round1657 cross-league decision

### Semantic v2 confirmed

Three-league source snapshot created:

- `data/analysis/football_lab_20260924_j1j2j3_team_cbp_semantic_v2_source_v01.csv`
- J1 = 20
- J2 = 20
- J3 = 20
- required NULL = 0
- Round1657 coverage = 26/26

Semantic artifact:

- `data/analysis/football_lab_20260924_j1j2j3_team_semantic_v2_v01.csv`

Definitions:

- `SEASON_LEVEL`
  = league-internal population z-score of CBP per-match value

- `RECENT_CHANGE`
  = league-internal population z-score of:
  `(recent5 / 5) - season_per_match`

Football LAB `recent5` was established as the five-match CBP TOTAL,
not a per-match average.

Therefore:

- `recent5_avg = recent5 / 5`

Category governance:

- offense = `REFERENCE_ONLY`
  - empirically confirms approximately:
    `offense = pass + cross + dribble`
- pass = `KEEP_PRIMITIVE`
- cross = `KEEP_PRIMITIVE`
- dribble = `KEEP_PRIMITIVE`
- shot = `KEEP_PRIMITIVE`
- goal = `KEEP_PRIMITIVE_DO_NOT_COMBINE_WITH_SHOT`
- gain = `KEEP_PRIMITIVE`
- defense = `CONTEXT_ONLY_EXPOSURE`
- save = `CONTEXT_ONLY_EXPOSURE`

Multiple correlated axes MUST NOT be treated as independent votes.

No new arbitrary PROCESS composite is approved.

Production weight remains:

- `0`

Usage status:

- `RESEARCH_ONLY`

### Round1657 cross-league contract

Round1657 league relation audit:

- SAME_LEAGUE = 0/13
- CROSS_LEAGUE = 13/13
- cross-league direct z-difference cells created = 0

League-internal z-scores describe a team's position relative to its own league.

They MUST NOT be directly subtracted across J1/J2/J3 without historical
cross-league calibration.

Examples of prohibited interpretation:

- J2 +1.0z > J1 -0.2z
- arbitrary J1/J2/J3 league correction
- arbitrary league-strength offsets

### Existing knowledge audit

Prior Football LAB transport already used the caveat:

- `FOOTBALL_LAB_LEAGUE_STANDARDIZED_RESEARCH_ONLY`

Existing Football LAB production beta:

- `0`

Therefore cross-league calibration was already treated as research-only,
not production-validated.

### Historical OOF feasibility audit

Exact historical team-CBP snapshot audit found only explicit 2026-09-24
snapshot values:

- `20260924`
- `20260924_114138`
- `20260924_233151`

Pre-2026-09 historical Football LAB team-CBP snapshots found:

- NONE

Decision:

- `STATUS = BLOCKED_NO_HISTORICAL_TEAM_CBP_SNAPSHOTS_FOUND`
- `OOF_ALLOWED = False`

Current/final-season Football LAB CBP values MUST NOT be backfilled into
older matches because that would create future-information leakage.

### Final Round1657 Football LAB decision

Knowledge state:

- Football LAB official semantics = `CONFIRMED`
- semantic v2 season level = `CONFIRMED`
- semantic v2 recent change = `CONFIRMED`
- Round1657 coverage = `26/26`
- cross-league calibration = `UNRESOLVED`
- valid historical OOF = `BLOCKED_BY_MISSING`
- Round1657 directional matchup use = `BLOCKED_BY_OOF`
- production probability use = `0`
- usage = `RESEARCH_ONLY`

Operational rule:

Do NOT restart Football LAB cross-league calibration research unless
new genuinely historical pre-match team-CBP snapshots become available.

For Round1657, Football LAB may remain descriptive/contextual only.
It must not create HOME/AWAY outcome direction or mutate P_base.


---

## 2026-09-30 — Conversation handoff / post-1657 transition

### Conversation status

The current ChatGPT conversation reached its practical length limit.

Next conversation must continue from this STATE rather than restarting research.

User workflow:

- user executes terminal commands and pastes results
- after pasted terminal output:
  - explicit `判定：PASS / FAIL / PARTIAL PASS`
  - concise interpretation
  - exactly ONE next terminal command
- do not equate acquisition with semantic understanding
- check existing knowledge before starting new research
- preserve reproducibility and old artifacts
- do not mutate production probabilities using unvalidated research sources

### Pending Round1657 postmortem

Round1657 has finished.

A pending user question is:

- How many matches did the previous tentative prediction hit?

The last conversational tentative 13-symbol prediction was:

`2 / 2 / 0 / 2 / 1 / 2 / 2 / 1 / 0 / 2 / 2 / 0 / 2`

IMPORTANT:

- This was NOT a completed canonical P_base production prediction.
- It was an information-integrated provisional prediction made before the full Round1657 production pipeline was completed.
- Obtain official Round1657 results first.
- Compare all 13 matches exactly.
- Report total hits and misses.
- Do not rewrite history or call it a production-model score.

### Next-round transition

The project is now moving from Round1657 to the next Saturday toto round.

Before assuming the next round number:

1. verify the round number on toto official
2. verify the 13-match card
3. verify sales deadline
4. verify official vote-rate availability

Do not rely only on conversational assumptions about the next round.

### FootyStats latest status

Round1657 H2H URL validation stopped at:

- No5 FC大阪 vs 福岡
- HTTP 429
- bytes = 5795

Governance followed correctly:

- STOP on HTTP429
- no retry bypass
- no alternate-path evasion
- no 39-page acquisition after rate limit

Round1657 FootyStats 39 HTML snapshot therefore remains incomplete.

Current production knowledge remains:

Official/legacy FootyStats pre-match xG:

- `CONFIRMED`
- `OOF_VALIDATED`
- Stage1 `USED_PBASE`

Deep composite `fs_mu`:

- formula confirmed
- historically OOF tested
- standalone slightly better than legacy FS xG
- direct stack into P_base did NOT improve P_base
- `RESEARCH_ONLY`
- production weight = 0

Timing v05:

- validated mechanistic timing layer
- total expected goals preserved

Process modifiers:

- research only
- production weight = 0 unless new historical OOF evidence appears

For the next round:

- create/verify manifest first
- validate H2H canonical paths
- fetch HOME/H2H/AWAY only after URL QA
- stop again on HTTP429

### Football LAB semantic v2 final state

Completed artifacts:

- `data/analysis/football_lab_20260924_j1j2j3_team_cbp_semantic_v2_source_v01.csv`
- `data/analysis/football_lab_20260924_j1j2j3_team_semantic_v2_v01.csv`

Coverage:

- J1 = 20
- J2 = 20
- J3 = 20

Definitions:

`SEASON_LEVEL`
= league-internal population z-score of CBP per-match value

`RECENT_CHANGE`
= league-internal population z-score of:

`recent5 / 5 - season_per_match`

Football LAB recent5 is the TOTAL from the latest five matches,
not a per-match average.

Category governance:

- offense = `REFERENCE_ONLY`
- pass = `KEEP_PRIMITIVE`
- cross = `KEEP_PRIMITIVE`
- dribble = `KEEP_PRIMITIVE`
- shot = `KEEP_PRIMITIVE`
- goal = `KEEP_PRIMITIVE_DO_NOT_COMBINE_WITH_SHOT`
- gain = `KEEP_PRIMITIVE`
- defense = `CONTEXT_ONLY_EXPOSURE`
- save = `CONTEXT_ONLY_EXPOSURE`

Do NOT:

- recombine offense + pass
- make a simple shot + goal composite
- treat correlated CBPs as independent votes
- create arbitrary PROCESS mean
- directly modify production probability

Production weight:

- `0`

Usage:

- `RESEARCH_ONLY`

### Football LAB cross-league OOF decision

Round1657 was:

- same-league matches = 0/13
- cross-league matches = 13/13

Historical exact team-CBP snapshot audit found only explicit
2026-09-24 snapshot family:

- `20260924`
- `20260924_114138`
- `20260924_233151`

Historical pre-2026-09 pre-match team-CBP snapshots:

- NONE

Therefore:

- valid cross-league Football LAB historical OOF = unavailable
- current/final-season values must NOT be backfilled into older games
- cross-league directional conversion = `BLOCKED_BY_OOF`
- production probability use = 0

Do not restart this calibration research unless genuinely historical
pre-match Football LAB snapshots become available.

For a future round containing same-league matches:

- league-internal semantic comparison is interpretable as relative
  within-league team context
- still do not automatically turn it into calibrated outcome probability

### totoONE latest status

Reusable fetcher:

`scripts/fetch_totoone_lineups_v1.py`

Contract confirmed:

- accepts `--toto-round`
- checks totoONE current round equals requested round
- auto-discovers toto matches
- writes round-specific outputs
- supports `--dry-run`

Round1657 dry-run result:

- round = 1657
- matches = 13
- team-side rows = 26
- predicted starter rows = 0
- teams with XI = 0/26

Interpretation:

- round/card acquisition PASS
- XI publication unavailable at that snapshot
- do not treat 0 XI as fetch failure
- status = `BLOCKED_BY_NOT_PUBLISHED`

For next round:

- use the same fetcher
- dry-run first
- only save after 13 matches / 26 sides are verified

### J.League official / availability path

Existing script:

`scripts/check_toto_lineup_delta_v1.py`

Capabilities include:

- `--toto-round`
- compare latest two totoONE predicted-XI snapshots
- compare latest Fomelabo snapshots
- fetch official J.League suspension list
- generate suspension conflicts

Important caveat:

- default `--suspension-date` is an old fixed value
- next-round date must be explicitly supplied
- do not run blindly with old default

Availability governance:

- official suspension can be hard unavailable
- other reported absence / national-team selection is evidence,
  not automatically a calibrated probability
- player production coefficient remains 0 unless separately validated
- do not mutate P_base directly from uncalibrated XI warnings

### Sportsnavi latest status

Existing fetcher:

`scripts/fetch_sportsnavi_candidates_v01.py`

But it is hardcoded to Round1653:

- source:
  `data/raw/sportsnavi/discovery/1653/...`
- output root:
  `data/raw/sportsnavi/articles/1653`

Therefore:

- next-round use is currently `BLOCKED_HARDCODED_1653`
- do NOT run it unchanged
- generalize source/output round handling before reuse

Existing historical semantic processing may still be reused after acquisition.

### Soccer Hihyo / サッカー批評Web

Round1653 artifacts exist.

Use only genuinely relevant current articles for the new round.

Do not count article opinions as independent calibrated votes.

Classify as:

- contextual warning
- tactical/context evidence
- research-only unless historically validated

### toto official

For every new round, acquire/verify:

1. round number
2. 13 fixtures
3. deadline
4. latest vote rates

Vote rate is MARKET / public selection information,
not objective win probability.

Do not simply follow the most-selected symbol.

### Production architecture remains

`RAW DATA`
→ `SEMANTIC BLOCK`
→ `BLOCK SIGNAL`
→ `SOURCE SUMMARY`
→ `WARNING`
→ `ALLOCATION REVIEW`

Canonical anchor:

- `P_base`

Research layers must not silently mutate P_base.

Usage-state taxonomy:

- `USED_PBASE`
- `USED_WARNING`
- `USED_ALLOCATION_REVIEW`
- `USED_DATA_QUALITY`
- `RESEARCH_ONLY`
- `BLOCKED_BY_OOF`
- `BLOCKED_BY_MISSING`

Knowledge-state taxonomy:

- `CONFIRMED`
- `OOF_VALIDATED`
- `REJECTED`
- `RESEARCH_ONLY`
- `UNRESOLVED`

### Ticket-construction lessons retained from Round1656

Avoid common-core failure.

Do not make all tickets share the same weak fixed signs.

Draw principles:

- no forced draws
- no probability editing to fit draw count
- warning validity != allocation validity
- final `DRAW_COUNT_SUPPORT_MASS` QA required

Snapshot change log should record:

`what evidence changed`
→ `which fixed sign was released or retained`
→ `why`

### Immediate next tasks in next conversation

1. Verify official next Saturday toto round number/card/deadline.
2. Fetch official Round1657 results.
3. Score the provisional Round1657 prediction:
   `2/2/0/2/1/2/2/1/0/2/2/0/2`
4. Build/verify next-round manifest.
5. Audit current availability of:
   - toto official
   - totoONE
   - FootyStats
   - Football LAB
   - J.League official
   - JFA / national teams
   - Sportsnavi
   - サッカー批評Web
6. Obtain production inputs required for P_base.
7. Build P_base before interpreting warning layers.
8. Perform fixed-risk review.
9. Run draw-support/common-core portfolio QA.
10. Freeze final snapshot only after XI/injury/weather/market updates.

User currently says they do NOT plan to purchase based on the current prediction.
The goal is prediction-quality improvement and disciplined validation.


---

# NEXT RESEARCH ROADMAP — fixed 2026-10-03

## 0. Operating principle
- 次回以降、既に確認済みの取得方法・意味定義・検証結果を再調査しない。
- 新しいチャットは必ず TOTO_LABO_STATE.md を起点として再開する。
- RAW DATA → SEMANTIC BLOCK → BLOCK SIGNAL → SOURCE SUMMARY → WARNING → ALLOCATION REVIEW を維持する。
- P_base は production anchor。研究レイヤーから暗黙に変更しない。
- 相関する指標を独立票として重複加算しない。
- 引き分け数を合わせるために確率を編集しない。
- 新しい係数・補正・Simulation は historical OOF validation 前に production 昇格させない。

## 1. ONE-ACTION ROUND PREPARATION
次回以降はラウンド番号を指定するワンアクション取得を目標とする。

Target interface:
    python scripts/prepare_toto_round.py --round <ROUND>

Expected pipeline:
1. toto official card / vote rates
2. FootyStats URL resolution
3. FootyStats HOME / H2H / AWAY acquisition
4. parse
5. normalize
6. Football LAB acquisition / semantic normalization
7. totoONE round discovery / predicted XI
8. J.League suspension / availability inputs
9. data-quality QA
10. production input readiness report

Requirements:
- polite request delaysを維持する。
- HTTP429 / bot block / invalid responseでは停止する。回避を試みない。
- 成功済みファイルは即保存し、再実行時はvalid existing fileをskipする。
- canonical filesをresearch refreshで上書きしない。
- acquisition success と semantic understanding と production usability を区別する。
- SOURCE_UPDATE_TIME / SNAPSHOT_TIME / URL_IDENTITY を分離して記録する。
- partial failureでも取得済み成果を失わない。

## 2. COMPLETE DATA DICTIONARY
FootyStats + Football LAB + totoONE を完全データ辞書として整理する。

Semantic hierarchy:
    HTML TABLE
      -> UI BLOCK
      -> TAB
      -> METRIC
      -> POPULATION
      -> SEMANTIC ROLE

Each metric must record:
- source
- UI block
- source label
- normalized semantic name
- definition
- population
- HOME/AWAY/H2H/recent context
- sample-size warning
- high/low interpretation
- relevance to 1/0/2
- relevance to DRAW
- correlation/redundancy
- source defect / parsing caveat
- knowledge state
- production usage state

FootyStats confirmed source defect example:
- 前後半での失点 table contains duplicated source label 「前半-平均失点」.
- arithmetic indicates final row is likely second-half average conceded:
  Machida 0.50 + 1.25 = FT 1.75
  Kyoto 0.80 + 0.80 = FT 1.60
- preserve original source label.
- semantic interpretation may be HIGH-confidence inferred second-half conceded average.
- mark FOOTYSTATS_DUPLICATED_LABEL.
- do not claim FootyStats explicitly labels it as second half.

## 3. PLAYER-BASED 90-MINUTE SIMULATION RESEARCH

### Objective
totoONE predicted XIを出発点として、選手・チーム・試合環境を統合した
90分 match-path simulation を構築する。

Final research target:
    predicted XI
      -> PLAYER UTILITY
      -> TEAM STRENGTH / STYLE
      -> MATCH CONTEXT
      -> TIME-VARYING HAZARD
      -> SCORE-STATE RESPONSE
      -> substitutions / availability effects
      -> 90-minute match path
      -> score distribution
      -> H/D/A
      -> DRAW path decomposition

### Player Utility
Candidate sources:
- fantasy soccer information
- FootyStats player data
- Football LAB player data
- totoONE predicted starting XI

Do NOT simple-average sources.

Utility must be position/role aware and historically validated.

Candidate concepts:
- attacking contribution
- xG / scoring contribution
- shot generation / finishing
- chance creation
- progression / passing
- crossing / dribbling
- ball winning
- defensive suppression
- goalkeeper contribution
- minutes / expected availability
- replacement-level delta

Predicted XI uncertainty must remain explicit.

### Team layer
Candidate sources:
- FootyStats
- Football LAB
- totoONE

Candidate mechanisms:
- scoring / conceding distributions
- xG / xGA
- shots / SOT / conversion
- timing distributions
- BTTS / clean-sheet structure
- attacking routes
- hot zones
- chance creation
- scoring / conceding patterns
- team style / matchup interaction

Do not treat correlated team metrics as independent votes.

### Match Context
Explicit context layer:
- suspension / cards
- injury
- predicted availability
- consecutive-match fatigue
- rest days
- recent player minutes
- travel distance
- travel + rest interaction
- national-team call-up
- national-team minutes
- return timing / international travel
- credible team/player news
- rotation indications

News must not receive arbitrary probability adjustments.
Unvalidated context remains WARNING / RESEARCH_ONLY.

### Simulation scale
Monte Carlo count is NOT validation.

Development stages:
1. 10K — logic/debugging
2. 100K — numerical/path stability
3. historical OOF validation of inputs and coefficients
4. 1,000,000 — final production-scale simulation only after validation

A wrong model simulated 1M times remains a wrong model.

### P_base relationship
P_base remains production anchor.

Initial simulation mode:
    CONTROL / RESEARCH_ONLY

Simulation must not silently mutate P_base.

Compare:
    P_sim vs P_base

Disagreement is initially a forensic trigger, not an automatic override.

Production promotion requires historical OOF evidence.

## 4. DRAW RESEARCH — CORE TOTO LABO PROJECT

Principle:
    「引き分けを制するものはtotoを制する」

Goal:
predict DRAW through match-generation structure, not by forcing a target number of draws.

Candidate DRAW structure:
- low total-goal environment
- attack-strength closeness
- defensive-strength closeness
- xG/xGA closeness
- first-half stalemate
- time-varying scoring hazard
- BTTS / clean-sheet structure
- recent-form convergence/divergence
- score-state equalization response
- substitution effects
- player availability symmetry/asymmetry
- late equalizer paths

DRAW path decomposition should include at minimum:
- 0-0 stalemate
- 1-1 balanced
- 2-2+ open draw
- HOME leads -> AWAY equalizes
- AWAY leads -> HOME equalizes
- late equalizer
- HT draw -> FT draw

Do not count correlated DRAW metrics as independent votes.

Historical validation must test:
- P_DRAW calibration
- draw log loss / multiclass log loss
- Brier
- draw recall/precision only as diagnostics, not sole objective
- probability-bin calibration
- league/season stability
- temporal OOF stability
- score-path consistency

Final ticket QA retains:
- common-core failure check
- DRAW_COUNT_SUPPORT_MASS
- no forced draws
- no post-hoc outcome fitting

## 5. GIT / CHAT HANDOFF REQUIREMENT

Before declaring the next-round preparation complete:
1. update TOTO_LABO_STATE.md
2. update CURRENT handoff document
3. record canonical artifacts / scripts / unresolved items
4. review git status
5. stage explicit files only
6. review staged diff
7. check for secrets / credentials / inappropriate RAW or large files
8. commit
9. fetch/check remote state before push
10. push safely

Never:
- git add .
- git reset
- git clean
- blind git pull

Goal:
A new ChatGPT conversation must be able to read STATE and continue from the exact validated stopping point without repeating completed research.

## 6. NEXT-ROUND RESEARCH ORDER
1. finish complete data dictionary
2. build reliable one-action acquisition/orchestration
3. define Player Utility schema
4. acquire/normalize historical player inputs
5. construct match-context layer
6. build CONTROL 90-minute simulator
7. develop DRAW-path diagnostics
8. historical temporal OOF
9. compare P_sim with P_base
10. only then consider production promotion
11. validate 1M simulation after model validation


## FOOTBALL LAB FULL-DATA ACQUISITION — 2026 60-TEAM SLUG REGISTRY (2026-10-03)

### Status
- PASS.
- New registry:
  `data/analysis/football_lab_team_slug_map_2026_v02.csv`
- Previous v01 was preserved; no canonical overwrite.

### Population / QA
- Football LAB 2026 semantic master population:
  - J1: 20
  - J2: 20
  - J3: 20
  - TOTAL: 60
- v01 slug registry:
  - J1: 20/20 RESOLVED
  - J2: 20/20 RESOLVED
  - J3: 0/20 (not in old map population)
- J3 discovery source:
  `/summary/team_ranking/j3?year=2026`
- One safe J3 ranking probe:
  - HTTP 200
  - bytes 76498
  - block markers none
  - title confirmed 2026/27 J3 ranking
  - one ranking table
  - SHA256:
    `855d6cf4f3dc27b98376074a85c74af0a6a7d5336b108cac0f2d7b96c4328aee`
- Broad page-link scan produced 65 apparent slugs and was rejected as too broad.
- Restricting extraction to the ranking table produced exactly 20 J3 team links.
- v02 final QA:
  - rows 60
  - J1 RESOLVED 20
  - J2 RESOLVED 20
  - J3 RESOLVED 20
  - unique teams 60
  - unique slugs 60
  - duplicate slugs 0
  - non-resolved 0
  - semantic-master coverage 60/60

### J3 slugs
- FC大阪=f-os
- 北九州=kiky
- 奈良=nara
- 山口=r-ya
- 岐阜=gifu
- 愛媛=ehim
- 松本=mats
- 栃木SC=to-s
- 滋賀=rsfc
- 熊本=kuma
- 琉球=ryuk
- 相模原=sagm
- 福島=fksm
- 群馬=gnm
- 讃岐=sanu
- 金沢=kana
- 長野=naga
- 高知=kusc
- 鳥取=totr
- 鹿児島=kufc

### Acquisition architecture implication
The 60-team slug registry can now serve as the identity layer for Football LAB team-specific families such as:
`preview / formation / style / transfer / season / simulation`
subject to family-by-family URL and semantic validation.

Do NOT interpret slug resolution as data acquisition or semantic understanding.
Current non-CBP full-data families remain RESEARCH_ONLY / not yet comprehensively acquired.

### Fetch-core requirements already established
Reuse:
- CBP v02 HTTP/size/block validation
- page metadata
- SHA256 lineage
- JSON/CSV manifest concepts
- preview round/team slug resolution
- slug ambiguity rejection

New generic fetch core must add:
- immediate manifest persistence after every successful URL
- resumability/idempotence
- validated-existing skip by URL identity + raw + SHA256
- explicit 429/bot/invalid STOP
- polite delays
- no canonical overwrite
- SOURCE_UPDATE_TIME / SNAPSHOT_TIME / URL_IDENTITY separation
- semantic_key / site_parameter / display_label separation

P_base remains unchanged.
Football LAB production transport weight remains 0.
All full-data expansion work remains RESEARCH_ONLY until semantic validation and historical OOF justify promotion.


# TOTO LABO GOVERNANCE / 1658→1659→1660 RESEARCH PLAN — 2026-10-04

## 1. CANONICAL STATE / CHAT HANDOFF

Canonical project state:
`TOTO_LABO_STATE.md`

This root STATE is the single canonical research state.

`docs/TOTO_LABO_STATE.md` is LEGACY / historical reference only.
It must NOT be treated as a synchronized copy and must NOT become the new canonical state.

Create and maintain:
`docs/TOTO_LABO_HANDOFF.md`

HANDOFF purpose:
- short entry point for a new ChatGPT conversation
- point to canonical STATE
- identify current validated stopping point
- identify canonical scripts / dictionaries / architecture
- state non-negotiable governance
- state exactly what should be done next
- prevent repeated research already completed

New-chat recovery order:
`HANDOFF -> relevant canonical STATE sections -> Git-tracked specifications/scripts -> continue from validated stopping point`

Do not depend on chat memory alone.

## 2. ROUND STRATEGY

Round 1658:
- development / semantic-understanding / parser / dictionary / simulator research round
- FootyStats and totoONE pre-match assets already exist
- Football LAB round-specific join remains to be constructed from validated source assets
- known results must NOT be used to fit inputs or coefficients and then presented as predictive validation
- any 1658 result review must be explicitly post-prediction diagnostic

Round 1659:
- target blind rehearsal round
- acquire and freeze PRE-MATCH snapshot before using results
- run the complete preparation / semantic / simulation pipeline without outcome knowledge
- use as forward validation for operational readiness

Round 1660:
- important future prediction target
- use only mechanisms that have survived appropriate validation
- do not rush architecture or promote unvalidated research merely to meet Round 1660

Long-term TOTO LABO quality takes priority over single-round overfitting.

## 3. COMPLETE MULTISOURCE DATA-DICTIONARY GOAL

Primary sources:
- FootyStats
- Football LAB
- totoONE

Goal is NOT merely acquisition.

Required stages:
`ACQUIRED -> PARSED -> SEMANTICALLY UNDERSTOOD -> POPULATION DEFINED -> CORRELATION/OVERLAP AUDITED -> MATCH-GENERATION ROLE ASSIGNED -> TEMPORALLY VALIDATED -> ELIGIBLE FOR MODEL USE`

Never treat:
`data acquired == understood == predictive == production usable`

Common semantic hierarchy:
`SOURCE -> PAGE/FAMILY -> BLOCK/TAB -> METRIC -> POPULATION -> HOME/AWAY CONDITION -> TIME WINDOW -> UNIT -> MEASURED/DERIVED -> MATCH-GENERATION ROLE -> CORRELATION GROUP -> DRAW RELATION -> MISSING SEMANTICS -> OOF STATUS -> USAGE STATUS`

Match-generation map:
`scoring intensity -> chance generation -> attacking route -> shot arrival -> shot quality/xG -> conversion -> set pieces -> timing -> score state -> DRAW path`

Correlated stages must not become independent votes.

Examples requiring overlap control:
- chance creation
- shots
- xG
- goals
- conversion/success rate
- CBP/process metrics
- equivalent FootyStats / Football LAB representations

totoONE predicted XI is primarily a player/availability/context input, not an independent 1X2 vote.

## 4. PRODUCTION GOVERNANCE

`P_base` remains the production anchor.

Research information must not silently mutate P_base.

FootyStats research process transport weight remains 0 unless explicitly promoted by historical temporal OOF.

Football LAB research transport weight remains 0 unless explicitly promoted by historical temporal OOF.

XI/player/context coefficients remain research-only until separately validated.

`P_sim vs P_base` disagreement is a forensic trigger, not automatic override.

No post-hoc Round1658 fitting may be promoted as forward predictive evidence.

## 5. DRAW PRINCIPLE

Research principle:
`引き分けを制するものはtotoを制する`

This does NOT mean forcing DRAW probability upward.

DRAW must be studied through generative paths including:
- 0-0
- 1-1
- 2-2+
- home lead -> away equalizer
- away lead -> home equalizer
- late equalizer
- HT 0-0 -> FT DRAW

Existing DRAW research assets must be reviewed before creating duplicate research.

## 6. SIMULATION VALIDATION ORDER

Required progression:
`10K logic check -> 100K stability -> historical temporal OOF -> 1M precision run`

One million repetitions are NOT model validation by themselves.

Future CONTROL ROOM should display real calculations only:
- true progress
- H/D/A convergence
- checkpoint convergence
- DRAW paths
- P_base vs P_sim
- uncertainty / stability
- model/input/run identifiers

UI must never change model logic.

## 7. GIT GOVERNANCE

Git is for reproducibility and handoff, not indiscriminate storage of the entire working directory.

Priority Git content:
- canonical STATE
- HANDOFF
- architecture specifications
- data-dictionary specifications
- source/semantic schemas
- validated canonical scripts
- lightweight configuration
- provenance / lineage specifications
- reproducible QA rules

Do not blindly commit:
- large raw HTML collections
- database backups
- SQLite WAL/SHM
- zip archives
- large generated simulation output
- temporary files
- swap files
- obsolete generated copies

Never:
- `git add .`
- `git reset`
- `git clean`
- blind `git pull`

Use explicit staging and review.

Current repository fact:
- `scripts/` contains substantial current research code but was not Git-tracked at the 2026-10-04 audit.
- scripts must be classified before selective staging:
  `CANONICAL / HISTORICAL_REFERENCE / GENERATED / UNRESOLVED`

## 8. DOCUMENT GOVERNANCE

Canonical:
`TOTO_LABO_STATE.md`

Legacy:
`docs/TOTO_LABO_STATE.md`

New short handoff:
`docs/TOTO_LABO_HANDOFF.md`

Existing tracked but empty documents available for current specifications:
- `docs/totoLABO_architecture.md`
- `docs/pipeline.md`
- `docs/csv_dictionary.md`

Existing non-empty research documents must not be blindly overwritten:
- `docs/FEATURE_CATALOG.md`
- `docs/draw_research.md`

## 9. NEXT RESEARCH SEQUENCE

1. establish Git-safe STATE/HANDOFF governance
2. classify/select canonical existing scripts
3. construct common multisource data-dictionary schema
4. complete FootyStats dictionary
5. complete Football LAB acquisition + dictionary
6. complete totoONE dictionary
7. construct semantic overlap/correlation map across all three sources
8. map validated information into match-generation process
9. define Player Utility and context schemas
10. prepare Round1659 PRE-MATCH blind snapshot
11. 10K / 100K simulation validation
12. historical temporal OOF
13. blind Round1659 evaluation when results become available
14. prepare Round1660 using only validated mechanisms
15. 1M CONTROL ROOM after model validation

## 10. CURRENT STOPPING POINT

Governance audit completed.

Confirmed:
- root `TOTO_LABO_STATE.md` is the canonical and much more complete STATE
- `docs/TOTO_LABO_STATE.md` is a different older document
- `docs/TOTO_LABO_HANDOFF.md` does not yet exist
- `docs/totoLABO_architecture.md`, `docs/pipeline.md`, and `docs/csv_dictionary.md` are tracked but currently empty
- substantial current scripts exist outside Git tracking
- no bulk Git staging is permitted

NEXT ACTION:
Create the short HANDOFF specification from canonical STATE and validated current architecture, then selectively establish the first Git governance baseline.



# TOTO LABO PROJECT-MEMORY INDEX — 2026-10-04

## Purpose

Prevent future ChatGPT conversations from repeatedly rediscovering where files are, what research was already performed, and which historical assets exist.

The project memory is now layered:

1. `docs/TOTO_LABO_HANDOFF.md`
   - short new-chat bootstrap

2. `TOTO_LABO_STATE.md`
   - canonical detailed research history / validated conclusions / governance

3. `docs/TOTO_LABO_ASSET_INVENTORY.csv`
   - full local asset-location index

4. `docs/TOTO_LABO_RESEARCH_INDEX_V2.csv`
   - section-body-aware index of canonical STATE research themes

5. `docs/TOTO_LABO_STATE_ASSET_LINKS.csv`
   - links from STATE references to current filesystem assets

6. Git
   - reproducible code/specification/governance layer

## 2026-10-04 inventory facts

Full project audit:
- 9,674 files
- approximately 6.16 GB local project assets

Asset inventory source-family guesses:
- OTHER 5,231
- FOOTYSTATS 2,494
- JLEAGUE 1,085
- TOTOONE 459
- FOOTBALL_LAB 219
- DRAW 128
- FANSAKA 58

Asset layers:
- OTHER 5,355
- RAW 2,452
- ANALYSIS 626
- CODE 494 by first inventory classification
- EVALUATION 293
- PLAYER 204
- PARSED 106
- MODEL 55
- FEATURE 49
- DOC 22
- SIMULATION 18

Recursive Python lineage audit:
- 517 Python files under scripts/src
- 456 normalized family keys
- 44 multi-version families
- 412 singleton families

The recursive Python count supersedes the earlier coarse CODE count when discussing Python-code inventory.

## Research-history index facts

Canonical STATE:
- 16,890 lines at index-generation time
- 713 headings

Heading-only V1 classification:
- 454 OTHER headings

Section-body-aware V2 classification:
- 636 classified headings
- 77 OTHER headings

V2 is the preferred research-theme index.

Theme assignment is discovery/indexing only.
It does NOT automatically imply:
- CANONICAL
- OOF_VALIDATED
- production eligibility

## STATE-to-asset lineage facts

STATE path extraction:
- 341 references
- 268 unique paths
- 333 references currently resolve
- 8 references currently missing

Missing does NOT automatically mean lost research.
A missing reference may be:
- historical
- renamed
- generated
- proposed architecture
- never implemented

Known example:
`scripts/prepare_toto_round.py`
is a future one-action orchestration target, not an existing canonical script at this stopping point.

## New-chat anti-rediscovery rule

A new conversation must NOT begin by broadly searching the repository for previously known work.

Recovery order:

`HANDOFF`
-> `RESEARCH_INDEX_V2`
-> relevant canonical `STATE` sections
-> `STATE_ASSET_LINKS`
-> `ASSET_INVENTORY`
-> exact canonical/relevant artifact

Only perform new filesystem discovery when these indexes do not answer the question.

Do not infer that the highest version number is automatically canonical.

Historical failures, rejected models, blocked research, and superseded versions are project knowledge and must be preserved to prevent duplicate research.

## Current limitation

The project-memory indexes establish discovery and lineage infrastructure, but not every one of the 9,674 assets has been semantically classified.

`UNRESOLVED` therefore means:
classification has not yet been established,
not that the asset is useless.

Future classification should occur when a research family is actually being used, rather than manually reviewing thousands of files without a research purpose.



## PROJECT MEMORY GIT BASELINE — 2026-10-04

Local baseline commit established:

`d4b71956b68c9b6fc7d35cfbc8796cf40fc6ff2e`

Commit subject:

`Establish TOTO LABO project memory baseline`

This commit is the first Git baseline containing:
- canonical `TOTO_LABO_STATE.md`
- short `docs/TOTO_LABO_HANDOFF.md`
- full local asset inventory index
- section-aware research index
- STATE-to-asset link index
- first selectively chosen canonical research/pipeline scripts

Important:
- this commit does NOT contain all raw/local TOTO LABO data
- local raw/generated/historical assets remain discoverable through the project-memory indexes
- the remaining dirty working tree must not be interpreted as disposable
- do not use `git reset`, `git clean`, or `git add .`
- future chats should use this hash as the first project-memory Git reference point

# DAILY FINISH / NEXT-CHAT START POINT — 2026-10-04

## 1. PROJECT MEMORY INFRASTRUCTURE — COMPLETED

TOTO LABO project-memory / handoff infrastructure is now complete.

Final QA:

- Git baseline:
  `d4b71956b68c9b6fc7d35cfbc8796cf40fc6ff2e`
- baseline-lineage commit / current synchronized HEAD:
  `edc4b7e5bcbbcad718f224fbaa16e0d5604f08c0`
- `HEAD == origin/main` confirmed.

Required project-memory files all PASS:

- `TOTO_LABO_STATE.md`
- `docs/TOTO_LABO_HANDOFF.md`
- `docs/TOTO_LABO_ASSET_INVENTORY.csv`
- `docs/TOTO_LABO_RESEARCH_INDEX_V2.csv`
- `docs/TOTO_LABO_STATE_ASSET_LINKS.csv`

Project-memory scale established:

- local project assets: 9,674 files
- local project size: approximately 6.16 GB
- recursive Python inventory under scripts/src: 517 files
- normalized Python family keys: 456
- multi-version Python families: 44
- canonical STATE research headings indexed: 713
- section-body-aware classified headings: 636
- STATE asset references: 341
- unique referenced paths: 268
- currently resolving references: 333

## 2. NEW-CHAT RECOVERY CONTRACT

Future conversations must recover TOTO LABO in this order:

`docs/TOTO_LABO_HANDOFF.md`
-> `docs/TOTO_LABO_RESEARCH_INDEX_V2.csv`
-> relevant sections of canonical `TOTO_LABO_STATE.md`
-> `docs/TOTO_LABO_STATE_ASSET_LINKS.csv`
-> `docs/TOTO_LABO_ASSET_INVENTORY.csv`
-> exact relevant artifact

Do NOT begin a new conversation with broad repository grep/find merely to rediscover known work.

The purpose of the indexes is to USE previous work, not repeatedly rediscover it.

`TOTO_LABO_STATE.md` remains the canonical detailed research record.
`docs/TOTO_LABO_HANDOFF.md` is the short bootstrap, not a replacement for STATE.

Do not infer:
- latest version number = canonical
- existing file = validated
- acquired data = semantically understood
- missing STATE path = lost research
- UNRESOLVED = useless

Historical failures, rejected models, BLOCKED_BY_OOF research, and superseded versions remain reusable project knowledge.

## 3. PROJECT-MEMORY PHASE — STOP HERE

Do not continue asset cataloguing for its own sake.

The current infrastructure is sufficient to return to core TOTO LABO research.

The remaining 9,674 assets do NOT need manual semantic classification before research resumes.

Classify unresolved assets when their research family becomes relevant.

Do not:
- `git add .`
- `git reset`
- `git clean`
- blindly overwrite canonical files
- blindly commit large raw/database/model assets

The intentionally dirty historical/local working tree must be preserved.

## 4. NEXT RESEARCH START POINT — FIXED

The next conversation must NOT restart repository discovery.

The next core research task is:

`FootyStats × Football LAB × totoONE COMPLETE DATA DICTIONARY / SEMANTIC INTEGRATION`

Required research sequence:

1. recover existing validated FootyStats research from Project Memory
2. recover existing Football LAB research/assets from Project Memory
3. recover existing totoONE research/assets from Project Memory
4. complete source-specific data dictionaries
5. map semantically equivalent and source-unique metrics
6. identify population/definition differences
7. identify correlation / double-counting risk
8. map metrics into common match-generation process
9. preserve `P_base` as production anchor
10. keep unvalidated additions RESEARCH_ONLY
11. proceed to Player Utility / Match Context historical validation
12. integrate existing DRAW research and DRAW-path decomposition
13. historical OOF validation
14. 10K simulation logic check
15. 100K stability check
16. only after validation, 1M simulation

Common match-generation direction remains:

`得点強度`
-> `チャンス生成`
-> `攻撃経路`
-> `シュート`
-> `セットプレー`
-> `時間帯`
-> `得点 / 失点`
-> `score state`
-> `DRAW path`

## 5. NON-NEGOTIABLE MODEL GOVERNANCE

`P_base` remains the production anchor.

Research information must not silently mutate `P_base`.

Do not count correlated metrics as independent votes.

totoONE predicted XI is not an independent 1X2 vote.

FootyStats / Football LAB / totoONE information should be placed into the match-generation process rather than treated as three independent prediction votes.

DRAW remains a major research priority:

`引き分けを制するものはtotoを制する`

but draws must never be forced without probability support.

Simulation repetition count is not validation.

Required progression remains:

`10K logic`
-> `100K stability`
-> `historical OOF`
-> `1M precision`

Known-result rounds must not be used for post-hoc result fitting.

## 6. ROUND STRATEGY

Round1658:
- development / semantic / parser / dictionary / frozen-backtest research asset
- known result may be revealed only after frozen prediction for diagnostics
- no post-hoc coefficient fitting

Round1659:
- inventory currently had no round-specific files at the latest audit
- blind rehearsal only if genuinely acquired pre-kickoff
- otherwise any backfill must not be called blind pre-match validation

Round1660:
- important future operational target
- do not rush unvalidated research merely to target the round
- long-term TOTO LABO architecture and historical validation take priority

## 7. FUTURE ROUND AUTOMATION TARGET

Long-term one-action target remains:

`python scripts/prepare_toto_round.py --round <ROUND>`

This script is NOT yet an existing canonical implementation.

Target flow:

`toto official`
-> `J.League safe refresh`
-> `FootyStats URL resolution`
-> `FootyStats 39-page safe acquisition`
-> `FootyStats parse / normalize / semantic dictionary`
-> `Football LAB automatic acquisition`
-> `Football LAB full semantic normalization`
-> `FootyStats × Football LAB semantic comparison`
-> `totoONE predicted XI`
-> `availability / suspension / context`
-> `QA`
-> `production readiness`

Acquisition must remain polite, resumable, idempotent, and stop safely on 429 / bot / invalid responses.

## 8. NEXT CHAT — ABSOLUTE FIRST ACTION

Use the Project Memory indexes to retrieve the already-existing research and assets for:

`FootyStats`
`Football LAB`
`totoONE`

Then resume the complete multisource data-dictionary / semantic-integration work.

Do NOT restart from:
- generic repository inventory
- broad find/grep
- new speculative features
- arbitrary probability adjustment
- 1M simulation

The next phase is to turn the large amount of data already acquired into correctly understood, non-duplicated, historically testable information.

# END OF DAILY FINISH — 2026-10-04

# DAILY FINISH — 2026-10-05 — MULTISOURCE DICTIONARY / FL CBP CONTRACT

## Completed
- Common multisource dictionary semantic recovery progressed:
  - v01 draft: 449 rows
  - v02 semantic recovery: FL REVIEW 157 -> 0
  - v03: `data/analysis/toto_labo_multisource_dictionary_v03_fl_cbp_contract.csv`
- Football LAB CBP contract audited for 9 families:
  offense / pass / cross / dribble / shot / goal / gain / defense / save.
- Current J1/J2/J3 60-team semantic-v2 source identity verified:
  60 teams x 9 families x 4 representations = 2160/2160 exact matches.
  MISMATCH=0, GLOBAL_MAXERR=0.
- Source-measured CBP representations confirmed:
  rank / total / per_match / recent5.
- Derived identities numerically confirmed:
  recent5_avg = recent5 / 5
  recent_delta = recent5_avg - per_match
  diff_home_* = HOME - AWAY
  rank_adv_home = AWAY_RANK - HOME_RANK
- Dictionary v03 FL CBP rows:
  108/108 population resolved to supported team-within-league-CBP-category scope.
  108/108 condition resolved as fixture-side assignment / derived comparison.
  108/108 time-window contract recorded conservatively.
  108/108 measurement_type resolved.
- Important semantic guardrail:
  HOME/AWAY in the match feature layer means fixture-side assignment of team-level Football LAB CBP;
  it is NOT evidence of venue-specific Football LAB CBP.

## Intentionally unresolved
- CBP unit: 108/108 UNRESOLVED.
- Exact denominator/source definition of per_match remains unresolved.
- Exact source-window details not directly evidenced remain conservatively labeled.
- DRAW_RELATION: 108/108 UNRESOLVED.
- Do not infer DRAW effect from metric names.
- DRAW relevance must be tested later with historical OOF / draw-path analysis.

## Production governance
- production_weight = 0 for all FL CBP dictionary rows.
- No production promotion.
- P_base UNTOUCHED.
- Correlated CBP representations are not independent votes.
- offense remains reference-only where established.
- goal must not be recombined blindly with shot.
- defense/save remain context-only where established.

## Next research start
Continue from:
`data/analysis/toto_labo_multisource_dictionary_v03_fl_cbp_contract.csv`

Do NOT repeat:
- FL CBP 2160-value source identity audit
- recent5_avg/recent_delta identity audit
- diff_home/rank_adv orientation audit
- generic repository discovery for these already-resolved questions

Next objective:
Continue multisource semantic dictionary completion using existing Project Memory/indexes.
Resolve only evidence-supported remaining semantics.
Do not infer unit/DRAW relation.
After dictionary recovery QA, proceed toward FootyStats x Football LAB x totoONE semantic integration and historical OOF.
P_base remains the production anchor.

# DAILY FINISH — 2026-10-05 — MULTISOURCE DICTIONARY v04→v06 / FL TEAM_CONTEXT10 CONTRACT

## 1. Purpose

Continue multisource semantic recovery without modifying production probabilities.

Research governance remained fixed:

- `P_base` is the production anchor.
- Research-only source semantics do not directly modify `P_base`.
- Correlated metrics are not independent votes.
- DRAW relation is not inferred from intuition; historical OOF is required.
- Football LAB CBP108 already resolved/frozen was not reopened.
- `attack_col` / `field_strength` remain blocked because origin is unresolved.

---

## 2. FootyStats semantic contract — v04 / v05

### v04

Artifact:

`data/analysis/toto_labo_multisource_dictionary_v04_fs_semantic_contract.csv`

Resolved five FootyStats semantic/control fields:

- `ctx_finishing_side`
- `explicit_venue_detail_pair`
- `venue_finishing_side`
- `finishing_semantic_split`
- `semantic_flags`

These are derived semantic/QA controls and must not be treated as independent predictive votes.

### v05

Artifact:

`data/analysis/toto_labo_multisource_dictionary_v05_fs60_contract.csv`

FootyStats remaining 60 dictionary rows had population/unit contracts resolved.

Important semantic separation:

- venue xG/xGA/form = fixture team venue context.
- context shots/SOT/conversion/SPG/possession = match/H2H comparison context and must NOT be mislabeled venue-specific.
- explicit venue detail = separate explicit venue-detail source.
- semantic split fields = QA/control.
- matchup xG = derived diagnostic proxy from the same xG lineage.
- market probabilities = one correlated market lineage.
- xG crosscheck = QA/control.

FootyStats DRAW relation remains deferred to historical OOF.

Production weight remains zero for research-only dictionary recovery.

`P_base` remained untouched.

FootyStats population/unit semantic recovery is FROZEN unless new contradictory evidence appears.

---

## 3. Football LAB REVIEW157 role-aware triage

Football LAB REVIEW rows were partitioned as:

- KNOWN_CBP_OR_DERIVED_LINEAGE = 108
- META_IDENTITY_QA = 37
- TEAM_CONTEXT_ACTIONABLE = 10
- BLOCKED = 2

Blocked fields:

- `attack_col`
- `field_strength`

These remain `ORIGIN_UNRESOLVED`.

META/IDENTITY/QA fields are not predictive votes.

CBP108 remains frozen.

---

## 4. TEAM_CONTEXT10 fields

The actionable Football LAB contextual fields are:

- `fl_home_league_rank`
- `fl_away_league_rank`
- `fl_home_league_points`
- `fl_away_league_points`
- `fl_home_goals_for`
- `fl_away_goals_for`
- `fl_home_goals_against`
- `fl_away_goals_against`
- `fl_league_points_diff_home`
- `fl_league_rank_adv_home`

All ten belong to one correlated contextual lineage:

`FL_TEAM_LEAGUE_RESULT_CONTEXT`

They must NOT be counted as ten independent votes.

---

## 5. TEAM_CONTEXT10 two-snapshot arithmetic contract

Audited artifacts:

- `data/analysis/football_lab_toto1653_feature_blocks_v01.csv`
- `data/analysis/football_lab_toto1654_feature_blocks_v01.csv`

Both have shape 13x128.

Across both snapshots:

`fl_league_points_diff_home = fl_home_league_points - fl_away_league_points`

and:

`fl_league_rank_adv_home = fl_away_league_rank - fl_home_league_rank`

were reproduced exactly.

Positive `fl_league_rank_adv_home` therefore means the HOME fixture-side team has the better/lower league rank.

Arithmetic identities were proven over 26 fixture rows.

---

## 6. TEAM_CONTEXT10 builder lineage

Exact builders identified:

- `scripts/build_football_lab_toto1653_features_v01.py`
- `scripts/build_football_lab_toto1654_features_v01.py`

Both implementations use the same semantic contract.

Fixture identity:

`home_name = fixture home_team`

`away_name = fixture away_team`

then each is resolved to a Football LAB team record.

Base fields are copied from:

- `league_rank`
- `league_points`
- `goals_for`
- `goals_against`

The immediate normalized upstream asset is:

`data/analysis/football_lab_team_cbp_2026_normalized_v01.csv`

HOME/AWAY here means fixture-side team assignment.

It does NOT by itself mean venue-specific measurement.

---

## 7. Normalized → raw Football LAB lineage

Normalizer:

`scripts/normalize_football_lab_team_cbp_v01.py`

Raw root:

`data/raw/football_lab/cbp/2026`

Raw files are nested by league/category, not stored directly under the root.

Contract:

`ROOT / league / f"{category}.html"`

The parser explicitly reads:

`table#ls_teamCBP`

The league-result columns are taken from source cells:

- `vals[6] -> league_rank`
- `vals[7] -> league_points`
- `vals[8] -> goals_for`
- `vals[9] -> goals_against`

The normalizer cross-checks the duplicated league-result columns across CBP categories.

Therefore the established lineage is:

`Football LAB raw CBP HTML`
→ `table#ls_teamCBP`
→ source cells 6:10
→ normalized BASE4
→ fixture-side HOME/AWAY team join
→ TEAM_CONTEXT8
→ derived points/rank fields

---

## 8. Raw source header contract

Nested raw HTML audit found 30 HTML files.

For the applicable `table#ls_teamCBP` pages, the source table directly labels source columns 6–9 as:

- `順位`
- `勝点`
- `得点`
- `失点`

This directly resolves the metric meaning of the BASE4 fields.

The page also identifies the season as:

`2026/27`

Source update information is present in the raw HTML.

However, the available evidence does NOT prove the exact cumulative/current-through-round time-window definition.

Therefore do NOT infer an exact cumulative window merely from plausible values or field names.

Time-window contract remains:

`2026_27_SOURCE_SNAPSHOT_EXACT_CUMULATIVE_WINDOW_UNRESOLVED`

Also note:

`最近５試合` belongs to the separate CBP recent-five column and must not be applied to league rank/points/GF/GA.

---

## 9. Multisource dictionary v06

Artifact:

`data/analysis/toto_labo_multisource_dictionary_v06_fl_team_context_contract.csv`

QA:

- ROWS = 449
- TARGETS = 10
- CHANGED ROWS = 10
- only TEAM_CONTEXT10 changed = TRUE
- exact window remains unresolved = TRUE
- DRAW remains historical-OOF-required = TRUE
- all TEAM_CONTEXT10 rows remain `RESEARCH_ONLY`
- all production weights remain 0

BASE8 contracts now distinguish:

- fixture HOME team
- fixture AWAY team
- source-measured rank/points/GF/GA

Derived2 contracts distinguish:

- `HOME_MINUS_AWAY_DERIVED` for points difference
- `AWAY_RANK_MINUS_HOME_RANK_DERIVED` for home rank advantage

All ten remain in:

`FL_TEAM_LEAGUE_RESULT_CONTEXT`

Semantic status:

`SOURCE_CONTRACT_RESOLVED_WINDOW_PARTIAL`

DRAW relation:

`UNRESOLVED_HISTORICAL_OOF_REQUIRED`

No production promotion occurred.

`P_base` remained untouched.

---

## 10. Frozen / unresolved state after v06

FROZEN:

- FootyStats FS60 population/unit semantic contract.
- Football LAB CBP108 semantic contract.
- TEAM_CONTEXT10 metric meaning and immediate lineage.
- TEAM_CONTEXT10 arithmetic direction.

NOT predictive votes:

- Football LAB META/IDENTITY/QA37.
- semantic QA/control fields.
- derived fields from the same underlying lineage.

BLOCKED:

- `attack_col`
- `field_strength`

UNRESOLVED:

- exact Football LAB cumulative/current-through-round window semantics.
- DRAW relationship for TEAM_CONTEXT10.
- predictive incremental value of TEAM_CONTEXT10.

Those questions require historical/pseudo-OOF evidence and must not be answered by semantic interpretation alone.

---

## 11. Next research boundary

Do NOT reopen FS60, FL CBP108, or TEAM_CONTEXT10 semantic meaning without contradictory source evidence.

Next work should proceed from the v06 dictionary and Project Memory.

The next major scientific question is not “what do these fields mean?” but whether the resolved information has incremental predictive value under leakage-safe historical/pseudo-OOF validation, especially for DRAW paths.

Before continuing research, finish Git/handoff stabilization so a new chat can resume without broad rediscovery.

---

## 2026-10-05 PLAYER/XI RESEARCH LINEAGE RECOVERY — CANONICAL CHECKPOINT

### Purpose
Past PLAYER/XI research lineage was reconstructed before any new implementation so that future chats do not restart already-completed research.

### Recovered lineage

#### Round1653 — multisource PLAYER/LINEUP architecture
Designed target Player Utility using:
- Fantasy/Fansaka information
- J.League official player information
- FootyStats player data
- Football LAB player data
- totoONE predicted XI / formation

Principles:
- do not simple-average sources
- preserve position / role semantics
- missing != zero
- correlated metrics are not independent votes
- predicted XI uncertainty remains explicit
- production promotion requires historical OOF

#### Round1654 — implementation foundation
Implemented:
- FootyStats 2026 player-strength prototype
- J.League canonical player identity / crosswalk
- totoONE/Fomelabo XI identity staging
- Football LAB TEAM CBP join / feature / semantic research

Important clarification:
- football_lab_toto1654_xi_strength_players_v01/v02/v03 filenames do NOT prove Football LAB PLAYER CBP numerical integration.
- inspected 1654 Football LAB feature/semantic scripts operate on TEAM CBP.
- P_base was not modified.

#### Round1656 — operational XI prototype and Football LAB matchup layer
Football LAB:
- J2/J3 TEAM CBP extraction and league-internal semantic standardization completed.
- TEAM matchup matrix completed for 13 matches / 26 sides.
- player TOP30 ranking asset exists:
  data/analysis/football_lab_2026_27_1656_player_cbp_top30_long_v01.csv
- this player asset is LEAGUE_TOP30_RANKING_ONLY, not a complete player population.
- absence from TOP30 must NOT be interpreted as zero / weak / below-average.
- Football LAB process/matchup production coefficients remained 0 pending historical OOF.
- defense/save/gain may reflect workload/exposure and are not direct defensive-strength votes.
- cross-league contrasts remained RESEARCH_UNCALIBRATED.

XI engine:
- predicted/actual XI player-strength pipeline became operational.
- actual XI = 26 teams x 11 = 286 starters.
- empirical player-strength coverage = 277/286 = 96.9%.
- 9 missing players received explicit baseline imputation.
- player/team/match strength artifacts were generated.
- inspected implementation shows numerical strength core is FootyStats player axes.
- J.League contributes canonical identity/context.
- XI/formation sources contribute lineup/identity context.
- no evidence was found that Fantasy + Football LAB PLAYER CBP + J.League performance were quantitatively fused into the operational six-axis XI strength engine.

### Canonical stopping point
FS-based XI strength engine = IMPLEMENTED / REUSABLE PROTOTYPE.

Football LAB TEAM process/matchup layer = IMPLEMENTED / RESEARCH-ONLY.

Football LAB PLAYER TOP30 = ACQUIRED / LIMITED-COVERAGE RESEARCH SOURCE.

Full multisource Player Utility
(Fantasy/Fansaka + FootyStats Player + Football LAB Player + J.League official performance + role/formation + availability/load)
= DESIGNED / PARTIALLY IMPLEMENTED / NOT YET PROVEN AS A COMPLETE NUMERICAL ENGINE.

PLAYER -> lambda / H-D-A production transport
= BLOCKED_BY_HISTORICAL_OOF.

Production governance:
- P_base remains canonical anchor.
- PLAYER/XI production coefficient remains 0 until historical OOF validation.
- Football LAB research coefficients remain 0 until historical OOF validation.
- do not result-fit Round1658.
- do not read Round1658 results before frozen source-isolated predictions are saved.

### Canonical continuation
Do NOT redesign PLAYER/XI from scratch.

Continue from the existing Round1656 FS-XI operational engine:
1. minimally transport it to Round1658 predicted XI;
2. QA 13 matches / 26 teams / 286 starters;
3. preserve identity confidence, position mismatch, minutes, reliability and imputation flags;
4. freeze XI/player-only Round1658 output without result access;
5. compare source-isolated FS-only / FL-team-only / XI-player-only views;
6. only then study combined mechanisms;
7. use historical OOF/pseudo-OOF before any production coefficient;
8. simulation progression remains 10K -> 100K -> historical OOF -> 1M.
