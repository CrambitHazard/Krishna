"""
KRISHNA — File utilities.

Common helpers for file I/O, path resolution, etc.
"""

from __future__ import annotations

from pathlib import Path

ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md", ".docx", ".pptx"}


def is_allowed_file(filename: str) -> bool:
    """Return True if the file extension is in the allow-list."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def safe_filename(filename: str) -> str:
    """Sanitise a filename — strips directory components."""
    return Path(filename).name
