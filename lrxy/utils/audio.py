"""Factory module for loading audio files with lyric embedding capabilities.

Provides a unified interface to handle different audio formats through
format-specific lyric handlers. Automatically detects file type and
returns the appropriate handler class for embedding unsynchronized lyrics.
"""

from pathlib import Path
from typing import Union

from mutagen import File
from mutagen._vorbis import VComment
from mutagen.id3 import ID3
from mutagen.mp4 import MP4Tags

from lrxy.formats import LrxyID3, LrxyVorbis, LrxyMP4
from lrxy.exceptions import UnsupportedFileFormatError


def load_audio(file: Union[Path, str]) -> Union[LrxyID3, LrxyVorbis, LrxyMP4]:
    """Load audio file with lyric-capable handler based on file format.

    Automatically detects audio format and returns the appropriate lyric handler:
    - MP3 files → LrxyID3 (ID3 tags)
    - Ogg/Vorbis files → LrxyVorbis (Vorbis comments)
    - MP4/M4A files → LrxyMP4 (MP4 tags)

    The returned handler provides a consistent interface for embedding lyrics
    regardless of underlying format. All handlers support the `embed_lyric()`
    method with identical parameters.

    Args:
        file: Path to audio file (string or Path object)

    Returns:
        Format-specific lyric handler instance:
        - LrxyID3 for MP3 files
        - LrxyVorbis for Ogg/Vorbis files
        - LrxyMP4 for MP4/M4A files

    Raises:
        UnsupportedFileFormatError: When file format isn't supported
        FileNotFoundError: If file doesn't exist

    Example:
        >>> from lrxy.utils import load_audio
        >>> audio = load_audio("song.mp3")
        >>> audio.embed_lyric("Verse 1\\nThis is a line\\n\\nChorus\\n...")
    """

    audio = File(file)

    if audio:
        if isinstance(audio.tags, ID3):
            return LrxyID3(audio)
        if isinstance(audio.tags, VComment):
            return LrxyVorbis(audio)
        if isinstance(audio.tags, MP4Tags):
            return LrxyMP4(audio)

    raise UnsupportedFileFormatError()
