from typing import TypedDict, Union

import requests


API: str = "https://lrclib.net/api/get"


class ReturnData(TypedDict):
    success: bool
    data: Union[dict, str]


def LRCLibAPI(params: dict) -> ReturnData:
    """
        Example:
        >>> lrc = LRCLibAPI(
        ...     {'artist_name': 'System Of A Down',
        ...     'track_name': 'Chop Suey',
        ...     'album_name': 'Toxicity',
        ...     'duration': '208'}
        ... )
        >>> lrc
        {
            "success": true,
            "data": {
                "id": 464567,
                "instrumental": false,
                "plainLyrics": "...",
                "syncedLyrics": "..."
            }
        }
)
    """
    res = requests.get(API, params=params)

    match res.status_code:
        case 200:
            j_data = res.json()
            j_data = dict(
                filter(lambda d: (d[0], d[1]) if d[0] in [
                    "id", "instrumental", "plainLyrics", "syncedLyrics"
                ] else False, res.json().items())
            )
            return {"success": True, "data": j_data}
        case 404:
            return {"success": False, "data": "notfound"}
        case _:
            return {"success": False, "data": res.text}
