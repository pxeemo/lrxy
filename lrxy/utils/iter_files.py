from typing import Union, Generator
from pathlib import Path

from lrxy.formats import Flac, Mp3, M4a
from lrxy.utils import LRCLibAPI
from lrxy.formats.audio import BaseFile
from lrxy.exceptions import LrxyException


def iter_files(*file_paths: Union[Path, str]) -> Generator[dict, None, None]:
    """
        Example:
        >>> for music in iter_files("song1.mp3", "song2.flac"):
        ...     if music["success"]:
        ...         music_obj = music["music_obj"]
        ...         synced_lyrics = music["data"]["syncedLyrics"]
        ...         music_obj.embed_lyric(synced_lyrics)
        ...     else:
        ...         print(music["data"],  # Error details
        ...               music["path"],  # File path
        ...               sep="\\n")
    """
    for file_path in file_paths:
        try:
            file = BaseFile(file_path)

            match file.extension:
                case ".mp3":
                    file = Mp3(file.path)
                case ".flac":
                    file = Flac(file.path)
                case ".m4a":
                    file = M4a(file.path)

        except LrxyException as e:
            yield {"path": file_path, 'success': False, 'data': str(e)}

        else:
            lrc = LRCLibAPI(file.get_tags())
            yield {"music_obj": file} | lrc  # file -> Mp3 | Flac | M4a
