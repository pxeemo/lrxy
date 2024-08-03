#!/usr/bin/python

from mutagen.mp4 import MP4


def load_audio(filename: str) -> MP4:
    return MP4(filename)


def load_metadata(audio: MP4) -> dict:
    return {
        "artist_name": audio["©ART"][0],
        "track_name": audio["©nam"][0],
        "album_name": audio["©alb"][0],
        "duration": int(audio.info.length),
    }


def embed_lyric(audio: MP4, lyric_text: str) -> None:
    audio["©lyr"] = lyric_text
    audio.save()
