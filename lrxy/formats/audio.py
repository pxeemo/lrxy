from typing import Union
from pathlib import Path

from lrxy.base_files import BaseFile
from lrxy.exceptions import (
    FileError,
    PathNotExistsError
)


class Audio(BaseFile):
    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path)

        if not self._check_path_exists():
            raise PathNotExistsError(str(self.path))

        if not self._check_is_file():
            raise FileError(str(self.path))

        self.audio = None
        self.extenstion = self.path.suffix

    def get_tags(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def embed_lyric(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")
