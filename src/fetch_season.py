import ssl
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://data.j-league.or.jp/SFMS01/search"
OUTPUT_ROOT = Path("data/jleague_seasons")


def build_url(year, frame_id):
    params = {
        "competition_years": year,
        "competition_frame_ids": frame_id,
        "tv_relay_station_name": "",
    }
    return f"{BASE_URL}?{urlencode(params)}"


def download(url, output_path):
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36"
            )
        },
    )

    context = ssl._create_unverified_context()

    with urlopen(request, context=context, timeout=60) as response:
        body = response.read()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(body)

    print(f"保存: {output_path} ({len(body):,} bytes)")


def fetch_season(year):
    targets = [
        ("j1", 1),
        ("j2", 2),
    ]

    for league, frame_id in targets:
        url = build_url(year, frame_id)
        output_path = OUTPUT_ROOT / str(year) / f"{league}.html"

        print(f"取得: {year} {league.upper()}")
        download(url, output_path)


def main():
    if len(sys.argv) != 2:
        print("使い方: python3 src/fetch_season.py YEAR")
        print("例: python3 src/fetch_season.py 2002")
        sys.exit(1)

    year = int(sys.argv[1])
    fetch_season(year)

    print(f"{year}年 J1/J2 HTML取得完了")


if __name__ == "__main__":
    main()