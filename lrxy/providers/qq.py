import os
import json
import logging
import re

import requests

from .utils import MetadataParams, ProviderResponse, LyricData


API: str = "https://lyrics.paxsenix.org/qq/lyrics-metadata"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
}
logger = logging.getLogger(__name__)


def parse_paxline(paxline, isbg: bool, opposite_turn: bool | None = None):
    if opposite_turn is None:
        opposite_turn = paxline["oppositeTurn"]
    line = {
        "begin": paxline["timestamp"],
        "end": paxline["endtime"],
        "background": isbg,
        "agent": "v2" if opposite_turn else "v1",
        "content": []
    }
    for lyricword in paxline["text"]:
        word = {
            "begin": lyricword["timestamp"],
            "end": lyricword["endtime"],
            "part": lyricword["part"],
            "text": lyricword["text"],
        }
        line["content"].append(word)
    return line


def lyric_parse(data) -> list:
    lines = []
    for lyricline in data:
        lines.append(parse_paxline(lyricline, isbg=False))
        if lyricline["background"]:
            lines.append(parse_paxline(
                lyricline["backgroundText"],
                isbg=True,
                opposite_turn=lyricline["oppositeTurn"],
            ))
    return lines


def qq_api(params: MetadataParams) -> ProviderResponse:
    result: ProviderResponse = {
        "success": False,
        "error": None,
        "message": None,
        "data": None,
    }
    try:
        req_data = {
            "title": params["title"],
            "artist": re.split(r" ?[,&] ?", params["artist"]),
            "album": params["album"],
            "duration": int(params["duration"]),
        }
        logger.debug("Request data: %s", json.dumps(req_data))
        response = requests.post(API, json=req_data, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        logger.debug("API response: %s\n", json.dumps(data))
        has_lyric = bool(data.get("lyrics"))
        timing = None
        if has_lyric:
            timing = "Word"
            lines = lyric_parse(data["lyrics"])
            lyric_content = {
                "timing": timing,
                "lyrics": lines,
            }

        lyric_data: LyricData = {
            "format": "json",
            "timing": timing,
            "instrumental": None,
            "hasLyric": has_lyric,
            "lyric": json.dumps(lyric_content) if has_lyric else None,
        }

        result["success"] = True
        result["data"] = lyric_data

    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 404:
            result["error"] = "notfound"
            result["message"] = "No music found for the given track metadata"
        else:
            result["error"] = "network"
            result["message"] = f"Failed to fetch: {e}"

    return result
