from typing import Literal, Union, List, Dict
from pathlib import Path

import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from lrxy.exceptions import (
    FileError,
    PathNotExistsError,
    UnsupportedFileFormatError,
    TagError
)


SUPPORTED_FORMATS = [".mp3", ".m4a", ".flac"]


class BaseFile:
    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            self.path = Path(path).expanduser()
        elif isinstance(path, Path):
            self.path = path.expanduser()
        else:
            raise ValueError(
                "The path must be a string or a pathlib.Path object")

        if not self.path.exists():
            raise PathNotExistsError(str(self.path))

        if not self.path.is_file():
            raise FileError(str(self.path))

        self.extension = self.path.suffix

        if self.extension not in SUPPORTED_FORMATS:
            raise UnsupportedFileFormatError(
                self.extension, SUPPORTED_FORMATS
            )

class Audio(BaseFile):
    def __init__(self, path: Union[Path, str],
                 audio_type: Literal[mutagen.flac.FLAC, mutagen.mp4.MP4, mutagen.mp3.MP3],
                 tags_name: List[str]) -> None:
        super().__init__(path)

        self.audio = audio_type(self.path)
        self.artist_name = self.audio.get(tags_name[0])
        self.track_name = self.audio.get(tags_name[1])
        self.album = self.audio.get(tags_name[2])
        self.duration = str(int(self.audio.info.length))

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

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self.path)!r})"

    def __str__(self):
        return str(self.path)

    def get_tags(self) -> Dict[str, str]:
        return {
            "artist_name": self.artist_name,
            "track_name": self.track_name,
            "album_name": self.album,
            "duration": self.duration
        }

    def embed_lyric(self, lyric: str):
        raise NotImplementedError(
            "This method should be implemented by suclasses.")
