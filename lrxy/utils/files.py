from pathlib import Path
from typing import Union, Dict, List, Literal
from lrxy.exceptions import (
    PathNotExistsError,
    FileError,
    DirectoryError,
    UnsupportedFileFormatError,
    FilterFormatError
)
SUPPORTED_FORMATS = [".mp3", ".flac", ".m4a"]


class MusicFiles:

    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            self.path = Path(path).expanduser()
        elif isinstance(path, Path):
            self.path = path.expanduser()
        else:
            raise ValueError(
                "The path must be a string or a pathlib.Path object")

    def _check_path_exists(self) -> bool:
        return self.path.exists()

    def _check_is_file(self) -> bool:
        return self.path.is_file()

    def _check_is_directory(self) -> bool:
        return self.path.is_dir()

    def extrac_music_file(self,
                          ) -> Dict[Path, Literal[*SUPPORTED_FORMATS]]:

        if not self._check_path_exists():
            raise PathNotExistsError(self.path)

        if not self._check_is_file():
            raise FileError(self.path)

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
        pass

        if not self._check_path_exists():
            raise PathNotExistsError(self.path)

        if not self._check_is_directory():
            raise DirectoryError(self.path)

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
