"""
DailyPostComment CRUD 操作
- 支持按帖子分页获取（顶层+子回复）
- 创建/点赞/点踩/软删除
- 同步 DailyPost.comments_count 计数
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_

from ..daily_post.base import DailyPost
from .base import DailyPostComment, DailyPostCommentCreate, DailyPostCommentUpdate
from ..base import now_naive


class DailyPostCommentCRUD:
    """每日帖评论 CRUD"""

    @staticmethod
    async def create(session: AsyncSession, data: DailyPostCommentCreate, author_user_id: int) -> DailyPostComment:
        comment = DailyPostComment(
            post_id=data.post_id,
            author_user_id=author_user_id,
            parent_id=data.parent_id,
            content=data.content,
            author_ip=data.author_ip,
        )
        session.add(comment)

        # 同步帖子评论计数
        post = await session.get(DailyPost, data.post_id)
        if post:
            post.comments_count += 1
            post.updated_at = now_naive()

        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def get_by_id(session: AsyncSession, comment_id: int) -> Optional[DailyPostComment]:
        return await session.get(DailyPostComment, comment_id)

    @staticmethod
    async def list_top_with_children(
        session: AsyncSession,
        post_id: int,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
    ) -> Tuple[List[DailyPostComment], int, Dict[int, List[DailyPostComment]]]:
        """分页获取顶层评论，并附带其子回复列表。
        返回: (top_level_comments, total_top_level, children_map)
        """
        # 统计顶层评论总数
        count_stmt = select(func.count(DailyPostComment.id)).where(
            DailyPostComment.post_id == post_id,
            DailyPostComment.parent_id.is_(None),
        )
        if not include_deleted:
            count_stmt = count_stmt.where(DailyPostComment.is_deleted == False)  # noqa: E712
        total_top = (await session.execute(count_stmt)).scalar() or 0

        # 查询顶层评论
        offset = (page - 1) * page_size
        top_stmt = (
            select(DailyPostComment)
            .where(
                DailyPostComment.post_id == post_id,
                DailyPostComment.parent_id.is_(None),
            )
            .order_by(desc(DailyPostComment.created_at))
            .offset(offset)
            .limit(page_size)
        )
        if not include_deleted:
            top_stmt = top_stmt.where(DailyPostComment.is_deleted == False)  # noqa: E712
        top_res = await session.execute(top_stmt)
        top_comments = list(top_res.scalars().all())

        if not top_comments:
            return [], total_top, {}

        # 查询这些顶层评论的所有子回复（仅一层，足够实现楼中楼 V1）
        top_ids = [c.id for c in top_comments if c.id is not None]
        child_stmt = select(DailyPostComment).where(
            DailyPostComment.post_id == post_id,
            DailyPostComment.parent_id.in_(top_ids),
        ).order_by(DailyPostComment.created_at.asc())
        if not include_deleted:
            child_stmt = child_stmt.where(DailyPostComment.is_deleted == False)  # noqa: E712
        child_res = await session.execute(child_stmt)
        children = list(child_res.scalars().all())

        children_map: Dict[int, List[DailyPostComment]] = {}
        for ch in children:
            if ch.parent_id is None:
                continue
            children_map.setdefault(ch.parent_id, []).append(ch)

        return top_comments, total_top, children_map

    @staticmethod
    async def like(session: AsyncSession, comment_id: int) -> Optional[DailyPostComment]:
        c = await session.get(DailyPostComment, comment_id)
        if not c or c.is_deleted:
            return None
        c.likes += 1
        c.updated_at = now_naive()
        await session.commit()
        await session.refresh(c)
        return c

    @staticmethod
    async def dislike(session: AsyncSession, comment_id: int) -> Optional[DailyPostComment]:
        c = await session.get(DailyPostComment, comment_id)
        if not c or c.is_deleted:
            return None
        c.dislikes += 1
        c.updated_at = now_naive()
        await session.commit()
        await session.refresh(c)
        return c

    @staticmethod
    async def soft_delete(session: AsyncSession, comment_id: int) -> Optional[DailyPostComment]:
        c = await session.get(DailyPostComment, comment_id)
        if not c or c.is_deleted:
            return None
        c.is_deleted = True
        c.updated_at = now_naive()
        # 同步帖子评论计数
        post = await session.get(DailyPost, c.post_id)
        if post and post.comments_count > 0:
            post.comments_count -= 1
            post.updated_at = now_naive()
        await session.commit()
        await session.refresh(c)
        return c

