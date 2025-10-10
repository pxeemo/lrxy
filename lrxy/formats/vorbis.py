"""Vorbis comment handler for embedding lyrics in Ogg/Vorbis and FLAC files.

Provides a consistent lyric embedding interface for audio formats using
Vorbis comments (Ogg, FLAC, etc.). Handles standard metadata validation
and provides simple lyric embedding through the 'lyrics' field.
"""

from mutagen import FileType
from .filetype import LrxyAudio


class LrxyVorbis(LrxyAudio):
    """Vorbis comment handler for lyric embedding operations.

    Specializes in managing lyrics for audio formats using Vorbis comments
    (Ogg, FLAC, etc.). Uses the standard 'lyrics' field for storage and
    ensures required metadata fields exist before operations.

    Inherits from LrxyAudio to enforce required metadata fields
    (artist, title, album) using Vorbis comment field names.

    Args:
        audio: Mutagen audio file object with Vorbis comment support
            (e.g., Ogg or FLAC file loaded via mutagen.File())
    """

    def __init__(self, audio: FileType):
        """Initialize with audio file and required metadata fields.

        Prepares the audio file for lyric operations by:
        1. Ensuring required metadata fields exist (artist, title, album)
        2. Setting up the Vorbis comment management context

        Args:
            audio: Mutagen audio file object to process
        """
        super().__init__(audio, {
            "artist": "artist",
            "title": "title",
            "album": "album",
        })

        self.has_lyric = bool(audio.tags.get("lyrics"))

    def embed_lyric(self, lyric: str) -> None:
        """Embed lyrics into the audio file's Vorbis comments.

        Stores lyrics in the standard 'lyrics' field, overwriting any
        existing content. Automatically saves changes to the file.

        Note:
            - Uses the official 'lyrics' field per Vorbis comment specification
            - Preserves existing metadata while updating lyrics
            - Requires valid UTF-8 encoded input

        Args:
            lyric: Lyrics text to embed

        Example:
            ```python
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.flac")
            >>> audio.embed_lyric("Verse 1\\nThis is a line\\n\\nChorus\\n...")
            ```
        """

        self.audio.tags["lyrics"] = lyric
        self.audio.save()
