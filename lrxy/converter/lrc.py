from typing import List, Tuple
import re

from lrxy.exceptions import UnexpectedTimingError
from .utils import Data, Line, Word, deformat_time, format_time


TIMESTAMP_PATTERN = r'(\d{2}(?::\d{2})+\.(?:\d+))'
METADATA_LINE_PATTERN = r'^\[(\D+):(.*)\]$'
LINE_PATTERN = rf'^(\[{TIMESTAMP_PATTERN}\](?:(v\d+):)?)? ?(.*)$'
WORD_PATTERN = rf'<{TIMESTAMP_PATTERN}>([^<]*)'
BG_PATTERN = r' ?\[bg:(.*?)\]'


def guess_timing(content: str) -> str:
    match = re.match(LINE_PATTERN, content)
    line_timestamp, line_content = match.group(1, 4)
    if line_timestamp:
        if re.search(WORD_PATTERN, line_content):
            return "Word"
        return "Line"
    return "None"


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


def parse(content: str) -> Data:
    timing = None
    lines: list[Line] = []
    for line_index, lrc_line in enumerate(content.splitlines()):
        if re.match(METADATA_LINE_PATTERN, lrc_line):
            continue

        if lrc_line and not timing:
            timing = guess_timing(lrc_line)

        match = re.match(LINE_PATTERN, lrc_line)
        agent, line_content = match.group(3, 4)
        if not match.group(1):
            if not lines or not lines[-1]['begin']:  # data has no timing
                if timing != 'None':
                    raise UnexpectedTimingError(line_index + 1, "lrc")
                lines.append({
                    'begin': None,
                    'end': None,
                    'agent': None,
                    'background': None,
                    'content': line_content,
                })
            elif line_content and lines and timing == "Line":
                # treat as multi-line lrc
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
            if (
                isinstance(line['content'], list) and timing != 'Word') or (
                isinstance(line['content'], str) and timing == 'Word'
            ):
                raise UnexpectedTimingError(line_index + 1, "lrc")
            lines.append(line)
        lines.extend(bg_lines)

    return {
        'timing': timing,
        'lyrics': lines,
    }


def generate_line_content(timing, line: Line) -> str:
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


def generate_line_timestamp(line: Line) -> str:
    timestamp = f'[{format_time(line["begin"])}]'
    if line['agent']:
        timestamp += line['agent'] + ':'
    return timestamp


def generate(data: Data) -> str:
    content = ''
    last_line_end = 0
    timing = data['timing']
    for line in data['lyrics']:
        if timing == 'None':
            content += line['content'] + '\n'
            continue

        if line['background']:
            content = content[:-1] + ' [bg:'
        else:
            content += generate_line_timestamp(line)

        content += generate_line_content(timing, line)

        if line['background']:
            content += ']'

        content += '\n'

        if timing == 'Line':
            if last_line_end and last_line_end != line['begin']:
                content += generate_line_timestamp(line) + "\n"
        last_line_end = line['end']

    if timing == "Line":
        content += generate_line_timestamp(line) + "\n"

    return content
