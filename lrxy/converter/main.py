#!/usr/bin/env python
import sys
import json
import argparse
from pathlib import Path
from typing import Literal
import logging

from lrxy.converter import lrc, ttml
from lrxy.exceptions import UnsupportedFileFormatError


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
        '-f', '--format',
        metavar='format',
        dest='format',
        nargs=1,
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

    input = Path(args.input)
    if args.output == '-':
        output = sys.stdout
    else:
        output = Path(args.output)

    match input.suffix:
        case ".lrc":
            input_format = "lrc"
        case ".ttml":
            input_format = "ttml"
        case _:
            raise UnsupportedFileFormatError(input)

    if args.format:
        output_format = args.format[0]
    else:
        if isinstance(output, Path):
            match output.suffix:
                case ".lrc":
                    output_format = "lrc"
                case ".ttml":
                    output_format = "ttml"
                case ".json":
                    output_format = "json"
                case _:
                    raise UnsupportedFileFormatError(output)
        else:
            output_format = "json"

    with open(input, "r", encoding="utf-8") as f:
        input_content = f.read()
    logger.debug("Input content: %s", input_content)

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
    from_format: Literal["lrc", "ttml", "json"],
    to_format: Literal["lrc", "ttml", "json"],
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
        case _:
            raise UnsupportedFileFormatError(from_format)
    logger.debug("Parsed data: %s", data)

    match to_format:
        case "lrc":
            result = lrc.generate(data)
        case "ttml":
            result = ttml.generate(data)
        case _:
            result = json.dumps(data)
    logger.debug("Converted data: %s", result)

    return result


if __name__ == "__main__":
    main()
