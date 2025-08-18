"""
Global project state utilities for LibriScribe2.

This module maintains lightweight global state that needs to be accessible
across modules without explicit plumbing through call stacks.

Currently stores:
- initial_date (UTC YYYY-MM-DD) for tagging LLM requests consistently.
"""

from __future__ import annotations

import threading

_lock = threading.RLock()
_initial_date: str | None = None


def set_initial_date(date_str: str) -> None:
    """Set the project's initial date (UTC YYYY-MM-DD)."""
    global _initial_date
    if not isinstance(date_str, str) or not date_str:
        return
    with _lock:
        _initial_date = date_str


def get_initial_date() -> str | None:
    """Get the project's initial date if set, else None."""
    with _lock:
        return _initial_date
