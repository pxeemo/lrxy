from .filetype import AudioType


class LrxyVorbis(AudioType):
    """
        Example:
        >>> flac_music = Flac("System Of A Down - Chop Suey.flac")
        >>> flac_music.track_name
        Chop Suey
        >>> flac_music.get_tags()
        {
            'artist_name': 'System Of A Down',
            'track_name': 'Chop Suey',
            'album_name': 'Toxicity',
            'duration': '208'
        }
        >>> with open("lyric.txt") as f:
        ...     flac_music.embed_lyric(f.read())
    """

    def __init__(self, audio):
        super().__init__(audio, ["artist", "title", "album"])

    def embed_lyric(self, lyric: str) -> None:
        self.audio["lyrics"] = lyric
        self.audio.save()
