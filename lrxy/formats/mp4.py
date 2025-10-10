"""MP4 tag handler for embedding lyrics in M4A/MP4 audio files.

Provides a consistent lyric embedding interface for MP4-based audio formats
(M4A, MP4, etc.). Uses Apple's standard metadata fields for lyrics storage
and enforces required metadata validation.
"""

from mutagen import FileType
from .filetype import LrxyAudio


class LrxyMP4(LrxyAudio):
    """MP4 tag handler for lyric embedding operations.

    Specializes in managing lyrics for MP4-based audio formats (M4A, MP4, etc.).
    Uses Apple's standard metadata fields and ensures required metadata exists
    before lyric operations.

    Inherits from LrxyAudio to enforce required metadata fields using
    MP4-specific atom names (©ART, ©nam, ©alb).

    Args:
        audio: Mutagen audio file object with MP4 tag support
            (e.g., M4A file loaded via mutagen.File())
    """

    def __init__(self, audio: FileType) -> None:
        """Initialize with audio file and required metadata fields.

        Prepares the audio file for lyric operations by:
        1. Ensuring required metadata fields exist (artist, title, album)
        2. Setting up the MP4 tag management context

        Args:
            audio: Mutagen audio file object to process
        """
        super().__init__(audio, {
            "artist": "©ART",
            "title": "©nam",
            "album": "©alb",
        })

        self.has_lyric = bool(audio.tags.get("©lyr"))

    def embed_lyric(self, lyric: str) -> None:
        """Embed lyrics into the audio file's MP4 metadata.

        Stores lyrics in the standard '©lyr' field (lyrics atom), overwriting
        any existing content. Automatically saves changes to the file.

        Note:
            - Uses Apple's official '©lyr' metadata field
            - Preserves existing metadata while updating lyrics
            - Requires valid UTF-8 encoded input
            - Compatible with iTunes, Apple Music, and most modern players

        Args:
            lyric: Lyrics text to embed

        Example:
            ```python
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.m4a")
            >>> audio.embed_lyric("Verse 1\\nThis is a line\\n\\nChorus\\n...")
            ```
        """

        self.audio.tags["©lyr"] = lyric
        self.audio.save()
