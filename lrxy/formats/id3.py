"""ID3 tag handler for embedding unsynchronized lyrics in audio files.

This module provides the LrxyID3 class which specializes in embedding
unsynchronized lyrics (USLT) into ID3 tags of audio files. It handles
tag version conversion, existing lyric cleanup, and proper metadata
formatting for maximum compatibility with media players.
"""

from mutagen.id3 import USLT
from mutagen import FileType
from .filetype import LrxyAudio


class LrxyID3(LrxyAudio):
    """ID3 tag handler for lyric embedding operations.

    Specializes in managing unsynchronized lyrics (USLT) in audio files
    using ID3 tags. Handles automatic tag version conversion and
    cleanup of existing lyric tags before embedding new content.

    Inherits from LrxyAudio to enforce required metadata fields
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
        super().__init__(audio, {
            "artist": "TPE1",
            "title": "TIT2",
            "album": "TALB",
        })

        self.has_lyric = any((audio.tags.getall(tag)
                             for tag in ['USLT', 'SYLT']))

    def embed_lyric(self, lyric: str) -> None:
        """Embed lyrics into the audio file's ID3 tags.

        Performs a complete lyric embedding workflow:
        1. Removes all existing USLT and SYLT lyrics
        2. Creates new USLT tag with UTF-8 encoding (encoding=3)
        3. Saves changes to the audio file

        Note:
            - Uses empty description field ('') for the USLT tag
              (standard for primary lyrics display)
            - Overwrites any existing lyrics without preservation

        Args:
            lyric: Lyrics text to embed

        Example:
            ```python
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.mp3")
            >>> audio.embed_lyric("Verse 1\\nThis is a line\\n\\nChorus\\n...")
            ```
        """

        lyric_tag = USLT(encoding=3, desc='Embedded with lrxy', text=lyric)
        audio = self.audio
        audio.tags.delall('USLT')
        audio.tags.delall('SYLT')
        audio.tags.add(lyric_tag)
        audio.save()
