import sqlite3

DB = "data/toto.db"

con = sqlite3.connect(DB)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS round_standings (
    season INTEGER,
    round_no INTEGER,
    league TEXT,
    team TEXT,

    rank INTEGER,

    played INTEGER,
    win INTEGER,
    draw INTEGER,
    lose INTEGER,

    goals_for INTEGER,
    goals_against INTEGER,
    goal_diff INTEGER,

    points INTEGER,

    PRIMARY KEY (
        season,
        round_no,
        league,
        team
    )
)
""")

con.commit()
con.close()

print("round_standings 作成完了")
