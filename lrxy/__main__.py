import argparse
from lrxy.utils import iter_files


def main():
    parser = argparse.ArgumentParser(
        prog="lrxy",
        description="A synced lyric fetcher and embedder for music files"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write-lrc",
        action="store_true",
        help="write lyrics to .lrc files"
    )
    group.add_argument(
        "--embed",
        metavar="LRC_FILE",
        nargs=1,
        help="embed existing lyrics file into music"
    )

    parser.add_argument(
        "files",
        metavar="MUSIC_FILE",
        action="append",
        nargs="+",
        help="path of music files to process"
    )

    args = parser.parse_args()
    print(args)

    if args.embed:
        if len(args.files[0]) > 1:
            parser.error("can't use '--embed' with multiple music files")
            return

        # TODO: read and embed from an lrc file
        print("--embed is not implemented yet!")
        return

    for result in iter_files(*args.files[0]):
        if result['success']:
            audio = result["music_obj"]
            plain_lyric = result["data"]["plainLyrics"]
            synced_lyric = result["data"]["syncedLyrics"]
            lyric = synced_lyric

            if plain_lyric and not synced_lyric:
                print("Synced lyric not available. Falling back to plain lyric.")
                lyric = plain_lyric
            elif not plain_lyric:
                print(f"Song has no lyric: {audio.path}")
                continue

            if args.write_lrc:
                lrc_file = audio.path.with_suffix(".lrc")
                if lrc_file.exists():
                    raise FileExistsError

                with open(lrc_file, "w", encoding="utf-8") as f:
                    f.write(lyric)

                print(f"Successfully written to: {lrc_file}")
            else:
                audio.embed_lyric(lyric)
                print("Successfully embedded the lyric")


if __name__ == "__main__":
    main()
