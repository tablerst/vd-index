from __future__ import annotations
from cashews import cache


class CashewsCache:
    @staticmethod
    def setup(*, redis_url: str, l1_size: int = 10000, l1_prefix: str = "l1:") -> None:
        """Initialize cashews with explicit two backends:
        - L1: in-process memory bound to a prefix (e.g., l1:)
        - L2: redis as default backend (no prefix)
        """
        # L1 - memory backend with capacity limit, under the given prefix
        cache.setup(f"mem://?size={l1_size}", prefix=l1_prefix.rstrip(":"))
        # L2 - redis backend (default)
        cache.setup(redis_url)
