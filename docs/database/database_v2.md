# totoLABO Database v2

## Version
v2.0

---

# Philosophy

外部サイトが増えてもDB構造は変更しない。

追加するのはデータだけ。

---

# Master

## team_master

チーム基本情報

- team_id
- short_name
- full_name
- english_name
- category
- league
- stadium
- prefecture

---

## player_master

選手基本情報

- player_id
- team_id
- name
- english_name
- birth
- height
- weight
- foot
- position

---

## stadium_master

スタジアム情報

---

## source_master

データソース一覧

例

- toto
- jleague
- footystats
- fansaka
- transfermarkt

---

# Mapping

## team_source_map

外部サイトとのチーム対応表

例

team_id=31

↓

toto
福岡

↓

JLeague
アビスパ福岡

↓

FootyStats
Avispa Fukuoka

---

## player_source_map

外部サイトとの選手対応表

---

# Match

## team_match_stats

1試合ごとのチームスタッツ

予定項目

- possession
- shots
- shots_on_target
- xG
- corners
- fouls
- yellow
- red

---

## player_match_stats

1試合ごとの選手スタッツ

予定項目

- minutes
- goal
- assist
- shot
- key_pass
- rating

---

# Prediction

## feature_store

AI特徴量

---

## prediction_result

予測保存

---

# Future

追加予定

- Weather
- Referee
- Odds
- Betting Rate
- Fantasy
- Transfer Value
- Injury
- Formation
- Starting XI

