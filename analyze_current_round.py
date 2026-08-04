from __future__ import annotations

import argparse
import sys

import pandas as pd

from match_report import print_summary


CURRENT_FILE = "current_toto_matches.csv"


def load_match_numbers(
    hold_cnt_id: int,
) -> list[int]:
    try:
        df = pd.read_csv(
            CURRENT_FILE,
            dtype={
                "hold_cnt_id": "Int64",
                "match_no": "Int64",
            },
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{CURRENT_FILE} が見つかりません。"
        )

    required = {
        "hold_cnt_id",
        "match_no",
        "home",
        "away",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "current_toto_matches.csvに必要な列がありません: "
            + ", ".join(sorted(missing))
        )

    target = df[
        df["hold_cnt_id"] == hold_cnt_id
    ].copy()

    if target.empty:
        raise ValueError(
            f"第{hold_cnt_id}回のデータがありません。"
        )

    target = target.sort_values("match_no")

    return [
        int(value)
        for value in target["match_no"].dropna()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "TOTO LABOの開催回全試合レポートを"
            "一括表示します。"
        )
    )

    parser.add_argument(
        "hold_cnt_id",
        type=int,
        help="toto開催回",
    )

    args = parser.parse_args()

    try:
        match_numbers = load_match_numbers(
            args.hold_cnt_id
        )
    except (
        FileNotFoundError,
        ValueError,
        pd.errors.ParserError,
    ) as error:
        print(
            f"エラー: {error}",
            file=sys.stderr,
        )
        return 1

    print()
    print("#" * 72)
    print(
        f"TOTO LABO 第{args.hold_cnt_id}回 "
        f"全試合レポート"
    )
    print(
        f"対象試合数: {len(match_numbers)}"
    )
    print("#" * 72)

    success = 0
    failed = 0

    for index, match_no in enumerate(
        match_numbers,
        start=1,
    ):
        print()
        print()
        print(
            f"[{index}/{len(match_numbers)}] "
            f"No.{match_no}"
        )
        print()

        result = print_summary(
            args.hold_cnt_id,
            match_no,
        )

        if result == 0:
            success += 1
        else:
            failed += 1

        if index < len(match_numbers):
            print()
            print("-" * 72)

    print()
    print("#" * 72)
    print("全試合レポート終了")
    print(f"成功: {success}")
    print(f"失敗: {failed}")
    print("#" * 72)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
