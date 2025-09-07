"""Iterate over audio files with consistent result structure and provider flexibility.

Processes audio files sequentially through a generator interface,
returning standardized results for both successful processing
and error cases. All yielded results maintain identical dictionary
structure regardless of outcome, simplifying batch processing.

Each result dictionary always contains these keys:
- success: Boolean indicating overall operation success
- path: Absolute file path (Path object)
- music_obj: Audio handler instance if loaded (None on failure)
- error: Error category if failed (None on success)
- error_message: Detailed error description if failed (None on success)
- data: Fetched lyric data if available (None when not fetched/failed)

Args:
    *file_paths: One or more audio file paths (string or Path objects)
    fetch: Whether to fetch lyrics from provider (default: True)
    provider: Function that takes metadata dict and returns ProviderResponse
        (default: lrclib_api from lrxy.providers)

Yields:
    dict: Processing result with consistent structure for all cases

    Success case (fetch=True, lyrics found):
        {
            'success': True,
            'path': Path('/path/to/song.mp3'),
            'music_obj': LrxyID3('/path/to/song.mp3'),
            'error': None,
            'error_message': None,
            'data': {  # Raw data from provider
                'id': 123,
                'instrumental': False,
                'plainLyrics': 'Verse 1\\nThis is a line...',
                'syncedLyrics': '...'
            }
        }

    Success case (fetch=True, no lyrics found):
        {
            'success': False,
            'path': Path('/path/to/song.mp3'),
            'music_obj': LrxyID3('/path/to/song.mp3'),
            'error': 'notfound',
            'error_message': 'No lyrics found for the given track metadata',
            'data': None
        }

    Success case (fetch=False):
        {
            'success': True,
            'path': Path('/path/to/song.mp3'),
            'music_obj': LrxyID3('/path/to/song.mp3'),
            'error': None,
            'error_message': None,
            'data': None
        }

    Error case (file loading failure):
        {
            'success': False,
            'path': Path('/path/to/invalid.mp3'),
            'music_obj': None,
            'error': 'File format not supported',
            'error_message': None,
            'data': None
        }

Example:
    >>> from lrxy.utils import iter_files
    >>>
    >>> # Process multiple files with lyric fetching
    >>> for result in iter_files("song1.mp3", "song2.flac"):
    ...     if not result['success']:
    ...         print(f"❌ {result['path'].name}: {result['error_message']}")
    ...     elif not result['data']:
    ...         print(f"⚠️  {result['music_obj'].track_name}: No lyrics found")
    ...     else:
    ...         # Extract plain lyrics from provider data
    ...         plain_lyrics = result['data']['plainLyrics']
    ...         result['music_obj'].embed_lyric(plain_lyrics)
    ...         print(f"✅ {result['music_obj'].track_name}")
    >>>
    >>> # Process without fetching lyrics (metadata inspection)
    >>> for result in iter_files("song3.m4a", fetch=False):
    ...     if result['success']:
    ...         tags = result['music_obj'].get_tags()
    ...         print(f"Artist: {tags['artist_name']}")
    >>>
    >>> # Use custom lyric provider
    >>> from lrxy.providers import musixmatch_api
    >>> for result in iter_files("song.mp3", provider=musixmatch_api):
    ...     if result['success'] and result['data']:
    ...         # Handle provider-specific data structure
    ...         result['music_obj'].embed_lyric(result['data']['plainLyrics'])
"""

from typing import Union, Generator
from pathlib import Path
import logging

from lrxy.exceptions import LrxyException
from lrxy.providers import lrclib_api
from .audio import load_audio


logger = logging.getLogger(__name__)


def iter_files(
    *file_paths: Union[Path, str],
    fetch: bool = True,
    provider=lrclib_api,
) -> Generator[dict, None, None]:
    for file_path in file_paths:
        result = {
            'success': True,
            'path': Path(file_path),
            'music_obj': None,
            'error': None,
            'error_message': None,
            'data': None,
        }

        try:
            audio = load_audio(file_path)
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

        yield result
