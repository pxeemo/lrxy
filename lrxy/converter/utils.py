from typing import Literal, TypedDict
import re


class Word(TypedDict):
    begin: int | None
    end: int | None
    part: bool
    text: str


class Line(TypedDict):
    begin: int | None
    end: int | None
    agent: str
    background: bool
    content: str | list[Word]


class Data(TypedDict):
    timing: Literal["Word", "Line", "None"]
    lyrics: list[Line]


def deformat_time(text: str, srt: bool = False) -> int:
    if srt:
        text = text.replace(',', '.')
    if re.match(r'.*\ds$', text):
        text = text.removesuffix("s")
    milis = 0
    times = text.split(':')
    times.reverse()
    for i, time in enumerate(times):
        milis += int(float(time) * 1000) * 60**i
    return milis


def format_time(milis: int, colons: int = 1, srt: bool = False) -> str:
    text = (',' if srt else '.') + f'{milis % 1000:03d}'
    time = milis // 1000
    for i in range(1, colons+2):
        prefix = f'{time % 60**i:02d}'
        if i != 1:
            prefix += ':'
        text = prefix + text
        time //= 60**i
    return text
