import requests

import json
import logging

from .utils import ProviderResponse, LyricData

API = "https://api.paxsenix.dpdns.org/"
SEARCH_API = f"{API}/apple-music/search"
LYRICS_API = f"{API}/lyrics/applemusic"
logger = logging.getLogger(__name__)


def applemusic_api(params: dict) -> ProviderResponse:
    result: ProviderResponse = {
        'success': False,
        'error': None,
        'message': None,
        'data': None,
    }
    query = " ".join([params["title"], params["artist"]])

    try:
        response = requests.get(SEARCH_API, params={'q': query}, timeout=10.0)
        searchResult = response.json()
        first_match = searchResult["results"][0]
        logger.debug("Search result: %s\n", first_match)

        trackId = first_match['playParams']['id']
        hasLyric = first_match["hasTimeSyncedLyrics"]
        if hasLyric:
            response = requests.get(LYRICS_API, params={'id': trackId}, timeout=10.0)
            data = response.json()
            logger.debug("Track's lyric: %s\n", data)
            lyricData: LyricData = {
                'format': "ttml",
                'timing': data["type"],
                'instrumental': False,
                'lyric': data["ttml_content"],
            }

            result["success"] = True
            result["data"] = lyricData

    except requests.exceptions.RequestException as e:
        result["error"] = "network"
        result["message"] = f"Network error: {str(e)}"

    return result
