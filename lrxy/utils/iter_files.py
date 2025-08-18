from typing import Union, Generator
from pathlib import Path

from lrxy.exceptions import LrxyException
from lrxy.providers import LRCLibAPI
from .audio import load_audio


def iter_files(
    *file_paths: Union[Path, str],
    fetch: bool = True
) -> Generator[dict, None, None]:
    for file_path in file_paths:
        result = {
            'path': Path(file_path),
            'success': True,
            'error': None,
            'music_obj': None,
            'lyrics': None,
            'provider_data': None,
        }

        try:
            audio = load_audio(file_path)
            result['music_obj'] = audio

            if fetch:
                lrc = LRCLibAPI(audio.get_tags())
                result['provider_data'] = lrc

        except LrxyException as e:
            result['success'] = False
            result['error'] = str(e)

        yield result
