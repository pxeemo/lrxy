from typing import Union
from pathlib import Path

from .filetype import AudioType


class LrxyMP4(AudioType):
    """
        Example:
        >>> m4a_music = M4a("System Of A Down - Chop Suey.m4a")
        >>> m4a_music.track_name
        Chop Suey
        >>> m4a_music.get_tags()
        {
            'artist_name': 'System Of A Down',
            'track_name': 'Chop Suey',
            'album_name': 'Toxicity',
            'duration': '208'
        }
        >>> with open("lyric.txt") as f:
        ...     m4a_music.embed_lyric(f.read())

    """

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path, ["©ART", "©nam", "©alb"])

    def embed_lyric(self, lyric) -> None:
        self.audio["©lyr"] = lyric
        self.audio.save()
