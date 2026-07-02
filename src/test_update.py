import subprocess

# まずは3開催分だけ
round_list = [1636, 1635, 1634]

for round_no in round_list:

    print("=" * 50)
    print(f"第{round_no}回 開始")
    print("=" * 50)

    subprocess.run([
        "python3",
        "src/download_round.py",
        str(round_no)
    ])

    subprocess.run([
        "python3",
        "src/parse_round.py",
        str(round_no)
    ])

print()
print("★★★★★ 全て終了しました ★★★★★")