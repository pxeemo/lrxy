#!/usr/bin/python

from mutagen.id3 import USLT
from mutagen.mp3 import MP3


def load_audio(filename: str) -> MP3:
    return MP3(filename)


def load_metadata(audio: MP3) -> dict:
    return {
        "artist_name": audio["TPE1"].text[0],
        "track_name": audio["TIT2"].text[0],
        "album_name": audio["TALB"].text[0],
        "duration": int(audio.info.length),
    }


def embed_lyric(audio: MP3, lyric_text: str) -> None:
    lyric = USLT(encoding=3, desc='', text=lyric_text)

    audio.tags.update_to_v23()
    audio.tags.delall('USLT')
    audio.tags.delall('SYLT')
    audio.tags.add(lyric)

    audio.save()

