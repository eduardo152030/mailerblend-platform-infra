"""Future-worker safety contract, NOT deployed or a Chatterbox implementation.

All heavy engines must use the same serial agent queue and this existing PVE lock.
The context must cover process death/empty cgroup, not just task cancellation.
"""
from contextlib import contextmanager
import fcntl


@contextmanager
def engine_slot(path, preflight):
    with open(path, 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            if not preflight():
                raise RuntimeError('Insufficient memory or unavailable engine; do not load weights')
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
