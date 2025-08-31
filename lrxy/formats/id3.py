"""ID3 tag handler for embedding unsynchronized lyrics in audio files.

This module provides the LrxyID3 class which specializes in embedding
unsynchronized lyrics (USLT) into ID3 tags of audio files. It handles
tag version conversion, existing lyric cleanup, and proper metadata
formatting for maximum compatibility with media players.
"""

from mutagen.id3 import USLT
from mutagen import FileType
from .filetype import AudioType


class LrxyID3(AudioType):
    """ID3 tag handler for lyric embedding operations.

    Specializes in managing unsynchronized lyrics (USLT) in audio files
    using ID3v2.3 tags. Handles automatic tag version conversion and
    cleanup of existing lyric tags before embedding new content.

    Inherits from AudioType to enforce required metadata fields
    (artist, title, album) while adding lyric-specific functionality.

    Args:
        audio: Mutagen audio file object with ID3 tag support
            (e.g., MP3 file loaded via mutagen.File())
    """

    def __init__(self, audio: FileType):
        """Initialize with audio file and required metadata fields.

        Prepares the audio file for lyric operations by:
        1. Ensuring required metadata fields exist (artist, title, album)
        2. Setting up the ID3 tag management context

        Args:
            audio: Mutagen audio file object to process
        """
        super().__init__(audio, ["TPE1", "TIT2", "TALB"])

        self.has_lyric = any([audio.tags.getall(tag) for tag in ['USLT', 'SYLT']])

    def embed_lyric(self, lyric: str) -> None:
        """Embed lyrics into the audio file's ID3 tags.

        Performs a complete lyric embedding workflow:
        1. Converts tags to ID3v2.3 (broadest player compatibility)
        2. Removes all existing USLT and SYLT lyrics
        3. Creates new USLT tag with UTF-8 encoding (encoding=3)
        4. Saves changes to the audio file

        Note:
            - Uses empty description field ('') for the USLT tag
              (standard for primary lyrics display)
            - Overwrites any existing lyrics without preservation

        Args:
            lyric: Lyrics text to embed

        Example:
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.mp3")
            >>> audio.embed_lyric("Verse 1\\nThis is a line\\n\\nChorus\\n...")
        """

        lyric_tag = USLT(encoding=3, desc='', text=lyric)
        audio = self.audio
        audio.tags.update_to_v23()
        audio.tags.delall('USLT')
        audio.tags.delall('SYLT')
        audio.tags.add(lyric_tag)
        audio.save()
