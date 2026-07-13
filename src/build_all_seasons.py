import argparse
import subprocess
import sys
import time


def run_command(command):
    print()
    print("実行:", " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        raise RuntimeError(
            f"コマンドが失敗しました: {' '.join(command)}"
        )


def process_season(
    season,
    skip_fetch=False,
    skip_import=False,
):
    python = sys.executable

    print()
    print("=" * 72)
    print(f"{season}年の処理を開始")
    print("=" * 72)

    if not skip_fetch:
        run_command([
            python,
            "src/fetch_season.py",
            str(season),
        ])
    else:
        print(f"{season}年: HTML取得をスキップ")

    if not skip_import:
        run_command([
            python,
            "src/import_season.py",
            str(season),
        ])
    else:
        print(f"{season}年: DB取込をスキップ")

    run_command([
        python,
        "src/build_match_standings.py",
        str(season),
    ])

    run_command([
        python,
        "src/build_match_features_season.py",
        str(season),
    ])

    print()
    print(f"{season}年の処理完了")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "指定年度範囲のJリーグデータ取得・取込・"
            "試合前順位生成・特徴量生成を一括実行します。"
        )
    )

    parser.add_argument(
        "start_season",
        type=int,
        help="開始年度。例: 2002",
    )

    parser.add_argument(
        "end_season",
        type=int,
        help="終了年度。例: 2005",
    )

    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="HTML取得を省略します",
    )

    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="DB取込を省略します",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="年度ごとの待機秒数。既定値: 1.0",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="年度処理でエラーが出ても次年度へ進みます",
    )

    args = parser.parse_args()

    if args.start_season > args.end_season:
        parser.error(
            "開始年度は終了年度以下にしてください"
        )

    succeeded = []
    failed = []

    seasons = range(
        args.start_season,
        args.end_season + 1,
    )

    for season in seasons:
        try:
            process_season(
                season=season,
                skip_fetch=args.skip_fetch,
                skip_import=args.skip_import,
            )
            succeeded.append(season)

        except Exception as error:
            failed.append((season, str(error)))

            print()
            print(f"エラー: {season}年")
            print(error)

            if not args.continue_on_error:
                print("処理を停止します")
                sys.exit(1)

        if (
            season < args.end_season
            and args.delay > 0
        ):
            time.sleep(args.delay)

    print()
    print("=" * 72)
    print("全年度処理結果")
    print("=" * 72)
    print(f"成功: {len(succeeded)}年度")
    print(f"失敗: {len(failed)}年度")

    if succeeded:
        print(
            "成功年度:",
            ", ".join(str(year) for year in succeeded),
        )

    if failed:
        print("失敗年度:")

        for season, message in failed:
            print(f"  {season}: {message}")

        sys.exit(1)

    print("全年度のSeason Pipelineが完了しました")


if __name__ == "__main__":
    main()