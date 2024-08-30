from typing import Union
from pathlib import Path

from mutagen.mp4 import MP4

from .audio import Audio


class Mp4(Audio):
    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path, MP4, ["©ART", "©nam", "©alb"])

    def embed_lyric(self, lyric) -> None:
        self.audio["©lyr"] = lyric
        self.audio.save()
