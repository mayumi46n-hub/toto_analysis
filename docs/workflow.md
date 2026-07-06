# Project AKAMURASAKI LABO 開発フロー

## 新しいtoto回の登録

1. トトクラブHTML保存
2. J1公式HTML保存
3. J2公式HTML保存
4. python3 src/import_jleague_matches.py YYYYMMDD
5. python3 src/parse_toto_club.py 回数
6. 13/13確認
7. git commit

---

## HTML命名規則

data/jleague_YYYYMMDD_j1.html
data/jleague_YYYYMMDD_j2.html

---

## DB確認

SELECT round_no, COUNT(*)
FROM toto_matches
GROUP BY round_no;

---

## alias追加

INSERT OR IGNORE INTO team_alias ...