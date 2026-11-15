"""Pytest bootstrap for backend test discovery.

Ensures the backend package root is importable when pytest is launched from the
repository root (IDE discovery case).
"""

import math
import os
import sys
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import Engine

BACKEND_ROOT = Path(__file__).resolve().parent
backend_root_str = str(BACKEND_ROOT)

if backend_root_str not in sys.path:
    sys.path.insert(0, backend_root_str)


# Above 4 workers the suite gets slower: worker start-up costs more than it saves.
MAX_XDIST_WORKERS = 4


def _available_cpus() -> int:
    """CPUs this process may really use, cgroup CPU quota included.

    os.cpu_count() and xdist's "auto" see every CPU of the host, even in a container limited
    with --cpus (the GitLab runner case): 16 workers on 2 CPUs runs the suite 4x slower.
    """
    cpus = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    quota_files = (
        ("/sys/fs/cgroup/cpu.max", None),  # cgroup v2: "<quota> <period>" or "max <period>"
        ("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "/sys/fs/cgroup/cpu/cpu.cfs_period_us"),  # cgroup v1
    )
    for quota_file, period_file in quota_files:
        try:
            if period_file is None:
                quota, period = Path(quota_file).read_text().split()
            else:
                quota, period = Path(quota_file).read_text().strip(), Path(period_file).read_text().strip()
        except (OSError, ValueError):
            continue
        if quota not in {"max", "-1"}:
            cpus = min(cpus, math.ceil(int(quota) / int(period)))
        break
    return max(1, cpus)


def pytest_xdist_auto_num_workers(config: object) -> int:
    """Number of workers for `pytest -n auto`."""
    return min(_available_cpus(), MAX_XDIST_WORKERS)


@event.listens_for(Engine, "connect")
def _sqlite_without_fsync(dbapi_connection: object, _connection_record: object) -> None:
    """Never wait for the disk to flush a test SQLite database.

    Every commit, and every CREATE TABLE of create_all(), otherwise costs fsync calls: about
    40 ms each on the GitLab runner disk, which made the suite take minutes there. A crash
    can corrupt a test database, which is thrown away anyway.
    """
    if "sqlite" not in type(dbapi_connection).__module__:
        return
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.close()
