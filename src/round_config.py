def get_round_config(round_no):
    if round_no == 1:
        return {
            "html": "data/toto_club_2001_utf8.html",
            "table": 2,
        }

    if round_no == 2:
        return {
            "html": "data/toto_club_2001_utf8.html",
            "table": 1,
        }

    # 第31回は2001年最後の単独ページなので table 構造が通常と違う
    if round_no == 31:
        return {
            "html": "data/toto_club_2001_yosou15_utf8.html",
            "table": 1,
        }

    yosou_no = (round_no - 1) // 2
    table_index = 2 if round_no % 2 == 1 else 1

    return {
        "html": f"data/toto_club_2001_yosou{yosou_no}_utf8.html",
        "table": table_index,
    }