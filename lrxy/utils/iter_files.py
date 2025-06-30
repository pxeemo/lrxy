from typing import Union, Generator
from pathlib import Path

from lrxy.formats import Flac, Mp3, Mp4
from lrxy.utils import LRCLibAPI
from lrxy.formats.audio import BaseFile
from lrxy.formats import SUPPORTED_FORMATS
from lrxy.exceptions import (
    LrxyException, UnsupportedFileFormatError)


def iter_files(*file_paths: Union[Path, str]) -> Generator[dict, None, None]:
    """
        Example:
        >>> for music in iter_files("System Of A Down - Chop Suey.mp3",
        ...                         "KoЯn - Twisted Transistor.mp3"):
        ...     if music["success"]:
        ...         music_obj = music["music_obj"]
        ...         synced_lyrics = music["data"]["syncedLyrics"]
        ...         music_obj.embed_lyric(synced_lyrics)
        ...     else:
        ...         print(music["data"], # Error
        ...             music["path"], # Path file
        ...             sep="\\n")
    """
    for file_path in file_paths:
        try:
            file = BaseFile(file_path)

            match file.extension:
                case ".mp3":
                    file = Mp3(file.path)
                case ".flac":
                    file = Flac(file.path)
                case ".mp4":
                    file = Mp4(file.path)

        except LrxyException as e:
            yield {"path": file_path, 'success': False, 'data': str(e)}

        else:
            lrc = LRCLibAPI(file.get_tags())
            yield {"music_obj": file} | lrc  # file -> Mp3 | Flac | Mp4
