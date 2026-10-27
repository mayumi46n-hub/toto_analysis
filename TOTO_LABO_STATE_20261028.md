# TOTO_LABO_STATE — 2026-10-28 JST / GOAL3 第1666回

## 最優先の目的（6月から不変）
Jリーグ公式・Football LAB・ファンサカ・FootyStatsの詳細な選手／チーム指標を、本人確認・出典・取得時点・欠損管理付きで統合。予想先発、欠場・出場停止、戦術、GK、移動、休養、観客、順位等を同条件で扱い、リークを防いで検証。その後に真の90分イベント駆動シミュレーションを各試合100万回実行。ポアソン抽選をイベント駆動と偽らない。GOAL3の3試合からtoto13試合へ拡張可能にする。

## 第1666回（2026-10-28 19:00 JST）
1. 水戸（H）–C大阪（A）
2. 横浜FM（H）–広島（A）
3. 名古屋（H）–浦和（A）
予想先発：6チーム×11人＝66人。totoONEのPDFから抽出済み。64人は既存ファンサカ/Jリーグ公式系データと照合。未照合2人はファンサカ選手ページで本人ID確認：C大阪 ハビ・エルナンデス J48524、浦和 瀬古樹 J47CM1。2人の能力値は未取得・未接続。ポジション不一致8人は要確認で、誤りと断定しない。

## 確定した暫定戦力（player_power_fp_jlの単純平均、欠損は平均から除外）
| チーム | 先発 | 能力値あり | 平均 |
|---|---:|---:|---:|
| 水戸 | 11 | 11 | 4.593 |
| C大阪 | 11 | 10 | 5.245 |
| 横浜FM | 11 | 11 | 4.909 |
| 広島 | 11 | 11 | 5.600 |
| 名古屋 | 11 | 11 | 5.121 |
| 浦和 | 11 | 10 | 5.152 |
ホーム－アウェイ差：水戸－C大阪 -0.652、横浜FM－広島 -0.691、名古屋－浦和 -0.031。異なる分母での暫定比較。得点期待値や勝率ではない。

## Macプロジェクトと成果物
ルート：~/Desktop/toto_analysis（.venv）
- data/config/toto_rounds/1666_card_official.csv
- data/config/toto_rounds/1666_footystats_3html_manifest.csv
- data/raw/footystats/round_html/1666/1666_{01,02,03}_{home,h2h,away}.html（計9本）
- data/raw/football_lab/toto1666_previews_20261026_233201_v01/1666_{01_mito,02_y-fm,03_nago}_preview.html（計3本）
- data/players/fansaka_j1_player_power_v3_jleague.csv（J1の既存戦力起点）
- data/analysis/goal3_1666_xi_identity_audit.csv（66人）
- data/analysis/goal3_1666_xi_identity_v02.csv（66人、未照合2人にfansaka_id_verified追加）
- data/analysis/goal3_1666_strength_coverage_v01.csv（一次監査）
- data/analysis/goal3_1666_strength_join_v02.csv（再結合監査）
- data/players/toto1656_player_strength_master_v03.csv は566行、J2/J3の26チーム対象。第1666回J1の結合に使わない。
- audit_goal3_1666_xi.py、audit_goal3_1666_strength.py、join_goal3_1666_strength_v02.py はMacで実行済み（プロジェクトルートに配置）。

## 実行結果・重要な落とし穴
- 初回照合：64/66。未照合はハビ・エルナンデス、瀬古樹。
- 一次監査：fansaka ID-verified=64, numeric>0=64、strength=0、footystats=0。
- 再結合：fansaka jleague_id=64、strength=0、footystats=0。0件は『能力値が存在しない』の意味ではない。
- 第1656回戦力マスターはJ2/J3対象であり、0件の主因は対象リーグ違い。これをJ1向けに再結合し続けない。
- FootyStats側のIDクロスウォークは未確定。名前だけの曖昧結合を採用しない。
- Football LAB選手別能力は未接続。取得時点を必ず検査し、キックオフ後情報を混ぜない。
- totoONE取得スクリプトは13試合toto前提でGOAL3 3試合に非対応。Fomelaboの --toto-round は保存ファイル名ラベルであり、過去スナップショットを取得する機能ではない。
- goal3_1666_xi_identity_v02.csv の2件の fansaka_source_url が Markdownリンク表記のままの可能性あり。機械処理時に正規化すればよく、これだけのためにユーザーへ繰り返し修正を頼まない。
- ターミナルに長いPythonヒアドキュメントを貼り付けると崩れた。今後は構文チェック済み .py を配布し、Macでは短い実行コマンドだけ。

## 次回、絶対に最初にやること
既存J1マスター・Football LAB・FootyStatsの**実データの列／キー／所属／時点**を確認し、66人の選手別データをID優先で接続。各能力指標の値・単位・出典・欠損・マッチ方法を一つの表に出す。新規取得は必要性が判明したものだけ。推測の修正コードを何度も実行させない。選手能力がそろう前に得点確率や買い目を捏造しない。

## Daily Finish／本部報告
完了：66人照合、64人の暫定能力値、2人のファンサカID、3試合の暫定比較。
AI学習：リーグ違いのマスター誤用、実データを見ない結合修正、長い貼り付け指示を繰り返した。ユーザーのコンセプトは不変。
現在地点：本人照合と暫定比較まで。4ソース統合と真のイベント駆動モデルは未完成。
次回必須：J1の4ソースを本人・所属・時点で検証し、66人の詳細能力と欠損を統合。
保留：2人の能力値、ポジション8件、欠場／戦術／疲労等、モデル検証、シミュレーション、買い目。
