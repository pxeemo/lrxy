"""Base classes for audio file handling and metadata management.

Provides foundational classes for:
- File path validation and normalization (BaseFile)
- Audio metadata extraction and lyric embedding (AudioType)

All format-specific handlers (LrxyID3, LrxyVorbis, LrxyMP4) inherit from
these base classes to ensure consistent behavior across audio formats.
"""

from typing import Union, List, Dict
from pathlib import Path

from mutagen import FileType

from lrxy.exceptions import (
    UnsupportedFileFormatError,
    FileError,
    TagError,
    PathNotExistsError,
)


class BaseFile:
    """Base class for file path handling and validation.

    Provides standardized file path processing and validation for both
    audio files and lyric files. Handles path normalization, existence
    checks, and format validation.

    Args:
        path: File path (string or Path object)
        match_file: If True, validates path has desired format extension (.lrc)

    Raises:
        ValueError: If path is not string or Path object
        PathNotExistsError: If file doesn't exist
        FileError: If path points to a directory
        UnsupportedFileFormatError: If match_file=True and extension invalid

    Example:
        >>> from lrxy.formats import BaseFile
        >>> audio_file = BaseFile("song.mp3")
        >>> lrc_file = BaseFile("song.lrc", match_file=True)
    """

    def __init__(self, path: Union[str, Path], *, match_file: bool = False) -> None:
        """Initialize with validated file path.

        Normalizes path, checks existence, and validates file type/format.

        Args:
            path: File path to process
            match_file: Require .lrc extension when True

        Raises:
            ValueError: Invalid path type
            PathNotExistsError: Path doesn't exist
            FileError: Path is a directory
            UnsupportedFileFormatError: Invalid music file format

        Example:
            >>> from pathlib import Path
            >>> BaseFile(Path("~/Music/song.flac").expanduser())
        """
        if isinstance(path, str):
            self.path = Path(path).expanduser()
        elif isinstance(path, Path):
            self.path = path.expanduser()
        else:
            raise ValueError(
                "The path must be a string or a pathlib.Path object")

        if not self.path.exists():
            raise PathNotExistsError(str(self.path))

        if not self.path.is_file():
            raise FileError(str(self.path))

        self.extension = self.path.suffix


class AudioType(BaseFile):
    """Abstract base class for audio metadata handling and lyric embedding.

    Provides standardized:
    - Metadata extraction (artist, title, album, duration)
    - Required tag validation
    - Consistent lyric embedding interface

    Format-specific subclasses must implement embed_lyric() to handle
    format-specific tag operations. All handlers guarantee the same
    public interface for lyric embedding operations.

    Args:
        audio: Mutagen audio file object
        tag_keys: Tag names for {"artist": str, "title": str, "album": str}

    Raises:
        TagError: Missing required metadata tag

    Example:
        >>> from mutagen import File
        >>> audio = File("song.mp3")
        >>> handler = AudioType(audio, {
        ...     "artist": "TPE1",
        ...     "title": "TIT2",
        ...     "album": "TALB",
        ... })  # tag keys for ID3
        >>> handler.embed_lyric("...")  # Implemented by subclasses
    """

    def __init__(self, audio: FileType, tag_keys: dict[str, str]) -> None:
        """Initialize with validated audio metadata.

        Extracts and validates required metadata fields from audio tags.
        Computes duration in seconds as integer string.

        Args:
            audio: Mutagen audio file object
            tag_keys: Tag names for {"artist": str, "title": str, "album": str}

        Raises:
            TagError: If any required tag is missing

        Example:
            >>> from mutagen.mp3 import MP3
            >>> audio = MP3("song.mp3")
            >>> AudioType(audio, {
            ...     "artist": "TPE1",
            ...     "title": "TIT2",
            ...     "album": "TALB",
            ... })  # tag keys for ID3
        """
        super().__init__(audio.filename)

        self.audio = audio
        self.artist = audio.get(tag_keys["artist"])
        self.title = audio.get(tag_keys["title"])
        self.album = audio.get(tag_keys["album"])
        self.duration = str(int(audio.info.length))

        if self.artist:
            self.artist = self.artist[0]
        else:
            raise TagError(str(self.path), "artist")

        if self.title:
            self.title = self.title[0]
        else:
            raise TagError(str(self.path), "track")

        if self.album:
            self.album = self.album[0]
        else:
            raise TagError(str(self.path), "album")

    def __repr__(self):
        """Return formal string representation.

        Example:
            >>> repr(AudioType(...))
            "LrxyID3('path/to/song.mp3')"
        """
        return f"{self.__class__.__name__}({str(self.path)!r})"

    def __str__(self):
        """Return string representation (file path).

        Example:
            >>> str(AudioType(...))
            "path/to/song.mp3"
        """
        return str(self.path)

    def get_tags(self) -> Dict[str, str]:
        """Get extracted metadata as dictionary.

        Returns:
            Dictionary containing:
            - title: Track title
            - artist: Primary artist name
            - album: Album title
            - duration: Track duration in seconds (as string)

        Example:
            >>> handler.get_tags()
            {
                'title': 'Title',
                'artist': 'Artist',
                'album': 'Album',
                'duration': '245'
            }
        """
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
        }

    def embed_lyric(self, lyric: str):
        """Embed lyrics into audio file (abstract method).

        Must be implemented by format-specific subclasses.

        Args:
            lyric: Lyrics text to embed

        Raises:
            NotImplementedError: Always raised in base class

        Example:
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.mp3")
            >>> audio.embed_lyric("Verse 1\\nThis is a line\\n...")
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def embed_from_file(self, path: Union[str, Path]):
        """Embed lyrics from an external file.

        Loads lyrics from external file and embeds using format-specific
        handler. Validates input file format before processing.

        Args:
            path: Path to external lyric file

        Raises:
            UnsupportedFileFormatError: If file extension invalid
            PathNotExistsError: If lyric file doesn't exist

        Example:
            >>> from lrxy.utils import load_audio
            >>> audio = load_audio("song.mp3")
            >>> audio.embed_from_file("song.lrc")
        """
        file = BaseFile(path, match_file=True)

        with open(file.path) as lrc:
            self.embed_lyric(lrc.read())
