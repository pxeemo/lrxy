class LrxyException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PathNotExistsError(LrxyException):
    def __init__(self) -> None:
        self.message = f"Path does not exist."
        super().__init__(self.message)


class FileError(LrxyException):
    def __init__(self) -> None:
        self.message = f"Path is not a file."
        super().__init__(self.message)


class UnsupportedFileFormatError(LrxyException):
    def __init__(self) -> None:
        self.message = f"Unsupported file format."
        super().__init__(self.message)


class TagError(LrxyException):
    def __init__(self, tag_name: str) -> None:
        self.message = f"File has no tag {tag_name}"
        super().__init__(self.message)


class ParseLyricError(LrxyException):
    def __init__(self, format: str) -> None:
        self.message = f"There was a problem parsing {format}"
