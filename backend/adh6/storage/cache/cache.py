"""Async-compatible cache module for FastAPI.

In the async FastAPI context, caching is handled at the FastAPI level using
appropriate headers and potentially external cache solutions (Redis, Memcached).
This module provides a stub for backward compatibility.
"""


class AsyncCache:
    """Stub cache class for compatibility with existing code."""

    def get(self, key: str):
        """Get a value from cache (returns None in stub)."""
        return None

    def set(self, key: str, value, timeout=None):
        """Set a value in cache (no-op in stub)."""

    def delete(self, key: str):
        """Delete a value from cache (no-op in stub)."""

    def clear(self):
        """Clear all cache (no-op in stub)."""


# Stub cache instance for compatibility
cache = AsyncCache()
