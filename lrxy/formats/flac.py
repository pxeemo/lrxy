from typing import Union
from pathlib import Path

from mutagen.flac import FLAC

from .audio import Audio


class Flac(Audio):
    def __init__(self, path: Union[Path, str]):
        super().__init__(path,
                         FLAC, ["artist", "title", "album"])

    def embed_lyric(self, lyric: str) -> None:
        self.audio["LYRICS"] = lyric
        self.audio.save()
