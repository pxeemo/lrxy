import sys
import argparse
import logging

from lrxy.utils import iter_files
from lrxy.converter import convert, SUPPORTED_OUTPUTS
from lrxy.providers import lrclib_api, musixmatch_api


def get_version():
    from importlib_metadata import version
    return version("lrxy")


def main():
    logger = logging.getLogger()

    parser = argparse.ArgumentParser(
        prog="lrxy",
        description="A synced lyric fetcher and embedder for music files",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-n", "--no-embed",
        action="store_true",
        help="write lyrics to separate text files",
    )
    group.add_argument(
        "--embed",
        metavar="FILE",
        nargs=1,
        help="embed existing lyric file into music",
    )

    parser.add_argument(
        "-f", "--format",
        choices=SUPPORTED_OUTPUTS,
        nargs=1,
        default=["lrc"],
        help="output lyrics format",
    )

    parser.add_argument(
        "-p", "--provider",
        choices=["lrclib", "musixmatch"],
        nargs=1,
        default=["lrclib"],
        help="provider to fetch lyrics",
    )

    parser.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="do not overwrite existing lyrics",
    )

    parser.add_argument(
        "--log-level",
        choices=["error", "warning", "info", "debug"],
        nargs=1,
        default=["info"],
        help="command line verbosity",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="show current lrxy version and exit",
    )

    parser.add_argument(
        "files",
        metavar="MUSIC_FILE",
        action="append",
        nargs="+",
        help="path of music file to process",
    )

    args = parser.parse_args()
    fetch = not args.embed

    match args.provider[0]:
        case "lrclib":
            provider = lrclib_api
        case "musixmatch":
            provider = musixmatch_api

    logger.setLevel(getattr(logging, args.log_level[0].upper()))
    logger.debug("Parser args: %s", args)

    if args.embed and len(args.files[0]) > 1:
        parser.error("Can't use '--embed' with multiple music files")
        sys.exit(2)

    for result in iter_files(*args.files[0], fetch=fetch, provider=provider):
        logger.debug("File data: %s\n", result)
        audio = result["music_obj"]
        if args.embed:
            audio.embed_from_file(args.embed[0])
            logger.info("Successfully embedded lyric from file: %s", audio)
        elif result['success']:
            lyric_data = result["data"]
            lyric = convert(
                from_format=lyric_data["format"],
                to_format=args.format[0],
                input=lyric_data["lyric"],
            ) if lyric_data is not None else None

            if not lyric:
                logger.error("%s: Song has no lyric.", audio)
                continue

            if args.no_embed:
                file = audio.path.with_suffix(f".{args.format[0]}")
                if file.exists() and not args.overwrite:
                    logger.error("%s: File already exists.", file)
                else:
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(lyric)

                    logger.info("Successfully written to: %s", file)
            else:
                if audio.has_lyric and not args.overwrite:
                    logger.error("%s: Audio file already has embedded lyric.", audio)
                else:
                    audio.embed_lyric(lyric)
                    logger.info("Successfully embedded the lyric: %s", audio)

        else:
            logger.error("%s: %s", audio.path, result['error_message'])


if __name__ == "__main__":
    main()
