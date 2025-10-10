"""Base classes for audio file handling and metadata management.

Provides foundational classes for:
- File path validation and normalization (BaseFile)
- Audio metadata extraction and lyric embedding (LrxyAudio)

All format-specific handlers (LrxyID3, LrxyVorbis, LrxyMP4) inherit from
these base classes to ensure consistent behavior across audio formats.
"""

from pathlib import Path

from mutagen import FileType

from lrxy.exceptions import (
    NotFileError,
    TagError,
    PathNotExistsError,
)


def validate_path(path: str | Path) -> Path:
    """Initialize with validated file path.

    Checks existence, and validates file type/format.

    Args:
        path: File path to process

    Raises:
        ValueError: Invalid path type
        PathNotExistsError: Path doesn't exist
        NotFileError: Path is not a file
        UnsupportedFileFormatError: Invalid music file format

    Returns:
        path (Path): Normalized path

    Example:
        ```python
        >>> from pathlib import Path
        >>> BaseFile(Path("~/Music/song.flac").expanduser())
        ```
    """
    if isinstance(path, str):
        path = Path(path).expanduser()
    elif isinstance(path, Path):
        path = path.expanduser()
    else:
        raise ValueError(
            "The path must be a string or a pathlib.Path object")

    if not path.exists():
        raise PathNotExistsError()

    if not path.is_file():
        raise NotFileError()

    # extension = path.suffix
    return path


class LrxyAudio:
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
        >>> handler = LrxyAudio(audio, {
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
            >>> LrxyAudio(audio, {
            ...     "artist": "TPE1",
            ...     "title": "TIT2",
            ...     "album": "TALB",
            ... })  # tag keys for ID3
        """
        self.path = validate_path(audio.filename)
        self.audio = audio
        self.artist = audio.get(tag_keys["artist"])
        self.title = audio.get(tag_keys["title"])
        self.album = audio.get(tag_keys["album"])
        self.duration = str(int(audio.info.length))

        if self.artist:
            self.artist = self.artist[0]
        else:
            raise TagError("artist")

        if self.title:
            self.title = self.title[0]
        else:
            raise TagError("title")

        if self.album:
            self.album = self.album[0]
        else:
            raise TagError("album")

    def __repr__(self):
        """Return formal string representation.

        Example:
            ```python
            >>> repr(LrxyAudio(...))
            "LrxyID3('path/to/song.mp3')"
            ```
        """
        return f"{self.__class__.__name__}({str(self.path)!r})"

    def __str__(self):
        """Return string representation (file path).

        Example:
            ```python
            >>> str(LrxyAudio(...))
            "path/to/song.mp3"
            ```
        """
        return str(self.path)

    def get_tags(self) -> dict[str, str]:
        """Get extracted metadata as dictionary.

        Returns: Dictionary containing:
            title: Track title
            artist: Primary artist name
            album: Album title
            duration: Track duration in seconds (as string)

        Example:
            ```python
            >>> handler.get_tags()
            {
                'title': 'Title',
                'artist': 'Artist',
                'album': 'Album',
                'duration': '245'
            }
            ```
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

    def embed_from_file(self, path: str | Path):
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
        file = validate_path(path)

        with open(file) as lrc:
            self.embed_lyric(lrc.read())
