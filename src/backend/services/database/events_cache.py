from __future__ import annotations
import asyncio
from typing import Set

from sqlalchemy import event
from sqlalchemy.orm import Session
from cashews import cache as C

from services.cache.keys import (
    L1_PREFIX,
    ACTIVITY_STATS_ALL,
    MEMBER_STATS_ALL,
    TAG_ACTIVITY_STATS,
    TAG_MEMBER_STATS,
)

_CHANGED_KEY = "__changed_tablenames__"


@event.listens_for(Session, "after_flush")
def _after_flush_collect(session: Session, flush_ctx) -> None:  # type: ignore[no-redef]
    names: Set[str] = session.info.setdefault(_CHANGED_KEY, set())
    for obj in session.new.union(session.dirty).union(session.deleted):
        name = getattr(getattr(obj, "__table__", None), "name", None) or getattr(obj, "__tablename__", None)
        if name:
            names.add(name)


@event.listens_for(Session, "after_commit")
def _after_commit_invalidate(session: Session) -> None:  # type: ignore[no-redef]
    names: Set[str] = session.info.pop(_CHANGED_KEY, set())
    if not names:
        return
    loop = asyncio.get_event_loop()

    if any(name in {"activities", "activity", "activity_participants"} for name in names):
        loop.create_task(C.delete(ACTIVITY_STATS_ALL))
        loop.create_task(C.delete(f"{L1_PREFIX}{ACTIVITY_STATS_ALL}"))
        # Future: tag-based invalidation
        # loop.create_task(C.delete_tags(TAG_ACTIVITY_STATS))

    if any(name in {"members", "member"} for name in names):
        loop.create_task(C.delete(MEMBER_STATS_ALL))
        loop.create_task(C.delete(f"{L1_PREFIX}{MEMBER_STATS_ALL}"))
        # loop.create_task(C.delete_tags(TAG_MEMBER_STATS))
