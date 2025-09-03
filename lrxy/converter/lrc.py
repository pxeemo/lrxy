from typing import List, Tuple
import json
import re

from lrxy.exceptions import ParseLyricError
from .utils import Data, Line, Word, deformatTime, formatLrcTime


TIMESTAMP_PATTERN = r'(\d{2}(?::\d{2})+\.(?:\d+))'
METADATA_LINE_PATTERN = r'^\[(\D+):(.*)\]$'
LINE_PATTERN = rf'^(\[{TIMESTAMP_PATTERN}\](?:(v\d+):)?)? ?(.*)$'
WORD_PATTERN = rf'<{TIMESTAMP_PATTERN}>([^<]*)'
BG_PATTERN = r' ?\[bg:(.*?)\]'


def parseLrcLine(
    lineContent: str,
    agent: str | None = None,
    beginTime: int | None = None,
    background: bool = False
) -> Tuple[Line, List[Line]]:
    line: Line = {
        'begin': beginTime,
        'end': None,
        'agent': agent,
        'background': background,
        'content': [],
    }

    bgLines: list[Line] = []
    for bgLine in re.finditer(BG_PATTERN, lineContent):
        bgLineData, _ = parseLrcLine(bgLine.group(1), background=True)
        bgLines.append(bgLineData)
        # lineContent = (lineContent[bgLine.span()[0]:] +
        #                lineContent[:bgLine.span()[1]])
        lineContent = ''.join(lineContent.split(bgLine.group(0)))

    time = 0
    for wordMatch in re.finditer(WORD_PATTERN, lineContent):
        time = deformatTime(wordMatch.group(1))
        if line['content']:
            if not line['content'][-1]['end']:
                line['content'][-1]['end'] = time
        elif not line['begin']:
            line['begin'] = time

        wordText = wordMatch.group(2)
        if not wordText:
            continue

        wordData: Word = {
            'begin': deformatTime(wordMatch.group(1)),
            'end': None,
            'part': not wordText.endswith(' '),
            'text': wordText.removesuffix(' '),
        }
        line['content'].append(wordData)

    if not line['end'] and time:
        line['end'] = time

    # if it's not word by word
    if not line['content']:
        line['content'] = lineContent

    return line, bgLines


def generate(data: Data) -> str:
    lrcContent = ''
    lastLineEnd = 0
    for line in data['lyrics']:
        if data['timing'] == 'None':
            lrcContent += line['content'] + '\n'
            continue

        if lastLineEnd and lastLineEnd != line['begin']:
            lrcContent += f'[{formatLrcTime(lastLineEnd)}]\n'
        lastLineEnd = line['end']

        if not line['background']:
            lrcContent += f'[{formatLrcTime(line["begin"])}]'
            if line['agent']:
                lrcContent += line['agent'] + ':'
        else:
            lrcContent = lrcContent[:-1] + ' [bg:'

        if data['timing'] == 'Line':
            lrcContent += line['content']
        else:
            for word in line['content']:
                wordBegin = f'<{formatLrcTime(word["begin"])}>'
                if not lrcContent.endswith(wordBegin):
                    lrcContent += wordBegin

                lrcContent += word['text']
                if not word['part'] and word != line['content'][-1]:
                    lrcContent += ' '

                lrcContent += f'<{formatLrcTime(word["end"])}>'

            lineEnd = f'<{formatLrcTime(line["end"])}>'
            if not lrcContent.endswith(lineEnd):
                lrcContent += lineEnd

        if line['background']:
            lrcContent += ']'

        lrcContent += '\n'

    if lastLineEnd and lastLineEnd != line['begin']:
        lrcContent += f'[{formatLrcTime(lastLineEnd)}]\n'

    return lrcContent


def parse(content: str) -> Data:
    timing = None
    lines: list[Line] = []
    for lrcLine in content.splitlines():
        if re.match(METADATA_LINE_PATTERN, lrcLine):
            continue

        match = re.match(LINE_PATTERN, lrcLine)
        if not match.group(1):
            if not lines or not lines[-1]['begin']:
                line: Line = {
                    'begin': None,
                    'end': None,
                    'agent': None,
                    'background': None,
                    'content': match.group(4),
                }
                if not timing:
                    timing = 'None'
                lines.append(line)
            continue
        elif timing == 'None':
            raise ParseLyricError('lrc')

        beginTime = deformatTime(match.group(2))
        agent, lineContent = match.group(3, 4)
        line, bgLines = parseLrcLine(
            lineContent=lineContent,
            agent=agent,
            beginTime=beginTime,
        )

        if lines and not lines[-1]['end']:
            lines[-1]['end'] = line['begin']

        if isinstance(line['content'], list):
            lines.append(line)
            if not timing:
                timing = 'Word'
            elif timing != 'Word':
                raise ParseLyricError('lrc')
        elif isinstance(line['content'], str):
            lines.append(line)
            if not timing:
                timing = 'Line'
            elif timing != 'Line':
                raise ParseLyricError('lrc')
        lines.extend(bgLines)

    data: Data = {
        'timing': timing,
        'lyrics': lines,
    }

    return data
