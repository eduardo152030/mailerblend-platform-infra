"""Serialize post-watch probes with planned Prometheus reload/readiness transactions.

Does not pause scraping or applications. Primary per-CT observation remains every30s;
only overlapping post-watch probes wait for a known configuration transaction to finish.
"""
import contextlib,fcntl,os
from pathlib import Path

@contextlib.contextmanager
def monitoring_lock(root,exclusive):
    path=Path(root)/'prometheus-transaction.lock'
    fd=os.open(path,os.O_RDWR|os.O_CREAT,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield
    finally:
        fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
