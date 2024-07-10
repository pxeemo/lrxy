#!/usr/bin/python

from mutagen.id3 import USLT
from mutagen.flac import FLAC


def load_audio(filename: str) -> FLAC:
    return FLAC(filename)


def load_metadata(audio: FLAC) -> dict:
    return {
        "artist_name": audio["artist"][0],
        "track_name": audio["title"][0],
        "album_name": audio["album"][0],
        "duration": int(audio.info.length),
    }


def embed_lyric(audio: FLAC, lyric_text: str) -> None:
    audio["LYRICS"] = lyric_text
    audio.save()

