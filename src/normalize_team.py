import sqlite3

DB_PATH = "data/toto.db"


def normalize_team_name(name):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
    SELECT official_name
    FROM team_alias
    WHERE alias_name=?
    """, (name,))

    row = cur.fetchone()

    con.close()

    if row:
        return row[0]

    return name

if __name__ == "__main__":
    test_names = [
        "Ｆ東京",
        "FC東京",
        "東京",
        "横浜FM",
        "Ｃ大阪",
        "市原",
        "鹿島",
    ]

    for name in test_names:
        print(name, "→", normalize_team_name(name))