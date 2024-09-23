import argparse
from lrxy.utils import iter_files


def main():
    parser = argparse.ArgumentParser(
        prog="lrxy",
        description="A synced lyric fetcher and embedder for music files"
    )

    parser.add_argument(
        "-s", "--separate",
        action="store_true",
        help="write lyric to a lrc file",
    )

    parser.add_argument(
        "file",
        nargs="+",
        help="path of music file"
    )

    args = parser.parse_args()

    files = iter_files(*args.file)
    for res in files:
        print(f"file: {res['path']}")
        success, data = res["success"], res["data"]
        if success:
            audio = res["path"]
            plain_lyric = res["data"]["plainLyrics"]
            synced_lyric = res["data"]["syncedLyrics"]

            audio.embed_lyric(synced_lyric)
            print("successful embeded synced lyric")
        else:
            if data == "notfound":
                print("i can't found lyric for this music")
            else:
                print(f"error: {data}")
        print("*"*10)


if __name__ == "__main__":
    main()
