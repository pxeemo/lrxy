"""Musixmatch API client for fetching richly formatted lyrics.

Provides access to Musixmatch's lyric database with support for both
standard line-synchronized and word-synchronized lyrics. Processes
API responses into a standardized format compatible with lrxy's
lyric embedding system.

The API requires these metadata fields for successful lookup:
- artist: Primary artist name
- title: Track title
- album: Album title
- duration: Track duration in seconds (as string)

Note:
    Musixmatch offers richer timing information than LRCLib, including
    word-level synchronization when available. This provider preserves
    that detailed timing data in a structured format.
"""

import os
import json
import logging

import requests

from .utils import MetadataParams, ProviderResponse, LyricData


API: str = "https://api.paxsenix.org/musixmatch/tracks/match/lyrics"
API_TOKEN = os.getenv("PAXSENIX_API_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
logger = logging.getLogger(__name__)


def richsync_parse(richsync) -> list:
    """Parse Musixmatch's richsync format into structured timing data.

    Converts word-level synchronized lyrics into a standardized structure
    with precise timing information for each word and line. This preserves
    the detailed synchronization available in Musixmatch's richsync format.

    Args:
        richsync: Raw richsync data from Musixmatch API response

    Returns: List of line objects with structure:

            ```
            [
                {
                    'begin': int,       # Start time in milliseconds
                    'end': int,         # End time in milliseconds
                    'background': bool, # Whether line is background vocal
                    'agent': None,      # Vocalist (e.g.: "v1")
                    'content': [        # Words in this line
                        {
                            'begin': int,
                            'end': int,
                            'part': str,  # Whether word or syllable
                            'text': str   # Word text
                        },
                        # ...more words
                    ]
                },
                # ...more lines
            ]
            ```

    Example:
        ```python
        >>> rich_data = [{"timestamp": "0", "endtime": "5000", "text": [...]}]
        >>> parsed = richsync_parse(rich_data)
        >>> print(parsed[0]['content'][0]['text'])
        "Verse"
        ```
    """
    lines = []
    for richline in richsync:
        content = []
        for richword in richline["text"]:
            word = {
                "begin": int(richword["timestamp"]),
                "end": int(richword["endtime"]),
                "part": richword["part"],
                "text": richword["text"],
            }
            content.append(word)
        line = {
            "begin": int(richline["timestamp"]),
            "end": int(richline["endtime"]),
            "background": False,
            "agent": None,
            "content": content,
        }
        lines.append(line)
    return lines


def lyric_parse(data) -> list:
    """Parse standard Musixmatch lyrics into structured timing data.

    Converts line-synchronized lyrics into a standardized structure with
    timing information for each line. Calculates end times based on
    the next line's start time for proper playback timing.

    Args:
         Raw lyrics data from Musixmatch API response

    Returns: List of line objects with structure:

            > ```python
            > [
            >     {
            >         'begin': int,         # Start time in milliseconds
            >         'end': int,           # End time in milliseconds
            >         'background': bool,   # Whether line is background vocal
            >         'agent': None,        # Vocalist (e.g.: "v1")
            >         'content': str | list # Line content
            >     },
            >     # ...more lines
            > ]
            > ```

    Example:
        ```python
        >>> lyric_data = [{"time": {"total": 0}, "text": "Line 1"}]
        >>> parsed = lyric_parse(lyric_data)
        >>> print(parsed[0]['content'])
        "Line 1"
        ```
    """
    lines = []
    for lyricline in data:
        begin = int(lyricline["time"]["total"] * 1000)
        line = {
            "begin": begin,
            "end": None,
            "background": False,
            "agent": None,
            "content": lyricline["text"]
        }
        if lines:
            lines[-1]["end"] = begin
        if line["content"]:
            lines.append(line)
    return lines


def musixmatch_api(params: MetadataParams) -> ProviderResponse:
    """Fetch lyrics from Musixmatch API using track metadata.

    Makes a GET request to the Musixmatch API with provided track
    information and processes the response into lrxy's standardized
    format with detailed timing information when available.

    Args: params (MetadataParams): Dictionary containing track metadata with keys:
        artist (str): artist name
        title (str): track title
        album (str): album name
        duration (str): track duration in seconds

    Returns: Standardized APIResponse structure with consistent fields (LyricData):
        success (bool): Indicating overall operation success
        error (str | None): Error category (only when success=False)
        message (str | None): Detailed error description (only when success=False)
        data (LyricData | None): Lyric data dictionary (only when success=True)

    Example:
        ```python
        from lrxy.providers import musixmatch_api

        # Get lyrics using track metadata
        result = musixmatch_api({
            "artist": "Radiohead",
            "title": "No Surprises",
            "album": "OK Computer",
            "duration": "216"
        })

        if result['success']:
            print(f"Lyrics found with {result['data']['timing']} timing")
            # Access the structured lyric data
            lyric_data = json.loads(result['data']['lyric'])
            print(f"First line: {lyric_data['lyrics'][0]['content']}")
        else:
            print(f"Error ({result['error']}): {result['message']}")
        ```
    """
    result: ProviderResponse = {
        "success": False,
        "error": None,
        "message": None,
        "data": None,
    }
    if API_TOKEN:
        logger.debug("Using api token $PAXSENIX_API_TOKEN")
    else:
        logger.warning("API token $PAXSENIX_API_TOKEN not found")

    try:
        response = requests.get(API, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        logger.debug("API response: %s\n", json.dumps(data))
        has_lyric = data["track"]["has_lyrics"]
        if has_lyric:
            # if data["track"]["has_richsync"]:
            #     timing = "Word"
            #     lines = richsync_parse(data["richsync"])
            timing = "Line"
            lines = lyric_parse(data["lyrics"])
            lyric_content = {
                "timing": timing,
                "lyrics": lines,
            }

        lyric_data: LyricData = {
            "format": "json",
            "timing": timing,
            "instrumental": data["track"]["instrumental"],
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
