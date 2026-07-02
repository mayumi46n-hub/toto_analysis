import subprocess
import os

round_list = range(1637, 1600, -1)

total = len(round_list)

print("=" * 60)
print("        TotoLab 自動更新")
print("=" * 60)

success_count = 0
skip_count = 0
fail_count = 0

skipped_rounds = []
failed_rounds = []

for i, round_no in enumerate(round_list, start=1):

    print()
    print(f"[{i}/{total}] 第{round_no}回")

    html_file = f"data/toto_round_{round_no}.html"

    if os.path.exists(html_file):
        print("HTMLあり → ダウンロード省略")
    else:
        try:
            subprocess.run(
                ["python3", "src/download_round.py", str(round_no)],
                check=True
            )
        except Exception:
            print("❌ ダウンロード失敗")
            fail_count += 1
            failed_rounds.append(round_no)
            continue

    result = subprocess.run(
        ["python3", "src/parse_round.py", str(round_no)]
    )

    if result.returncode == 0:
        print("✅ DB登録完了")
        success_count += 1

    elif result.returncode == 2:
        print("⏭ スキップ")
        skip_count += 1
        skipped_rounds.append(round_no)

    else:
        print("❌ 解析またはDB登録に失敗")
        fail_count += 1
        failed_rounds.append(round_no)

print()
print("=" * 60)
print("更新終了")
print(f"成功: {success_count}開催")
print(f"スキップ: {skip_count}開催")
print(f"失敗: {fail_count}開催")

if skipped_rounds:
    print()
    print("スキップした開催回")
    print("-" * 20)
    for r in skipped_rounds:
        print(f"第{r}回")

if failed_rounds:
    print()
    print("失敗した開催回")
    print("-" * 20)
    for r in failed_rounds:
        print(f"第{r}回")

print("=" * 60)