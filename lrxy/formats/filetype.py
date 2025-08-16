from typing import Union, List, Dict
from pathlib import Path

from lrxy.exceptions import (
    UnsupportedFileFormatError,
    FileError,
    TagError,
    PathNotExistsError,
)


class BaseFile:
    def __init__(self, path: Union[str, Path],
                 *, match_lrc: bool = False) -> None:
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

        if match_lrc:
            if self.extension not in (".lrc", ".txt"):
                raise UnsupportedFileFormatError(self.extension)


class AudioType(BaseFile):
    def __init__(self, audio,
                 tags_name: List[str]) -> None:
        super().__init__(audio.filename)

        self.audio = audio
        self.artist_name = audio.get(tags_name[0])
        self.track_name = audio.get(tags_name[1])
        self.album = audio.get(tags_name[2])
        self.duration = str(int(audio.info.length))

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
            "This method should be implemented by subclasses.")

    def embed_from_lrc(self, path: Union[str, Path]):
        lrc_file = BaseFile(path, match_lrc=True)

        with open(lrc_file.path) as lrc:
            self.embed_lyric(lrc.read())
