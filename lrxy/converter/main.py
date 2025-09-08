#!/usr/bin/env python
import sys
import json
import argparse
from pathlib import Path
from typing import Literal
import logging

from lrxy.converter import lrc, ttml, srt
from lrxy.exceptions import UnsupportedFileFormatError


SUPPORTED_INPUTS = ["ttml", "lrc", "srt", "json"]
SUPPORTED_OUTPUTS = ["ttml", "lrc", "srt", "json"]
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        prog='lrxy-convert',
        description='A tool from lrxy to convert lyric formats'
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

    parser.add_argument(
        '-i', '--input-format',
        choices=SUPPORTED_INPUTS,
        nargs=1,
        default=None,
        help='specify the format to convert from'
    )

    parser.add_argument(
        '-o', '--output-format',
        choices=SUPPORTED_OUTPUTS,
        nargs=1,
        default=None,
        help='specify the format to convert to'
    )

    parser.add_argument(
        "--log-level",
        choices=["error", "warning", "info", "debug"],
        default="info",
    )

    args = parser.parse_args()
    logger.setLevel(getattr(logging, args.log_level.upper()))
    logger.debug("Parser args: %s", args)

    input = sys.stdin if args.input == '-' else Path(args.input)
    output = sys.stdout if args.output == '-' else Path(args.output)

    if args.input_format:
        input_format = args.input_format[0]
    else:
        if isinstance(input, Path):
            match input.suffix:
                case ".lrc":
                    input_format = "lrc"
                case ".ttml":
                    input_format = "ttml"
                case ".srt":
                    input_format = "srt"
                case ".json":
                    input_format = "json"
                case _:
                    logger.error(
                        "%s: Input format '%s' is not supported.",
                        input,
                        input.suffix,
                    )
        else:
            parser.error("Can't read from stdin"
                         "without specifying '-i/--input-format'")

    if args.output_format:
        output_format = args.output_format[0]
    else:
        if isinstance(output, Path):
            match output.suffix:
                case ".lrc":
                    output_format = "lrc"
                case ".ttml":
                    output_format = "ttml"
                case ".srt":
                    output_format = "srt"
                case ".json":
                    output_format = "json"
                case _:
                    logger.error(
                        "%s: Output format '%s' is not supported.",
                        output,
                        output.suffix,
                    )
        else:
            output_format = "json"

    if isinstance(input, Path):
        with open(input, "r", encoding="utf-8") as f:
            input_content = f.read()
    else:
        input_content = input.read()
    logger.debug("Input content: %s\n", input_content)

    result = convert(
        from_format=input_format,
        to_format=output_format,
        input=input_content,
    )

    if isinstance(output, Path):
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        output.write(result)


def convert(
    from_format: Literal[*SUPPORTED_INPUTS],
    to_format: Literal[*SUPPORTED_OUTPUTS],
    input: str,
) -> str:
    if from_format == to_format:
        return input

    logger.debug("Converting from %s to %s", from_format, to_format)
    match from_format:
        case "lrc":
            data = lrc.parse(input)
        case "ttml":
            data = ttml.parse(input)
        case "srt":
            data = srt.parse(input)
        case "json":
            data = json.loads(input)
        case _:
            raise UnsupportedFileFormatError(from_format)
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
