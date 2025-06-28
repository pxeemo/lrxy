from typing import Union
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.id3 import USLT

from .audio import Audio


class Mp3(Audio):
    """
        Example:
        >>> mp3_music = Mp3("System Of A Down - Chop Suey.mp3")
        >>> mp3_music.track_name
        Chop Suey
        >>> mp3_music.get_tags()
        {
            'artist_name': 'System Of A Down',
            'track_name': 'Chop Suey',
            'album_name': 'Toxicity',
            'duration': '208'
        }
        >>> with open("lyric.txt") as f:
        ...     mp3_music.embed_lyric(f.read())

    """
    def __init__(self, path: Union[Path, str]):
        super().__init__(path, MP3, ["TPE1", "TIT2", "TALB"])

    def embed_lyric(self, lyric: str) -> None:
        lyric = USLT(encoding=3, desc='', text=lyric)

        self.audio.tags.update_to_v23()
        self.audio.tags.delall('USLT')
        self.audio.tags.delall('SYLT')
        self.audio.tags.add(lyric)

        self.audio.save()
