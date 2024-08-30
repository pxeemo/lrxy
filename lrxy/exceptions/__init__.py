class LrxyException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PathNotExistsError(LrxyException):
    def __init__(self, path: str) -> None:
        message = f"The path '{path}' does not exist"
        super().__init__(message)


class FileError(LrxyException):
    def __init__(self, path: str) -> None:
        message = f"This path '{path}' is not a file"
        super().__init__(message)


class UnsupportedFileFormatError(LrxyException):
    def __init__(self, unsupported_format: str,
                 supported_formats: list) -> None:
        message = (
            f"Unsupported format '{unsupported_format}'. "
            f"Only supported formats {supported_formats} "
        )
        super().__init__(message)


class TagError(LrxyException):
    def __init__(self, path: str, tag_name: str) -> None:
        message = f"This music '{path}' has no tag {tag_name}"
        super().__init__(message)
