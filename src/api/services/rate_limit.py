from __future__ import annotations

from collections import defaultdict, deque
from time import time


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        # I keep the limiter in memory because it is enough for a single-node
        # deployment and gives the API a first layer of abuse protection.
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        # I return both the decision and retry time because clients can behave
        # more politely when the API tells them when to try again.
        now = time()
        bucket = self._events[key]
        cutoff = now - self.window_seconds

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
            return False, retry_after

        bucket.append(now)
        return True, 0
