# lrxy - Lyric Embedding Library

[![PyPI - Version](https://img.shields.io/pypi/v/lrxy)](https://pypi.org/project/lrxy/)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpxeemo%2Flrxy%2Fmain%2Fpyproject.toml)](https://pypi.org/project/lrxy/)

Embed lyrics directly into your audio files with a simple, consistent interface across multiple audio formats.

## Features

- **Support multiple providers**: Ablity to choose between different providers. Currently supported providers:

|Provider|Details|
|-|----|
|**LRCLib**|Simple and reliable LRC provider|
|**Apple Music**|Supports word-by-word lyrics|
|**MusixMatch**|Large lyrics database used by most streaming services|
- **Batch processing**: Process multiple files efficiently
- **Support multiple formats**: Support a wide range of audio formats and most used lyric formats including:

|Format|Details|
|-|------|
|**LRC**|Extended LyRiC is a rich LRC format with word-by-word support and other features|
|**TTML**|Timed Text Markup Language standard by Apple|
|**SRT**|Popular line-by-line media subtitle format|

## Installation

#### Using pip:
```sh
pip install lrxy
```

#### Using uv:
```sh
uv tool install lrxy  # as a cli tool
uv pip install lrxy   # as a python module
```

## Command Line

### lrxy

A synced lyric fetcher and embedder for music files

```
usage: lrxy [-h] [-n | --embed FILE] [-f {ttml,lrc,srt,json}]
            [-p {lrclib,musixmatch,applemusic}] [--no-overwrite]
            [--shell-completion {bash,zsh,fish}]
            [--log-level {error,warning,info,debug}] [-v]
            MUSIC_FILE [MUSIC_FILE ...]

positional arguments:
  MUSIC_FILE            path of music file to process

options:
  -h, --help            show this help message and exit
  -n, --no-embed        write lyrics to separate text files
  --embed FILE          embed existing lyric file into music
  -f {ttml,lrc,srt,json}, --format {ttml,lrc,srt,json}
                        output lyrics format
  -p {lrclib,musixmatch,applemusic}, --provider {lrclib,musixmatch,applemusic}
                        provider to fetch lyrics
  --no-overwrite        do not overwrite existing lyrics
  --shell-completion {bash,zsh,fish}
                        provide shell completion
  --log-level {error,warning,info,debug}
                        command line verbosity
  -v, --version         show current lrxy version and exit
```
Provider is going to be lrclib by default

### lrxy-convert

A tool from lrxy to convert between different lyric formats

```
usage: lrxy-convert [-h] [-i {ttml,lrc,srt,json}]
                    [-o {ttml,lrc,srt,json}]
                    [--shell-completion {bash,zsh,fish}]
                    [--log-level {error,warning,info,debug}]
                    INPUT OUTPUT

positional arguments:
  INPUT                 path of the input file to convert from
  OUTPUT                path of the output file to convert to

options:
  -h, --help            show this help message and exit
  -i {ttml,lrc,srt,json}, --input-format {ttml,lrc,srt,json}
                        input lyric file format
  -o {ttml,lrc,srt,json}, --output-format {ttml,lrc,srt,json}
                        output lyric file format
  --shell-completion {bash,zsh,fish}
                        provide shell completion
  --log-level {error,warning,info,debug}
                        command line verbosity
```
The default output is a json structed data

### Example
Easy to use automatic batch lyric fetch and embed:
```sh
lrxy song1.mp3 song2.flac
```

Get lyric for songs as a separate ttml file from Apple Music:
```sh
lrxy -p applemusic -n song.opus
```

Embed a lyric file to a music without any further steps:
```sh
lrxy --embed lyric.lrc song.m4a
```

Convert a ttml file to an elrc type format:
```sh
lrxy-convert lyric.ttml lyric.lrc
```

You can also pipe with specifying the format manually:
```sh
lrxy-convert lyric.srt -o ttml - | cat
```

## Quick Start

```python
from lrxy.utils import load_audio, iter_files
from lrxy.providers import lrclib_api

# Load any audio file (MP3, FLAC, M4A, etc.)
for result in iter_files("song1.mp3", "song2.flac", provider=lrclib_api):
    audio = result["music_obj"]
    lyric = result["data"]["lyric"]
    if lyric:
        audio.embed_lyric(lyric)
```

## Usage

### Basic Lyric Embedding

```python
from lrxy.utils import load_audio

# Load audio file (format detected automatically)
audio = load_audio("path/to/song.mp3")

# Check required metadata
print(f"Artist: {audio.artist}")
print(f"Title: {audio.title}")
print(f"Album: {audio.album}")
print(f"Duration: {audio.duration} seconds")

# Embed lyrics
audio.embed_lyric("Verse 1\nThis is a line\n\nChorus\nThis is the chorus")
```

### Lyric Converting
```python
from lrxy.converter import ttml, lrc

with open("path/to/lyric.ttml", "r") as f:
  ttml_lyric = f.read()

# parse the contents of the ttml file into a structed json data
data = ttml.parse(ttml_lyric)

# generate lrc format lyric from the structed data
lrc_lyric = lrc.generate(data)

with open("path/to/output/lyric.lrc", "w") as f:
  f.write(lrc_lyric)
```

### Batch Processing

```python
from lrxy.utils import iter_files

# Process multiple files with automatic lyric fetching
for result in iter_files("song1.mp3", "song2.flac", "song3.m4a"):
    if not result['success']:
        print(f"❌ {result['path'].name}: {result['error']}")
    elif not result['data']['syncedLyrics']:
        print(f"⚠️  {result['music_obj'].track_name}: No lyrics found")
    else:
        result['music_obj'].embed_lyric(result['syncedLyrics'])
        print(f"✅ {result['music_obj'].track_name}")
```

### Embed Lyrics from File

```python
from lrxy.utils import load_audio

audio = load_audio("song.mp3")
audio.embed_from_file("song.lrc")
```

## Supported Audio Formats

lrxy supports the most common audio formats with consistent API access:

| Format | File Extensions | Tag Standard | Notes |
|--------|-----------------|--------------|-------|
| **MP3** | `.mp3` | ID3 | Supports both ID3v2.3 and ID3v2.4 and uses `USLT` tag to store lyric |
| **FLAC**, **Opus** | `.flac`, `.opus` | Vorbis Comments | Stores lyrics in standard `lyrics` field |
| **Ogg Vorbis** | `.ogg`, `.oga` | Vorbis Comments | Same as FLAC format handling |
| **M4A/MP4** | `.m4a`, `.mp4`, `.aac` | MP4 atoms | Uses Apple's `©lyr` field |

### Format-Specific Details

#### MP3 (ID3 Tags)
- **Required metadata**: Artist (`TPE1`), Title (`TIT2`), Album (`TALB`)
- **Lyrics storage**: `USLT` frame (unsynchronized lyrics)

#### FLAC/Ogg (Vorbis Comments)
- **Required metadata**: Artist (`artist`), Title (`title`), Album (`album`)
- **Lyrics storage**: Standard `lyrics` field
- **Special handling**: Preserves all existing metadata while updating lyrics

#### M4A/MP4 (MP4 Atoms)
- **Required metadata**: Artist (`©ART`), Title (`©nam`), Album (`©alb`)
- **Lyrics storage**: Apple's `©lyr` field
- **Special handling**: Compatible with iTunes, Apple Music, and modern players

## Error Handling

lrxy provides consistent error reporting through a standardized result structure:

```python
from lrxy.utils import iter_files

for result in iter_files("song1.mp3", "invalid_file.xyz"):
    if not result['success']:
        # All errors have the same structure
        print(f"Error processing {result['path'].name}:")
        print(f"- Type: {result['error']}")
        print(f"- Message: {result['message']}")
    else:
        # Successful results have consistent structure
        print(f"Processed {result['music_obj'].track_name}")
```

### Common Error Types

| Error Type | Description | Likely Cause |
|------------|-------------|--------------|
| `notfound` | Lyrics not found | Incorrect metadata or unavailable lyrics |
| `network` | Network/connection issue | Internet problems or API downtime |
| `api` | API response error | Invalid response format from lyric provider |
| `format` | Unsupported audio format | File extension not recognized |
| `tag` | Missing required metadata | Artist/title/album not present in file |

## Advanced Usage

### Custom Lyric Provider

```python
from lrxy.utils import iter_files
from lrxy.providers import lrclib_api

# Create custom provider function
def my_provider(tags):
    # Your custom implementation
    return lrclib_api(tags)  # Or your own API client

# Use with iter_files
for result in iter_files("song.mp3", provider=my_provider):
    # Process results...
```

### Skip Files with Existing Lyrics

```python
from lrxy.utils import iter_files

# Only process files without existing lyrics
for result in iter_files("Music/*.mp3"):
    audio = result['music_obj']
    if result['success']:
        lyric = result['data']['syncedLyrics']:
        if not audio.has_lyric:
            audio.embed_lyric(lyric, overwrite=False)
```

## Requirements

- Python 3.10+
- Mutagen (installed automatically as dependency)

## Acknowledgments
- [**Paxsenix API**](https://api.paxsenix.org/): For Apple Music and MusixMatch providers
- [**LRCLib**](https://lrclib.net): For their great lyric platform

## License

Distributed under the GPLv2 License. See [LICENSE](LICENSE.md) for more information.
