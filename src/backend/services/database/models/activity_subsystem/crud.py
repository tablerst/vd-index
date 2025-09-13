"""
CRUD utilities for the new Activities subsystem (vote/thread).
"""
from __future__ import annotations

from typing import List, Optional, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import ActActivity, ActVoteOption, ActVoteRecord, ActThreadPost


class ActActivityCRUD:
    @staticmethod
    async def list(
        session: AsyncSession,
        status: str = "ongoing",
        page: int = 1,
        size: int = 10,
    ) -> Tuple[List[ActActivity], int]:
        offset = (page - 1) * size
        stmt = (
            select(ActActivity)
            .where(ActActivity.status == status)
            .order_by(ActActivity.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        result = await session.exec(stmt)
        items = result.all()

        count_stmt = select(func.count(ActActivity.id)).where(ActActivity.status == status)
        total = (await session.exec(count_stmt)).one()
        return items, total

    @staticmethod
    async def get(session: AsyncSession, activity_id: int) -> Optional[ActActivity]:
        return await session.get(ActActivity, activity_id)


class ActVoteCRUD:
    @staticmethod
    async def list_options(
        session: AsyncSession, activity_id: int, query: str | None = None, size: int = 50
    ) -> List[ActVoteOption]:
        stmt = select(ActVoteOption).where(ActVoteOption.activity_id == activity_id)
        if query:
            # simple ILIKE search
            stmt = stmt.where(ActVoteOption.label.ilike(f"%{query}%"))
        stmt = stmt.order_by(ActVoteOption.id.asc()).limit(size)
        return (await session.exec(stmt)).all()

    @staticmethod
    async def get_ranking(
        session: AsyncSession, activity_id: int, top: int = 10
    ) -> List[tuple[int, int]]:
        # returns list of (option_id, votes)
        stmt = (
            select(ActVoteRecord.option_id, func.count(ActVoteRecord.id))
            .where(ActVoteRecord.activity_id == activity_id)
            .group_by(ActVoteRecord.option_id)
            .order_by(func.count(ActVoteRecord.id).desc())
            .limit(top)
        )
        return (await session.exec(stmt)).all()

    @staticmethod
    async def get_vote_record(
        session: AsyncSession, activity_id: int, voter_id: int
    ) -> Optional[ActVoteRecord]:
        stmt = select(ActVoteRecord).where(
            ActVoteRecord.activity_id == activity_id, ActVoteRecord.voter_id == voter_id
        )
        return (await session.exec(stmt)).first()

    @staticmethod
    async def upsert_vote(
        session: AsyncSession,
        activity_id: int,
        option_id: int,
        voter_id: int,
        display_anonymous: bool,
    ) -> ActVoteRecord:
        record = await ActVoteCRUD.get_vote_record(session, activity_id, voter_id)
        if record:
            record.option_id = option_id
            record.display_anonymous = display_anonymous
            session.add(record)
        else:
            record = ActVoteRecord(
                activity_id=activity_id,
                option_id=option_id,
                voter_id=voter_id,
                display_anonymous=display_anonymous,
            )
            session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def revoke_vote(session: AsyncSession, activity_id: int, voter_id: int) -> bool:
        record = await ActVoteCRUD.get_vote_record(session, activity_id, voter_id)
        if not record:
            return False
        await session.delete(record)
        await session.commit()
        return True


class ActThreadCRUD:
    @staticmethod
    async def list_posts(
        session: AsyncSession, activity_id: int, size: int = 20
    ) -> List[ActThreadPost]:
        stmt = (
            select(ActThreadPost)
            .where(ActThreadPost.activity_id == activity_id)
            .order_by(ActThreadPost.id.desc())
            .limit(size)
        )
        return (await session.exec(stmt)).all()

    @staticmethod
    async def create_post(
        session: AsyncSession,
        activity_id: int,
        author_id: int,
        content: str,
        display_anonymous: bool = False,
        parent_id: int | None = None,
    ) -> ActThreadPost:
        post = ActThreadPost(
            activity_id=activity_id,
            author_id=author_id,
            content=content,
            display_anonymous=display_anonymous,
            parent_id=parent_id,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

