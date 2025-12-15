import sys
import logging

import argparse
import argcomplete

from lrxy.utils import iter_files
from lrxy.converter import convert, SUPPORTED_OUTPUTS
from lrxy.providers import lrclib_api, musixmatch_api, applemusic_api, qq_api
from lrxy import completions


def get_version():
    from importlib.metadata import version
    return version("lrxy")


def get_parser():
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
        help="embed existing lyric file into music",
    )

    parser.add_argument(
        "-f", "--format",
        choices=SUPPORTED_OUTPUTS,
        default=None,
        help="output lyrics format",
    )

    parser.add_argument(
        "-p", "--provider",
        choices=["lrclib", "musixmatch", "applemusic", "qq"],
        default="lrclib",
        help="provider to fetch lyrics",
    )

    parser.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="do not overwrite existing lyrics",
    )

    parser.add_argument(
        "--shell-completion",
        choices=["bash", "zsh", "fish"],
        type=completions.generate_completion,
        dest="completion",
        help="provide shell completion",
    )

    parser.add_argument(
        "--log-level",
        choices=["error", "warning", "info", "debug"],
        default="info",
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
        action="extend",
        nargs="+",
        help="path of music file to process",
    )

    return parser


def main():
    logger = logging.getLogger()
    parser = get_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    fetch = not args.embed

    match args.provider:
        case "lrclib":
            provider = lrclib_api
        case "musixmatch":
            provider = musixmatch_api
        case "applemusic":
            provider = applemusic_api
        case "qq":
            provider = qq_api

    logger.setLevel(getattr(logging, args.log_level.upper()))
    logger.debug("Parser args: %s", args)

    if args.embed and len(args.files) > 1:
        parser.error("Can't use '--embed' with multiple music files")
        sys.exit(2)

    for result in iter_files(*args.files, fetch=fetch, provider=provider):
        logger.debug("File data: %s\n", result)
        audio = result["music_obj"]
        lyric_data = result["data"]
        output_format = args.format or "lrc"

        if args.embed:  # embed from file
            audio.embed_from_file(args.embed)
            logger.info("Successfully embedded lyric from file: %s", audio)
            continue

        if not result['success']:
            logger.error("%s: %s", result['path'], result['error_message'])
            continue

        if not lyric_data["hasLyric"]:
            logger.error("%s: Song has no synced lyric.", audio)
            continue

        if not args.format and lyric_data["format"] != "json":
            lyric = lyric_data["lyric"]
        else:
            lyric = convert(
                from_format=lyric_data["format"],
                to_format=output_format,
                input_content=lyric_data["lyric"],
            )

        if args.no_embed:
            file = audio.path.with_suffix(f".{output_format}")
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


if __name__ == "__main__":
    main()
