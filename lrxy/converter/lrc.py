from typing import List, Tuple
import re

from lrxy.exceptions import ParseLyricError
from .utils import Data, Line, Word, deformat_time, format_time


TIMESTAMP_PATTERN = r'(\d{2}(?::\d{2})+\.(?:\d+))'
METADATA_LINE_PATTERN = r'^\[(\D+):(.*)\]$'
LINE_PATTERN = rf'^(\[{TIMESTAMP_PATTERN}\](?:(v\d+):)?)? ?(.*)$'
WORD_PATTERN = rf'<{TIMESTAMP_PATTERN}>([^<]*)'
BG_PATTERN = r' ?\[bg:(.*?)\]'


def parse_line(
    content: str,
    agent: str | None = None,
    begin_time: int | None = None,
    background: bool = False
) -> Tuple[Line, List[Line]]:
    line: Line = {
        'begin': begin_time,
        'end': None,
        'agent': agent,
        'background': background,
        'content': [],
    }

    bg_lines: list[Line] = []
    for bg_line in re.finditer(BG_PATTERN, content):
        bg_line_data, _ = parse_line(bg_line.group(1), background=True)
        bg_lines.append(bg_line_data)
        # content = (content[bg_line.span()[0]:] +
        #                content[:bg_line.span()[1]])
        content = ''.join(content.split(bg_line.group(0)))

    time = 0
    for word_match in re.finditer(WORD_PATTERN, content):
        time = deformat_time(word_match.group(1))
        if line['content']:
            if not line['content'][-1]['end']:
                line['content'][-1]['end'] = time
        elif not line['begin']:
            line['begin'] = time

        word_text = word_match.group(2)
        if not word_text:
            continue

        word: Word = {
            'begin': deformat_time(word_match.group(1)),
            'end': None,
            'part': not word_text.endswith(' '),
            'text': word_text.removesuffix(' '),
        }
        line['content'].append(word)

    if not line['end'] and time:
        line['end'] = time

    # if it's not word by word
    if not line['content']:
        line['content'] = content

    return line, bg_lines


def generate_line(timing, line: Line) -> str:
    if timing == 'Line':
        return line['content']

    content = ''
    for word in line['content']:
        word_begin = f'<{format_time(word["begin"])}>'
        if not content.endswith(word_begin):
            content += word_begin

        content += word['text']
        if not word['part'] and word != line['content'][-1]:
            content += ' '

        content += f'<{format_time(word["end"])}>'

    line_end = f'<{format_time(line["end"])}>'
    if not content.endswith(line_end):
        content += line_end

    return content


def generate(data: Data) -> str:
    content = ''
    last_line_end = 0
    timing = data['timing']
    for line in data['lyrics']:
        if timing == 'None':
            content += line['content'] + '\n'
            continue

        if not line['background']:
            content += f'[{format_time(line["begin"])}]'
            if line['agent']:
                content += line['agent'] + ':'
        else:
            content = content[:-1] + ' [bg:'

        content += generate_line(timing, line)

        if line['background']:
            content += ']'

        content += '\n'

        if timing == 'Line':
            if last_line_end and last_line_end != line['begin']:
                content += f'[{format_time(last_line_end)}]\n'
        last_line_end = line['end']

    return content


def get_timing(line_content: str | list) -> str:
    if isinstance(line_content, list):
        return "Word"
    if isinstance(line_content, str):
        return "Line"
    raise ParseLyricError('lrc')


def parse(content: str) -> Data:
    timing = None
    lines: list[Line] = []
    for lrc_line in content.splitlines():
        if re.match(METADATA_LINE_PATTERN, lrc_line):
            continue

        match = re.match(LINE_PATTERN, lrc_line)
        agent, line_content = match.group(3, 4)
        if not match.group(1):
            if not lines or not lines[-1]['begin']:  # data has no timing
                if not timing:
                    timing = 'None'
                lines.append({
                    'begin': None,
                    'end': None,
                    'agent': None,
                    'background': None,
                    'content': line_content,
                })
            elif lines:  # treat as multi-line lrc
                lines[-1]['content'] += "\n" + line_content
            continue

        begin_time = deformat_time(match.group(2))
        line, bg_lines = parse_line(
            content=line_content,
            agent=agent,
            begin_time=begin_time,
        )

        if lines and not lines[-1]['end']:
            lines[-1]['end'] = begin_time

        if line['content']:
            lines.append(line)
        lines.extend(bg_lines)

        new_timing = get_timing(line['content'])
        if not timing:
            timing = new_timing
        elif timing != new_timing:
            raise ParseLyricError('lrc')

    return {
        'timing': timing,
        'lyrics': lines,
    }
