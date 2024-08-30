from typing import Union
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.id3 import USLT

from .audio import Audio


class Mp3(Audio):
    def __init__(self, path: Union[Path, str]):
        super().__init__(path, MP3, ["TPE1", "TIT2", "TALB"])

    def embed_lyric(self, lyric: str) -> None:
        lyric = USLT(encoding=3, desc='', text=lyric)

        self.audio.tags.update_to_v23()
        self.audio.tags.delall('USLT')
        self.audio.tags.delall('SYLT')
        self.audio.tags.add(lyric)

        self.audio.save()
