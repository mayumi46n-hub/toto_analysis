import sqlite3

DB_PATH = "data/toto.db"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

print("=" * 40)
print("      TotoLab データ分析")
print("=" * 40)

# 全試合数
cur.execute("""
SELECT COUNT(*)
FROM toto_matches
""")
total = cur.fetchone()[0]

print(f"総試合数：{total}")

print()

# ホーム勝率・引き分け率・アウェイ勝率
cur.execute("""
SELECT
ROUND(SUM(CASE WHEN result='1' THEN 1 ELSE 0 END)*100.0/COUNT(*),1),
ROUND(SUM(CASE WHEN result='0' THEN 1 ELSE 0 END)*100.0/COUNT(*),1),
ROUND(SUM(CASE WHEN result='2' THEN 1 ELSE 0 END)*100.0/COUNT(*),1)
FROM toto_matches
""")

home_rate, draw_rate, away_rate = cur.fetchone()

print(f"ホーム勝率 ：{home_rate}%")
print(f"引き分け率 ：{draw_rate}%")
print(f"アウェイ勝率：{away_rate}%")

print()

# 平均得点
cur.execute("""
SELECT
ROUND(AVG(home_score),2),
ROUND(AVG(away_score),2),
ROUND(AVG(home_score + away_score),2)
FROM toto_matches
""")

home_avg, away_avg, total_avg = cur.fetchone()

print(f"ホーム平均得点 ：{home_avg}")
print(f"アウェイ平均得点：{away_avg}")
print(f"1試合平均得点 ：{total_avg}")

print()

# 最多スコア
cur.execute("""
SELECT
home_score,
away_score,
COUNT(*) as cnt
FROM toto_matches
GROUP BY home_score, away_score
ORDER BY cnt DESC
LIMIT 10
""")

print("【多いスコア TOP10】")

for row in cur.fetchall():
    print(f"{row[0]}-{row[1]}   {row[2]}試合")

con.close()