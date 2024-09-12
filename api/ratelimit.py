from datetime import timedelta

from django.core.cache import caches
from django.core.exceptions import PermissionDenied


class RateLimitExceeded(PermissionDenied):
    def __init__(self, usage, limit):
        self.usage = usage
        self.limit = limit
        super().__init__("Rate limit exceeded")


class RateLimit:
    def __init__(self, *, key, limit, period, cache=None, key_prefix="rl:"):
        self.key = key
        self.limit = limit

        if isinstance(period, timedelta):
            
            self.seconds = period.total_seconds()   # Can pass a timedelta for convenience
        else:
            self.seconds = period

        self.cache = cache or caches["default"]
        self.key_prefix = key_prefix

    def get_usage(self):
        
        return self.cache.get_or_set(
            self.key_prefix + self.key, 0, timeout=self.seconds # Timeout will be set here if it didn't exist, with a starting value of 0
        )

    def increment_usage(self):
        self.cache.incr(self.key_prefix + self.key, delta=1)

    def check(self):
        usage = self.get_usage()

        if usage >= self.limit:
            raise RateLimitExceeded(usage=usage, limit=self.limit)

        self.increment_usage()