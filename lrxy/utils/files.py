from pathlib import Path
from typing import Union, Dict, List, Literal
from lrxy.base_files import BaseFile
from lrxy.exceptions import (
    PathNotExistsError,
    FileError,
    DirectoryError,
    UnsupportedFileFormatError,
    FilterFormatError
)
SUPPORTED_FORMATS = [".mp3", ".flac", ".m4a"]


class MusicFiles(BaseFile):
    def __init__(self, path: Union[str, Path]) -> None:
        super().__init__(path)

    def extrac_music_file(self,
                          ) -> Dict[Path, Literal[*SUPPORTED_FORMATS]]:

        if not self._check_path_exists():
            raise PathNotExistsError(str(self.path))

        if not self._check_is_file():
            raise FileError(str(self.path))

        file_extension = self.path.suffix
        if file_extension in SUPPORTED_FORMATS:
            return {self.path: file_extension}
        else:
            raise UnsupportedFileFormatError(
                file_extension, SUPPORTED_FORMATS)

    def extract_music_files(
            self,
            filter_format: List[Literal[*SUPPORTED_FORMATS]
                                ] = SUPPORTED_FORMATS
    ) -> Dict[Path, Literal[*SUPPORTED_FORMATS]]:

        if not self._check_path_exists():
            raise PathNotExistsError(str(self.path))

        if not self._check_is_directory():
            raise DirectoryError([self.path])

        if filter_format != SUPPORTED_FORMATS:
            unsupported_formats = [
                frt for frt in filter_format if frt not in SUPPORTED_FORMATS]
            if len(unsupported_formats):
                raise FilterFormatError(
                    unsupported_formats, SUPPORTED_FORMATS)

        result_musics = {}
        for frt in filter_format:
            for music in self.path.glob(f"*{frt}"):
                result_musics.update({music: frt})

        return result_musics
