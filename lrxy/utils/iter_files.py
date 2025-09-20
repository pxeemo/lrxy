"""Module privides `iter_files` which processes audio files sequentially through
a generator interface, returning standardized results for both successful
processing and error cases. All yielded results maintain identical dictionary
structure regardless of outcome, simplifying batch processing. """

from typing import Union, Generator, TypedDict
from pathlib import Path
import logging

from lrxy.providers import lrclib_api
from lrxy.providers.utils import LyricData
from lrxy.formats import LrxyAudio
from lrxy.exceptions import LrxyException
from .audio import load_audio


logger = logging.getLogger(__name__)


class ResultType(TypedDict):
    """Type of the `iter_files` returning result"""
    success: bool
    path: Path
    music_obj: LrxyAudio | None
    error: str | None
    error_message: str | None
    data: LyricData | None


def iter_files(
    *file_paths: Union[Path, str],
    fetch: bool = True,
    provider=lrclib_api,
) -> Generator[dict, None, None]:
    """Iterate over audio files with consistent result structure and provider
        flexibility.

    Processes audio files sequentially through a generator interface,
    returning standardized results for both successful processing
    and error cases. All yielded results maintain identical dictionary
    structure regardless of outcome, simplifying batch processing.

    Args:
        *file_paths: One or more audio file paths (string or Path objects)
        fetch: Whether to fetch lyrics from provider (default: True)
        provider: Function that takes metadata dict and returns ProviderResponse
            (default: lrclib_api from lrxy.providers)

    Yields: Each result dictionary always contains these keys:
        success (boolean): Indicating overall operation success
        path (Path): Absolute file path
        music_obj (LrxyAudio | None): Audio handler instance if loaded
        error (str | None): Error category if failed
        error_message (str | None): Detailed error description if failed
        data (LyricData | None): Fetched lyric data if available (None when not
            fetched/failed)

    Example:
        ```python
        from lrxy.utils import iter_files

        # Process multiple files with lyric fetching
        for result in iter_files("song1.mp3", "song2.flac"):
            if not result['success']:
                print(f"❌ {result['path']}: {result['error_message']}")
            elif not result['data']:
                print(f"⚠️  {result['music_obj'].title}: No lyrics found")
            else:
                # Extract synced lyrics from provider data
                synced_lyrics = result['data']['lyric']
                result['music_obj'].embed_lyric(synced_lyrics)
                print(f"✅ {result['music_obj'].title}")

        # Process without fetching lyrics (metadata inspection)
        for result in iter_files("song3.m4a", fetch=False):
            if result['success']:
                tags = result['music_obj'].get_tags()
                print(f"Artist: {tags['artist']}")

        # Use custom lyric provider
        from lrxy.providers import musixmatch_api
        for result in iter_files("song.mp3", provider=musixmatch_api):
            if result['success'] and result['hasLyric']:
                # Handle provider-specific data structure
                result['music_obj'].embed_lyric(result['data']['lyric'])
        ```
    """

    for file_path in file_paths:
        result: ResultType = {
            'success': True,
            'path': Path(file_path),
            'music_obj': None,
            'error': None,
            'error_message': None,
            'data': None,
        }

        try:
            audio: LrxyAudio = load_audio(file_path)
            result['music_obj'] = audio

            if fetch:
                params = audio.get_tags()
                logger.debug("Music metadata: %s", params)
                data = provider(params)
                if data['success']:
                    result['data'] = data['data']
                else:
                    result['success'] = False
                    result['error'] = data['error']
                    result['error_message'] = data['message']

        except LrxyException as e:
            result['success'] = False
            result['error'] = str(e)
            result['error_message'] = str(e.message)

        yield result
