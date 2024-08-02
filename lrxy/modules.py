from typing import Literal, Optional, TypedDict
from colorama import Fore
import os
import requests
import json


class FetchDataReturnType(TypedDict):
    success: bool
    data: Optional[dict]
    message: Optional[str]


class GetFileTypeReturnType(TypedDict):
    success: bool
    format: Optional[str]
    message: Optional[str]


def get_filetype(audio_file: str) -> GetFileTypeReturnType:
    _, file_extension = os.path.splitext(audio_file)
    if os.path.exists(audio_file):
        if file_extension in ('.mp3', '.flac'):
            return {
                "success": True,
                "format": file_extension[1:],
                "message": None
            }
        else:
            return {
                "success": False,
                "format": file_extension,
                "message": f"{Fore.RED}Error: {Fore.RESET}Unsupported file format '{file_extension}': {Fore.CYAN}{audio_file}{Fore.RESET}\n       Only '.mp3' and '.flac' are supported."
            }
    else:
        return {
            "success": False,
            "format": file_extension,
            "message": f"{Fore.RED}Error: {Fore.RESET}File not found: {Fore.CYAN}{audio_file}{Fore.RESET}"
        }


def fetch_lyric_data(params: dict, audio_file: str) -> FetchDataReturnType:
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
                    "message": f"{Fore.RED}Error: {Fore.RESET}Couldn't find music: {Fore.CYAN}{audio_file}{Fore.RESET}\n       Try to change music's tags."
                }
            case _:
                return {"success": False, "data": None, "message": data.message}


def get_lyric(
    data: dict,
    default_lyric: Literal["auto", "plain_lyric", "synced_lyric"] = "auto"
) -> Optional[str]:

    plain_lyric = data.get("plainLyrics")
    synced_lyric = data.get("syncedLyrics")

    option_lyric = {
        "auto": synced_lyric or plain_lyric,
        "synced_lyric": synced_lyric,
        "plain_lyric": plain_lyric
    }

    return option_lyric.get(default_lyric, None)
