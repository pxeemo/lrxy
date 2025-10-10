"""Custom typed dictionaries and API utilities used for providers"""

from typing import TypedDict, Literal


class LyricData(TypedDict):
    format: str
    timing: Literal["Word", "Line", "None"] | None
    instrumental: bool
    lyric: str | dict | None


class MetadataParams(TypedDict):
    artist: str
    title: str
    album: str
    duration: str


class ProviderResponse(TypedDict):
    success: bool
    error: Literal["notfound", "network", "api", "nolyric"] | None
    message: str | None
    data: LyricData | None
