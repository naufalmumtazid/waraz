"""Backward-compatibility layer for video matching.

Delegates to `src.video.matching` with Indonesian parameter aliases.
"""

from .matching import match_two_sequences, search_archive
from typing import Any, Dict, List, Optional


def cocokkan_dua_sequence(
    query_hashes: List[str],
    archive_hashes: List[str],
    query_dhashes: Optional[List[str]] = None,
    archive_dhashes: Optional[List[str]] = None,
    # Indonesian aliases
    ambang_hamming: int = None,
    min_berurutan: int = None,
    # English aliases (pass-through)
    hamming_threshold: int = None,
    min_consecutive: int = None,
) -> Dict[str, Any]:
    """Indonesian alias for match_two_sequences.

    Accepts both Indonesian (ambang_hamming, min_berurutan) and
    English (hamming_threshold, min_consecutive) keyword arguments.
    """
    from .config import HAMMING_THRESHOLD, MIN_CONSECUTIVE_FRAMES

    # Indonesian takes precedence, then English, then defaults
    _hamming = (
        ambang_hamming if ambang_hamming is not None else
        (hamming_threshold if hamming_threshold is not None else HAMMING_THRESHOLD)
    )
    _min_cons = (
        min_berurutan if min_berurutan is not None else
        (min_consecutive if min_consecutive is not None else MIN_CONSECUTIVE_FRAMES)
    )

    return match_two_sequences(
        query_hashes=query_hashes,
        archive_hashes=archive_hashes,
        query_dhashes=query_dhashes,
        archive_dhashes=archive_dhashes,
        hamming_threshold=_hamming,
        min_consecutive=_min_cons,
    )


def cari_di_arsip(query_hashes, db, **kwargs) -> Dict[str, Any]:
    """Indonesian alias for search_archive."""
    return search_archive(query_hashes, db, **kwargs)


__all__ = [
    "match_two_sequences",
    "cocokkan_dua_sequence",
    "search_archive",
    "cari_di_arsip",
]
