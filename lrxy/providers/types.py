from typing import TypedDict, Literal


class LyricData(TypedDict):
    format: str
    timing: Literal["Word", "Line", "None"] | None
    instrumental: bool
    lyrics: str | dict | None


class ProviderResponse(TypedDict):
    success: bool
    data: LyricData | None
    error: Literal["notfound", "network", "api", "unknown"] | None
    message: str | None
    provider: str
