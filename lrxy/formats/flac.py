from typing import Union, Dict
from pathlib import Path

from mutagen.flac import FLAC

from .audio import Audio
from lrxy.exceptions import TagError


class Flac(Audio):
    def __init__(self, path: Union[Path, str]):
        super().__init__(path)

        self.audio: FLAC = FLAC(self.path)

        self.artist_name = self.audio.get("artist")
        self.track_name = self.audio.get("title")
        self.album = self.audio.get("album")
        self.direction = int(self.audio.info.length)

        if self.artist_name:
            self.artist_name = self.artist_name[0]
        else:
            raise TagError(str(self.path), "artist")

        if self.track_name:
            self.track_name = self.track_name[0]
        else:
            raise TagError(str(self.path), "track")

        if self.album:
            self.album = self.album[0]
        else:
            raise TagError(str(self.path), "album")

    def get_tags(self) -> Dict[str, str]:
        return {
            "artist_name": self.artist_name,
            "track_name": self.track_name,
            "album": self.album,
            "direction": str(self.direction)
        }

    def embed_lyric(self, lyric: str) -> None:
        self.audio["LYRICS"] = lyric
        self.audio.save()
