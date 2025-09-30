import logging
import re

from lrxy.exceptions import ParseLyricError
from .utils import Data, Line, deformat_time, format_time

TIMESTAMP_PATTERN = r'\d{2}(?::\d{2})+,\d+'
TIMESTAMP_LINE_PATTERN = fr'({TIMESTAMP_PATTERN}) --> ({TIMESTAMP_PATTERN})'
BLOCK_PATTERN = fr'^(\d+)\n{TIMESTAMP_LINE_PATTERN}\n(.+)'

logger = logging.getLogger(__name__)


def generate(data: Data) -> str:
    content = ''
    for index, line in enumerate(data['lyrics']):
        content += f'{index + 1}\n'

        content += format_time(line['begin'], srt=True)
        content += ' --> '
        content += format_time(line['end'], srt=True)

        if data['timing'] == 'Line':
            content += f'\n{line['content']}\n\n'
        elif data['timing'] == 'Word':
            text = ''
            for word in line['content']:
                text += word['text']
                if not word['part'] and word != line['content'][-1]:
                    text += ' '
            content += f'\n{text}\n\n'

    return content


def parse(content: str) -> Data:
    blocks = content.split("\n\n")
    lines: list[Line] = []
    last_line_number = 0
    for block in blocks:
        match = re.match(BLOCK_PATTERN, block)
        if not match:
            continue

        line_number = int(match.group(1))
        if line_number != last_line_number + 1:
            logger.debug(block)
            raise ParseLyricError('srt')
        last_line_number = line_number
        line: Line = {
            'begin': deformat_time(match.group(2), srt=True),
            'end': deformat_time(match.group(3), srt=True),
            'agent': None,
            'background': False,
            'content': match.group(4),
        }
        lines.append(line)

    data: Data = {
        'timing': 'Line',
        'lyrics': lines,
    }
    return data
