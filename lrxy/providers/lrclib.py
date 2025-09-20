"""LRCLib API client for fetching song lyrics with consistent response structure.

Provides a clean interface to the LRCLib.net API with standardized response
formatting for all possible outcomes. Handles API response parsing and error
conditions with clear categorization of failure types.

The API requires these metadata fields for successful lookup:
- artist_name
- track_name
- album_name
- duration (in seconds)

Note:
    LRCLib uses duration matching as part of its search algorithm,
    so accurate duration is critical for finding the correct lyrics.
"""

import logging
import json

import requests

from .utils import MetadataParams, ProviderResponse, LyricData


API: str = "https://lrclib.net/api/get"
logger = logging.getLogger(__name__)


def lrclib_api(params: MetadataParams) -> ProviderResponse:
    """Fetch lyrics from LRCLib API using track metadata.

    Makes a GET request to LRCLib.net with provided track information
    and processes the response into a standardized format with clear
    error categorization.

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
        from lrxy.providers import lrclib_api

        result = lrclib_api({
            "artist": "Radiohead",
            "title": "No Surprises",
            "album": "OK Computer",
            "duration": "216"
        })

        if result['success']:
            print(f"Lyrics found.")
            audio.embed_lyric(result['data']['lyric'])
        else:
            if result['error'] == 'notfound':
                print("No matching lyrics found")
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

    try:
        # Add timeout to prevent hanging requests
        retake_params = {
            "track_name": params["title"],
            "artist_name": params["artist"],
            "album_name": params["album"],
            "duration": params["duration"],
        }
        response = requests.get(API, params=retake_params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        logger.debug("API response: %s\n", json.dumps(data))
        lyric_data: LyricData = {
            "format": "lrc",
            "timing": None,
            "instrumental": data["instrumental"],
            "hasLyric": bool(data["syncedLyrics"]),
            "lyric": data["syncedLyrics"],
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
