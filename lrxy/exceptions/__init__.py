"""Provides different type of exceptions"""


class LrxyException(Exception):
    """Base exception super class type"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class PathNotExistsError(LrxyException):
    """Path does not exist."""

    def __init__(self) -> None:
        super().__init__("Path does not exist.")


class NotFileError(LrxyException):
    """Path is not a file."""

    def __init__(self) -> None:
        super().__init__("Path is not a file.")


class UnsupportedFileFormatError(LrxyException):
    """Unsupported file format."""

    def __init__(self) -> None:
        super().__init__("Unsupported file format.")


class TagError(LrxyException):
    """File has no valid metadata tag"""

    def __init__(self, tag_name: str) -> None:
        super().__init__(f"File has no tag {tag_name}")


class ParseLyricError(LrxyException):
    """There was a problem with parsing"""

    def __init__(self, in_format: str) -> None:
        super().__init__(f"There was a problem parsing {in_format}")
