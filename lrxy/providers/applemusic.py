import os
import json
import logging

import requests

from .utils import ProviderResponse, LyricData

API = "https://api.paxsenix.dpdns.org/"
SEARCH_API = f"{API}/apple-music/search"
LYRICS_API = f"{API}/lyrics/applemusic"
API_TOKEN = os.getenv("PAXSENIX_API_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
logger = logging.getLogger(__name__)


def applemusic_api(params: dict) -> ProviderResponse:
    result: ProviderResponse = {
        'success': False,
        'error': None,
        'message': None,
        'data': None,
    }
    query = " ".join([params["title"], params["artist"]])
    if API_TOKEN:
        logger.debug("Using api token $PAXSENIX_API_TOKEN")
    else:
        logger.warn("API token $PAXSENIX_API_TOKEN not found")

    try:
        response = requests.get(
            SEARCH_API,
            headers=HEADERS,
            params={'q': query},
            timeout=10.0,
        )
        response.raise_for_status()
        searchResult = response.json()
        first_match = searchResult["results"][0]
        logger.debug("Search result: %s\n", json.dumps(first_match))
        trackId = first_match['playParams']['id']
        hasLyric = first_match["hasTimeSyncedLyrics"]
        if hasLyric:
            response = requests.get(
                LYRICS_API,
                headers=HEADERS,
                params={'id': trackId},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            logger.debug("Track's lyric: %s\n", json.dumps(data))
            lyricData: LyricData = {
                'format': "ttml",
                'timing': data["type"],
                'instrumental': False,
                'lyric': data["ttml_content"],
            }

            result["success"] = True
            result["data"] = lyricData

    except requests.exceptions.RequestException as e:
        if e.response.status_code == 404:
            result["error"] = "notfound"
            result["message"] = "No music found for the given track metadata"
        else:
            result["error"] = "network"
            result["message"] = f"Failed to fetch: {e}"

    return result
