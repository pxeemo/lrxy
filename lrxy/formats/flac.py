from typing import Union
from pathlib import Path

from mutagen.flac import FLAC

from .audio import Audio


class Flac(Audio):
    """
        Example:
        >>> flac_music = Mp3("System Of A Down - Chop Suey.flac")
        >>> flac_music.track_name
        Chop Suey
        >>> flac_music.get_tags()
        {
            'artist_name': 'System Of A Down',
            'track_name': 'Chop Suey',
            'album_name': 'Toxicity',
            'duration': '208'
        }
        >>> with open("lyric.txt") as f:
        ...     flac_music.embed_lyric(f.read())

    """
    def __init__(self, path: Union[Path, str]):
        super().__init__(path,
                         FLAC, ["artist", "title", "album"])

    def embed_lyric(self, lyric: str) -> None:
        self.audio["LYRICS"] = lyric
        self.audio.save()
