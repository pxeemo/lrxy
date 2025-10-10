#!/usr/bin/env python
import sys
import json
from pathlib import Path
from typing import Literal
import logging

import argparse
import argcomplete

from lrxy.converter import lrc, ttml, srt
from lrxy.exceptions import UnsupportedFileFormatError, ParseLyricError
from lrxy import completions


SUPPORTED_INPUTS = ["ttml", "lrc", "srt", "json"]
SUPPORTED_OUTPUTS = ["ttml", "lrc", "srt", "json"]

logger = logging.getLogger(__name__)


def get_parser():
    parser = argparse.ArgumentParser(
        prog='lrxy-convert',
        description=('A tool from lrxy '
                     'to convert between different lyric formats')
    )

    parser.add_argument(
        '-i', '--input-format',
        choices=SUPPORTED_INPUTS,
        default=None,
        help='input lyric file format'
    )

    parser.add_argument(
        '-o', '--output-format',
        choices=SUPPORTED_OUTPUTS,
        default=None,
        help='output lyric file format'
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
        'input',
        metavar='INPUT',
        help='path of the input file to convert from'
    )

    parser.add_argument(
        'output',
        metavar='OUTPUT',
        help='path of the output file to convert to'
    )

    return parser


def main():
    parser = get_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    logger.setLevel(getattr(logging, args.log_level.upper()))
    logger.debug("Parser args: %s", args)

    input_file = sys.stdin if args.input == '-' else Path(args.input)
    output_file = sys.stdout if args.output == '-' else Path(args.output)

    if args.input_format:
        input_format = args.input_format
    elif isinstance(input_file, Path):
        input_format = input_file.suffix[1:]
        if input_format not in SUPPORTED_INPUTS:
            logger.error(
                "%s: Input format '%s' is not supported.",
                input_file,
                input_file.suffix,
            )
            sys.exit(1)
    else:
        parser.error("Can't read from stdin"
                     "without specifying '-i/--input-format'")
        sys.exit(1)

    if args.output_format:
        output_format = args.output_format
    elif isinstance(output_file, Path):
        output_format = output_file.suffix[1:]
        if output_format not in SUPPORTED_OUTPUTS:
            logger.error(
                "%s: Output format '%s' is not supported.",
                output_file,
                output_file.suffix,
            )
            sys.exit(1)
    else:
        output_format = "json"

    if isinstance(input_file, Path):
        with open(input_file, "r", encoding="utf-8") as f:
            input_content = f.read()
    else:
        input_content = input_file.read()
    logger.debug("Input content: %s\n", input_content)

    try:
        result = convert(
            from_format=input_format,
            to_format=output_format,
            input_content=input_content,
        )
    except ParseLyricError as e:
        logger.error(e)
        sys.exit(1)

    if isinstance(output_file, Path):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        output_file.write(result)


def convert(
    from_format: Literal[*SUPPORTED_INPUTS],
    to_format: Literal[*SUPPORTED_OUTPUTS],
    input_content: str,
) -> str:
    if from_format == to_format:
        return input_content

    logger.debug("Converting from %s to %s", from_format, to_format)
    match from_format:
        case "lrc":
            data = lrc.parse(input_content)
        case "ttml":
            data = ttml.parse(input_content)
        case "srt":
            data = srt.parse(input_content)
        case "json":
            data = json.loads(input_content)
        case _:
            raise UnsupportedFileFormatError()
    logger.debug("Parsed data: %s\n", data)

    match to_format:
        case "lrc":
            result = lrc.generate(data)
        case "ttml":
            result = ttml.generate(data)
        case "srt":
            if data["timing"] == "None":
                logger.error(
                    "The lyric lacks timing information, "
                    "which is not supported by the SRT format."
                )
                sys.exit(1)
            elif data["timing"] == "Word":
                logger.warning(
                    "The lyric is synced at the word level, "
                    "which the SRT format does not support. "
                    "It will be converted to line-level syncing."
                )
            result = srt.generate(data)
        case _:
            result = json.dumps(data)
    logger.debug("Converted data: %s\n", result)

    return result


if __name__ == "__main__":
    main()
