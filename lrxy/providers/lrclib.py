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

from typing import TypedDict, Literal, Optional

import requests


API: str = "https://lrclib.net/api/get"


class LyricData(TypedDict):
    """Structure for successful lyric data from LRCLib."""
    id: int
    instrumental: bool
    plainLyrics: str | None
    syncedLyrics: str | None
    provider: str
    format: str


class Result(TypedDict):
    success: bool
    data: LyricData | None
    error: str | None
    message: str | None


class APIResponse(TypedDict):
    """Standardized response structure for all LRCLib API interactions.

    Provides consistent shape regardless of outcome, with clear separation
    of success and error states through designated fields.

    Example:
        Success: {
            'success': True,
            'data': {'id': 123, 'instrumental': False, ...},
            'error': None,
            'message': None
        }
        Error: {
            'success': False,
            'data': None,
            'error': 'notfound',
            'message': 'No lyrics found for the given track metadata'
        }
    """
    success: bool
    data: Optional[LyricData]  # Present only on success
    error: Optional[Literal["notfound", "network", "api"]]  # Error category
    message: Optional[str]  # Human-readable error description


def lrclib_api(params: dict) -> APIResponse:
    """Fetch lyrics from LRCLib API using track metadata.

    Makes a GET request to LRCLib.net with provided track information
    and processes the response into a standardized format with clear
    error categorization.

    Args:
        params: Dictionary containing track metadata with keys:
            - artist_name: Primary artist name
            - track_name: Track title
            - album_name: Album title
            - duration: Track duration in seconds (as string)

    Returns:
        Standardized APIResponse structure with consistent fields:
        - success: Boolean indicating overall operation success
        - data: Lyric data dictionary (only when success=True)
        - error: Error category (only when success=False)
        - message: Detailed error description (only when success=False)

    Example:
        >>> from lrxy.providers.lrclib import lrclib_api
        >>>
        >>> result = lrclib_api({
        ...     "artist_name": "Radiohead",
        ...     "track_name": "No Surprises",
        ...     "album_name": "OK Computer",
        ...     "duration": "216"
        ... })
        >>>
        >>> if result['success']:
        ...     print(f"Lyrics found: {len(result['data']['plainLyrics'])} chars")
        ...     audio.embed_lyric(result['data']['plainLyrics'])
        ... else:
        ...     if result['error'] == 'notfound':
        ...         print("No matching lyrics found")
        ...     else:
        ...         print(f"Error ({result['error']}): {result['message']}")
    """
    try:
        # Add timeout to prevent hanging requests
        res = requests.get(API, params=params, timeout=10.0)
        result: Result = {
            "success": False,
            "data": None,
            "error": None,
            "message": None
        }

        match res.status_code:
            case 200:
                try:
                    api_data = res.json()
                    # Extract only the fields we care about
                    lyric_data: LyricData = {
                        "id": api_data["id"],
                        "instrumental": api_data["instrumental"],
                        "plainLyrics": api_data.get("plainLyrics"),
                        "syncedLyrics": api_data.get("syncedLyrics"),
                        "provider": "lrclib",
                        "format": "lrc",
                    }
                    result["success"] = True
                    result["data"] = lyric_data

                except (KeyError, TypeError) as e:
                    result["error"] = "api"
                    result["message"] = f"Invalid API response structure: {str(e)}"

            case 404:
                result["error"] = "notfound"
                result["message"] = "No music found for the given track metadata"

            case _:
                result["error"] = "api"
                result["message"] = f"API error {res.status_code}: {res.text}"

    except requests.exceptions.RequestException as e:
        result["error"] = "network"
        result["message"] = f"Network error: {str(e)}"

    return result
