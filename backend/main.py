"""FastAPI entry point for ADH6 Backend.

This module re-exports the FastAPI application from adh6.main for use with
ASGI servers (e.g., Gunicorn with Uvicorn workers, Docker, etc.).
"""

from adh6.main import app as application

__all__ = ["application"]
