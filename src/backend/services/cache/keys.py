from __future__ import annotations
import random
from datetime import timedelta

# L1 prefix (must match cashews_init setup)
L1_PREFIX = "l1:"

# Domain-level keys (examples already used in project)
ACTIVITY_STATS_ALL = "activity:stats:all"
MEMBER_STATS_ALL = "member:stats:all"

# Tags for bulk invalidation (reserved for future use)
TAG_ACTIVITY_STATS = "activity:stats"
TAG_MEMBER_STATS = "member:stats"


def ttl_with_jitter(base_seconds: int, *, spread: float = 0.2) -> timedelta:
    """Return a base TTL with +-spread jitter to avoid cache stampede.
    """
    delta = int(base_seconds * spread)
    return timedelta(seconds=base_seconds + random.randint(-delta, delta))
