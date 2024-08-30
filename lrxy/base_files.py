from typing import Union
from pathlib import Path


class BaseFile:
    def __init__(self, path: Union[str, Path]) -> None:
        if isinstance(path, str):
            self.path = Path(path).expanduser()
        elif isinstance(path, Path):
            self.path = path.expanduser()
        else:
            raise ValueError(
                "The path must be a string or a pathlib.Path object")

        self.extension = self.path.suffix

    def _check_path_exists(self) -> bool:
        return self.path.exists()

    def _check_is_file(self) -> bool:
        return self.path.is_file()

    def _check_is_directory(self) -> bool:
        return self.path.is_dir()
