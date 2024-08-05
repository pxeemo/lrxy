from pathlib import Path
from typing import Union, Dict, List, Literal


SUPPORTED_FORMATS = [".mp3", ".flac", ".m4a"]


class MusicFiles:

    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            self.path = Path(path).expanduser()
        elif isinstance(path, Path):
            self.path = path.expanduser()
        else:
            raise  # TODO

    def _check_path_exists(self) -> bool:
        return self.path.exists()

    def _check_is_file(self) -> bool:
        return self.path.is_file()

    def _file_extension(self) -> str:
        return self.path.suffix

    def extract_music_files(
            self,
            filter_format: List[Literal[*SUPPORTED_FORMATS]
                                ] = SUPPORTED_FORMATS
    ) -> Dict[Path, Literal[*SUPPORTED_FORMATS]]:
        if not self._check_path_exists():
            raise  # TODO

        if filter_format != SUPPORTED_FORMATS:
            check_formats = [
                frt for frt in filter_format if frt in SUPPORTED_FORMATS]
            if len(check_formats) != len(filter_format):
                raise  # TODO

        if self._check_is_file():
            file_extension = self._file_extension()
            if file_extension in SUPPORTED_FORMATS:
                return {self.path: file_extension}
            else:
                raise  # TODO
        else:
            result_musics = {}
            for s_format in SUPPORTED_FORMATS:
                for path in self.path.glob(f"*{s_format}"):
                    result_musics.update({path: s_format})
            if result_musics:
                return result_musics
            else:
                raise  # TODO
