"""Backward-compatibility layer for video matching.

Delegates directly to `src.video.matching`.
"""

from .matching import (
    cari_di_arsip,
    cocokkan_dua_sequence,
    match_two_sequences,
    search_archive,
)

__all__ = [
    "match_two_sequences",
    "cocokkan_dua_sequence",
    "search_archive",
    "cari_di_arsip",
]
