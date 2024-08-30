from typing import Literal, Union, List, Dict
from pathlib import Path

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from lrxy.base_files import BaseFile
from lrxy.exceptions import (
    FileError,
    PathNotExistsError,
    UnsupportedFileFormatError,
    TagError
)

SUPPORTED_FORMATS = [".mp3", ".mp4", ".flac"]


class Audio(BaseFile):
    def __init__(self, path: Union[Path, str],
                 audio_type: Literal[FLAC, MP4, MP3],
                 tags_name: List[str]) -> None:
        super().__init__(path)

        if not self._check_path_exists():
            raise PathNotExistsError(str(self.path))

        if not self._check_is_file():
            raise FileError(str(self.path))

        if self.extension not in SUPPORTED_FORMATS:
            raise UnsupportedFileFormatError(
                self.extension, SUPPORTED_FORMATS
            )

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
