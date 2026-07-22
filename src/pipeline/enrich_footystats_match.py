# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ORIGINAL_SCRIPT = (
    PROJECT_ROOT
    / "src/parsers/enrich_footystats_match_sides.py"
)

PARSERS_DIR = PROJECT_ROOT / "src/parsers"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "指定したFootyStats試合HTMLとJSONを使って、"
            "ホーム・アウェイ情報をJSONへ追加します。"
        )
    )

    parser.add_argument(
        "--html",
        required=True,
        type=Path,
        help="解析元HTMLファイル",
    )

    parser.add_argument(
        "--json",
        required=True,
        type=Path,
        help="更新対象JSONファイル",
    )

    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def load_original_module() -> ModuleType:
    if not ORIGINAL_SCRIPT.exists():
        raise FileNotFoundError(
            f"元スクリプトが見つかりません: {ORIGINAL_SCRIPT}"
        )

    parser_dir = str(PARSERS_DIR)

    if parser_dir not in sys.path:
        sys.path.insert(
            0,
            parser_dir,
        )

    spec = importlib.util.spec_from_file_location(
        "enrich_footystats_match_sides_runtime",
        ORIGINAL_SCRIPT,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "元スクリプトを読み込めませんでした"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def main() -> None:
    args = parse_args()

    html_path = resolve_path(
        args.html
    )

    json_path = resolve_path(
        args.json
    )

    if not html_path.is_file():
        raise FileNotFoundError(
            f"HTMLが見つかりません: {html_path}"
        )

    if not json_path.is_file():
        raise FileNotFoundError(
            f"JSONが見つかりません: {json_path}"
        )

    module = load_original_module()

    module.HTML_PATH = html_path
    module.JSON_PATH = json_path

    module.main()


if __name__ == "__main__":
    main()
