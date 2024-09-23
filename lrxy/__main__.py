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

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-y",
        action="store_true",
        help="automatically confirm all prompts"
    )
    group.add_argument(
        "--no-prompt",
        action="store_true",
        help="skip all prompts and use default behavior",
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

            if synced_lyric:
                lyric = synced_lyric
            elif plain_lyric:
                if args.y:
                    print("This song has no synced lyric. " +
                          "Using plain lyric instead...")
                    lyric = plain_lyric
                elif args.no_prompt:
                    print("This song has no synced lyric. Ignoring...")
                    continue
                else:
                    choice = input(
                        "This song has no synced lyric. " +
                        "Use plain lyric? [y/N] ")
                    if choice.lower() == "y":
                        lyric = plain_lyric
                    elif choice.lower() == "n" or not choice:
                        continue
                    else:
                        print("unexpected input")
                        continue
            else:
                print("This song has no lyric.")
                continue

            if args.separate:
                lrc_file = audio.path.with_suffix(".lrc")
                with open(lrc_file, "w", encoding="utf-8") as f:
                    f.write(lyric)
                print("successful written lrc file")
            else:
                audio.embed_lyric(lyric)
                print("successful embedded synced lyric")
        else:
            if data == "notfound":
                print("i can't found lyric for this music")
            else:
                print(f"error: {data}")
        print("*"*10)


if __name__ == "__main__":
    main()
