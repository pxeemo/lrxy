from pathlib import Path
from typing import Union

from mutagen import File
from mutagen._vorbis import VComment
from mutagen.id3 import ID3
from mutagen.mp4 import MP4Tags

from lrxy.formats import LrxyID3, LrxyVorbis, LrxyMP4
from lrxy.exceptions import UnsupportedFileFormatError


def load_audio(file: Union[Path, str]) -> Union[LrxyID3, LrxyVorbis, LrxyMP4]:
    audio = File(file)

    if isinstance(audio.tags, ID3):
        return LrxyID3(audio)
    if isinstance(audio.tags, VComment):
        return LrxyVorbis(audio)
    if isinstance(audio.tags, MP4Tags):
        return LrxyMP4(audio)

    raise UnsupportedFileFormatError(audio.__name__)
