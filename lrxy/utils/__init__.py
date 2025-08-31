"""Audio processing utilities for lyric embedding.

Provides the main public interface for:
- Loading audio files with automatic format detection (load_audio)
- Batch processing of audio files with consistent results (iter_files)

These functions form the core API for interacting with audio files
and embedding lyrics across different audio formats.
"""

# Public API exports
from .audio import load_audio
from .iter_files import iter_files

__all__ = ["load_audio", "iter_files"]
