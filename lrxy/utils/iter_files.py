from typing import Union, Generator
from pathlib import Path

from lrxy.exceptions import LrxyException
from lrxy.providers import LRCLibAPI
from .audio import load_audio


def iter_files(
    *file_paths: Union[Path, str],
    fetch: bool = True
) -> Generator[dict, None, None]:
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
            file = load_audio(file_path)

        except LrxyException as e:
            yield {"path": file_path, 'success': False, 'data': str(e)}

        else:
            if fetch:
                lrc = LRCLibAPI(file.get_tags())
                yield {"music_obj": file} | lrc  # file -> Mp3 | Flac | M4a
            else:
                yield {"music_obj": file}
