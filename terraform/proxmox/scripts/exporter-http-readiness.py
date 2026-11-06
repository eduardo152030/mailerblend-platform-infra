"""Bounded HTTP readiness after orderly exporter start, without exposing endpoint values."""
import time
import urllib.request

def wait_http(url,timeout=120,interval=2):
    assert timeout>0 and interval>0
    deadline=time.monotonic()+timeout
    while True:
        try:
            with urllib.request.urlopen(url,timeout=min(8,timeout)) as response:
                assert response.status==200
            return
        except (OSError,AssertionError):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Original exporter HTTP readiness timed out') from None
            time.sleep(min(interval,remaining))
