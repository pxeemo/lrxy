from typing import Union
from pathlib import Path

from mutagen.mp4 import MP4

from .audio import Audio


class Mp4(Audio):
    """
        Example:
        >>> mp4_music = Mp4("System Of A Down - Chop Suey.m4a")
        >>> mp4_music.track_name
        Chop Suey
        >>> mp4_music.get_tags()
        {
            'artist_name': 'System Of A Down',
            'track_name': 'Chop Suey',
            'album_name': 'Toxicity',
            'duration': '208'
        }
        >>> with open("lyric.txt") as f:
        ...     mp4_music.embed_lyric(f.read())

    """
    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path, MP4, ["©ART", "©nam", "©alb"])

    def embed_lyric(self, lyric) -> None:
        self.audio["©lyr"] = lyric
        self.audio.save()
