# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ORIGINAL_SCRIPT = (
    PROJECT_ROOT
    / "src/database/import_footystats_match.py"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "指定したFootyStats試合JSONを"
            "data/toto.dbへ登録します。"
        )
    )

    parser.add_argument(
        "--json",
        required=True,
        type=Path,
        help="取込対象JSONファイル",
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

    spec = importlib.util.spec_from_file_location(
        "import_footystats_match_runtime",
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

    json_path = resolve_path(
        args.json
    )

    if not json_path.is_file():
        raise FileNotFoundError(
            f"JSONが見つかりません: {json_path}"
        )

    module = load_original_module()

    module.JSON_PATH = json_path

    module.main()


if __name__ == "__main__":
    main()
