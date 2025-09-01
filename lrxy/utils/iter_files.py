"""Iterate over audio files with consistent result structure.

Processes audio files sequentially through a generator interface,
returning standardized results for both successful processing
and error cases. All yielded results maintain identical dictionary
structure regardless of outcome, simplifying batch processing.

Each result dictionary always contains these keys:
- path: Absolute file path (Path object)
- success: Boolean indicating operation success
- error: Error message if failed (None on success)
- music_obj: Audio handler instance if loaded (None on failure)
- lyrics: Fetched lyrics if available (None when not fetched/failed)
- provider_data: Raw provider response if fetched (None when not fetched/failed)

Args:
    *file_paths: One or more audio file paths (string or Path objects)
    fetch: Whether to fetch lyrics from LRCLib (default: True)

Yields:
    dict: Processing result with consistent structure for all cases

    Success case (fetch=True):
        {
            'path': Path('/path/to/song.mp3'),
            'success': True,
            'error': None,
            'music_obj': LrxyID3('/path/to/song.mp3'),
            'lyrics': 'Verse 1\\nThis is a line...',
            'provider_data': {'lyrics': '...', 'synced': False, ...}
        }

    Success case (fetch=False):
        {
            'path': Path('/path/to/song.mp3'),
            'success': True,
            'error': None,
            'music_obj': LrxyID3('/path/to/song.mp3'),
            'lyrics': None,
            'provider_data': None
        }

    Error case:
        {
            'path': Path('/path/to/invalid.mp3'),
            'success': False,
            'error': 'File format not supported',
            'music_obj': None,
            'lyrics': None,
            'provider_data': None
        }

Example:
    >>> from lrxy.utils import iter_files
    >>>
    >>> # Process multiple files with lyric fetching
    >>> for result in iter_files("song1.mp3", "song2.flac"):
    ...     if not result['success']:
    ...         print(f"❌ {result['path'].name}: {result['error']}")
    ...     elif result['data']['instrumental']:
    ...         print(f"⚠️  {result['music_obj'].track_name}: No lyrics found")
    ...     else:
    ...         result['music_obj'].embed_lyric(result['data']['syncedLyrics'])
    ...         print(f"✅ {result['music_obj'].track_name}")
    >>>
    >>> # Process without fetching lyrics (metadata inspection)
    >>> for result in iter_files("song3.m4a", fetch=False):
    ...     if result['success']:
    ...         tags = result['music_obj'].get_tags()
    ...         print(f"Artist: {tags['artist_name']}")
"""

from typing import Union, Generator
from pathlib import Path

from lrxy.exceptions import LrxyException
from lrxy.providers import lrclib_api
from .audio import load_audio


def iter_files(
    *file_paths: Union[Path, str],
    fetch: bool = True,
    provider=lrclib_api,
) -> Generator[dict, None, None]:
    for file_path in file_paths:
        result = {
            'path': Path(file_path),
            'success': True,
            'error': None,
            'error_message': None,
            'music_obj': None,
            'data': None,
        }

        try:
            audio = load_audio(file_path)
            result['music_obj'] = audio

            if fetch:
                lrc = provider(audio.get_tags())
                if lrc['success']:
                    result['data'] = lrc['data']
                else:
                    result['success'] = False
                    result['error'] = lrc['error']
                    result['error_message'] = lrc['message']

        except LrxyException as e:
            result['success'] = False
            result['error'] = str(e)

        yield result
