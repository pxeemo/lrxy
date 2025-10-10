"""Public interface for audio format-specific lyric handlers.

Exposes the three main lyric handler classes that implement the
consistent embedding interface across different audio formats.
These classes are automatically selected by `lrxy.utils.load_audio()`
and generally shouldn't be instantiated directly by users.

For most use cases, prefer using the unified interface:
    >>> from lrxy.utils import load_audio
    >>> audio = load_audio("song.mp3")
    >>> audio.embed_lyric("...")

The following format-specific handlers are available for advanced use:
- LrxyAudio: Superclass of LrxyID3, LrxyVorbis and LrxyMP4
- LrxyID3: For MP3 files (ID3 tags)
- LrxyVorbis: For Ogg/Vorbis and FLAC files
- LrxyMP4: For M4A/MP4 files

All handlers inherit from LrxyAudio and provide identical methods:
- embed_lyric(lyric: str): Embed plain-text lyrics
- embed_from_file(path): Embed lyrics from separate text file
- get_tags(): Retrieve metadata dictionary
"""

from .filetype import LrxyAudio
from .id3 import LrxyID3
from .vorbis import LrxyVorbis
from .mp4 import LrxyMP4


__all__ = ["LrxyAudio", "LrxyID3", "LrxyVorbis", "LrxyMP4"]
