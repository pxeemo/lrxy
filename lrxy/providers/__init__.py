"""Lyrics provider modules to fetch and return with a consistant response
structure"""

from .lrclib import lrclib_api
from .musixmatch import musixmatch_api
from .applemusic import applemusic_api
from .qq import qq_api

__all__ = [
    "lrclib_api",
    "musixmatch_api",
    "applemusic_api",
    "qq_api",
]
