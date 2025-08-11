"""
CRUD operations for DailyPost
"""
from __future__ import annotations
from typing import List, Optional, Tuple

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import DailyPost, DailyPostCreate, DailyPostUpdate


class DailyPostCRUD:
    """CRUD utilities for DailyPost."""

    @staticmethod
    async def create(session: AsyncSession, data: DailyPostCreate, author_user_id: int) -> DailyPost:
        post = DailyPost(
            author_user_id=author_user_id,
            **data.model_dump(),
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def get_by_id(session: AsyncSession, post_id: int) -> Optional[DailyPost]:
        return await session.get(DailyPost, post_id)

    @staticmethod
    async def update(session: AsyncSession, post_id: int, data: DailyPostUpdate) -> Optional[DailyPost]:
        post = await session.get(DailyPost, post_id)
        if not post:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(post, k, v)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, post_id: int) -> bool:
        post = await session.get(DailyPost, post_id)
        if not post:
            return False
        await session.delete(post)
        await session.commit()
        return True

    @staticmethod
    async def list_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        tag: Optional[str] = None,
        author_user_id: Optional[int] = None,
        published_only: bool = True,
    ) -> Tuple[List[DailyPost], int]:
        stmt = select(DailyPost)
        if published_only:
            stmt = stmt.where(DailyPost.published == True)
        # TODO: tag 过滤可在后续使用 JSONB 操作符实现（避免跨数据库不兼容问题）
        if author_user_id:
            stmt = stmt.where(DailyPost.author_user_id == author_user_id)
        from sqlmodel import func as sf
        total_stmt = stmt.with_only_columns(sf.count())
        total = (await session.exec(total_stmt)).one()
        stmt = stmt.order_by(DailyPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        results = (await session.exec(stmt)).all()
        return results, total

    @staticmethod
    async def list_trending(session: AsyncSession, limit: int = 12) -> List[DailyPost]:
        stmt = (
            select(DailyPost)
            .where(DailyPost.published == True)
            .order_by(DailyPost.views_count.desc(), DailyPost.created_at.desc())
            .limit(limit)
        )
        return (await session.exec(stmt)).all()

    @staticmethod
    async def increment_views(session: AsyncSession, post_id: int) -> Optional[int]:
        post = await session.get(DailyPost, post_id)
        if not post:
            return None
        post.views_count += 1
        await session.commit()
        return post.views_count

