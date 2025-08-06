import sys
import argparse
import logging
from lrxy.utils import iter_files


def main():
    logger = logging.getLogger(__name__)

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
        "--log-level",
        choices=["error", "warning", "info", "debug"],
        default="info",
        help="set log level"
    )

    parser.add_argument(
        "files",
        metavar="MUSIC_FILE",
        action="append",
        nargs="+",
        help="path of music files to process"
    )

    args = parser.parse_args()
    fetch = not args.embed

    logger.setLevel(getattr(logging, args.log_level.upper()))
    logger.debug(args)

    if args.embed and len(args.files[0]) > 1:
        parser.error("Can't use '--embed' with multiple music files")
        sys.exit(2)

    for result in iter_files(*args.files[0], fetch=fetch):
        audio = result["music_obj"]
        logger.debug(result)
        if args.embed:
            audio.embed_from_lrc(args.embed[0])
            logger.info("Successfully embedded lyric from file")
        elif result['success']:
            plain_lyric = result["data"]["plainLyrics"]
            synced_lyric = result["data"]["syncedLyrics"]
            lyric = synced_lyric

            if plain_lyric and not synced_lyric:
                logger.warning("Synced lyric not available. Falling back to plain lyric.")
                lyric = plain_lyric
            elif not plain_lyric:
                logger.error(f"Song has no lyric: {audio.path}")
                continue

            try:
                if args.write_lrc:
                    lrc_file = audio.path.with_suffix(".lrc")
                    if lrc_file.exists():
                        raise FileExistsError(
                            f"File already exists: {lrc_file}")

                    with open(lrc_file, "w", encoding="utf-8") as f:
                        f.write(lyric)

                    logger.info(f"Successfully written to: {lrc_file}")
                else:
                    audio.embed_lyric(lyric)
                    logger.info(f"Successfully embedded the lyric: {audio}")
            except FileExistsError as e:
                logger.error(e)

        elif result['data'] == 'notfound':
            logger.error(f"Music not found: {audio}")


if __name__ == "__main__":
    main()
