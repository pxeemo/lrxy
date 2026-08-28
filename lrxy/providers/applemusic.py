"""Apple Music API client for fetching richly formatted TTML lyrics.

Provides access to Apple Music's lyric database with support for standard
line-synchronized and word-synchronized (karaoke) lyrics. Processes API
responses into a standardized format compatible with lrxy's lyric embedding
system.

The API requires these metadata fields for successful lookup:
- artist: Primary artist name
- title: Track title
- album: Album title
- duration: Track duration in seconds (as string)

Note: Apple Music offers richer timing information, including word-level
synchronization when available. This provider preserves that detailed timing
data in a structured format.
"""

import json
import logging

import requests
from typing import TypedDict

from .types import MetadataParams, ProviderResponse, LyricData

SEARCH_API = "https://itunes.apple.com/search"
LYRICS_API = "https://lyrics.paxsenix.org/apple-music/lyrics"
logger = logging.getLogger(__name__)


class SearchApiResponse(TypedDict):
    resultCount: int
    results: list[dict[str, str | int]]


def applemusic_api(params: MetadataParams) -> ProviderResponse:
    """Fetch lyrics from Apple Music API using track metadata.

    Makes a GET request to the Apple Music API with provided track
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
        'success': False,
        'error': None,
        'message': None,
        'data': None,
    }
    query = " ".join([params["title"], params["artist"]])

    try:
        response = requests.get(
            SEARCH_API,
            params={'term': query, 'entity': 'song'},
            timeout=10.0,
        )
        response.raise_for_status()
        search_result: SearchApiResponse = response.json()

        if not search_result.get("results"):
            result["error"] = "notfound"
            result["message"] = "No music found for the given track metadata"
            return result

        first_match = search_result["results"][0]
        logger.debug("Search result: %s\n", json.dumps(first_match))
        track_id = int(first_match['trackId'])

        response = requests.get(
            LYRICS_API,
            params={'id': track_id},
            timeout=10.0,
        )
        response.raise_for_status()
        data: dict[str, str] = response.json()
        logger.debug("Track's lyric: %s\n", json.dumps(data))

        has_lyric = bool(data.get('ttmlContent'))
        lyric_data: LyricData = {
            'format': "ttml",
            'timing': None,
            'instrumental': False,
            'hasLyric': has_lyric,
            'lyric': None,
        }

        if has_lyric:
            timing = "Word" if 'itunes:timing="Word"' in data['ttmlContent'] else "Line"
            lyric_data['timing'] = timing
            lyric_data['lyric'] = data['ttmlContent']

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
