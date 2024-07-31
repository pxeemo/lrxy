from typing import Literal, Optional, TypedDict
import os
import requests
import json



class FetchDataReturnType(TypedDict):
    success: bool
    data: Optional[dict]
    message: Optional[str]


def get_filetype(audio_file: str) -> str:
    if os.path.exists(audio_file):
        _, file_extension = os.path.splitext(audio_file)
        if file_extension in ('.mp3', '.flac'):
            return file_extension[1:]
        else:
            raise TypeError(
                "Unsupported file format, only supported '.mp3' and '.flac'"
            )
    else:
        raise FileNotFoundError(f"file '{audio_file}' not found")


def fetch_lyric_data(params: dict) -> FetchDataReturnType:
    URL = "https://lrclib.net/api/get"
    try:
        response = requests.get(URL, params=params)
    except Exception as error:
        return {"success": False, "data": None, "message": str(error)}
    else:
        data = json.loads(response.text)

        match response.status_code:
            case 200:
                return {"success": True, "data": data, "message": None}
            case 404:
                return {
                    "success": False,
                    "data": None,
                    "message": "Couldn't find this music. Try to change music tags."
                }
            case _:
                return {"success": False, "data": None, "message": data.message}


def get_lyric(
        data: dict,
        default_lyric: Literal["auto", "plain_lyric", "synced_lyric"]
    ) -> Optional[str]:

    plain_lyric = data.get("plainLyrics")
    synced_lyric = data.get("syncedLyrics")

    match default_lyric:
        case "auto":
            if synced_lyric:
                return synced_lyric
            elif plain_lyric:
                return plain_lyric
            else:
                return None
        case "plain_lyric":
            if plain_lyric:
                return plain_lyric
            else:
                return None
        case "synced_lyric":
            if synced_lyric:
                return synced_lyric
            else:
                return None

