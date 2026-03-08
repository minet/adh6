"""Pytest bootstrap for backend test discovery.

Ensures the backend package root is importable when pytest is launched from the
repository root (IDE discovery case).
"""

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parent
backend_root_str = str(BACKEND_ROOT)

if backend_root_str not in sys.path:
    sys.path.insert(0, backend_root_str)
