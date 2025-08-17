"""
CRUD operations for DailyPost
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import DailyPost, DailyPostCreate, DailyPostUpdate

from sqlalchemy import delete as sa_delete
from ..daily_post_comment.base import DailyPostComment


class DailyPostCRUD:
    """CRUD utilities for DailyPost."""

    @staticmethod
    def _extract_from_tiptap(doc: Dict[str, Any] | None) -> tuple[Optional[str], Optional[str]]:
        """从 tiptap JSON 提取第一段纯文本与第一张图片URL。
        - 返回 (summary_text, first_image_url)
        - 若无法提取返回 (None, None)
        """
        if not doc or not isinstance(doc, dict):
            return None, None

        first_image: Optional[str] = None
        first_text: Optional[str] = None

        def walk(node: Any):
            nonlocal first_image, first_text
            if not isinstance(node, dict):
                return
            node_type = node.get('type')
            if node_type == 'image' and first_image is None:
                # tiptap Image extension usually stores src in attrs.src
                src = node.get('attrs', {}).get('src') if isinstance(node.get('attrs'), dict) else None
                if isinstance(src, str) and src:
                    first_image = src
            if node_type == 'paragraph' and first_text is None:
                # 提取 paragraph 下所有 text 节点串联（简单处理）
                texts: list[str] = []
                for child in node.get('content', []) or []:
                    if isinstance(child, dict) and child.get('type') == 'text':
                        t = child.get('text')
                        if isinstance(t, str):
                            texts.append(t)
                if texts:
                    first_text = ''.join(texts).strip()
            # 递归 children
            for child in node.get('content', []) or []:
                if isinstance(child, dict):
                    walk(child)

        walk(doc)
        return first_text or None, first_image or None

    @staticmethod
    async def create(session: AsyncSession, data: DailyPostCreate, author_user_id: int) -> DailyPost:
        payload = data.model_dump()
        content_jsonb = payload.get('content_jsonb')
        # 从 content_jsonb 提取摘要与首图
        summary, first_image = DailyPostCRUD._extract_from_tiptap(content_jsonb)

        # 回填旧字段（兼容）
        if summary:
            payload['content'] = summary[:2000]
        if first_image:
            payload['images'] = [first_image]
        # 若无 content_jsonb 则沿用传入的 content/images

        post = DailyPost(
            author_user_id=author_user_id,
            **payload,
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

        # 若传入 content_jsonb 则自动提取并更新摘要与首图
        if 'content_jsonb' in update_data and update_data.get('content_jsonb') is not None:
            summary, first_image = DailyPostCRUD._extract_from_tiptap(update_data.get('content_jsonb'))
            if summary is not None:
                update_data['content'] = summary[:2000]
            # 重置 images 为仅首图，或保留原有其余？本次实现：以首图为主
            if first_image is not None:
                update_data['images'] = [first_image]

        for k, v in update_data.items():
            setattr(post, k, v)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, post_id: int) -> bool:
        """
        删除帖子并级联清理其下的所有评论（物理删除）。
        中文注释：由于数据库外键未设置 ON DELETE CASCADE，需在业务层手动删除关联评论，避免外键约束错误。
        """
        post = await session.get(DailyPost, post_id)
        if not post:
            return False
        # 先删除关联评论
        await session.execute(
            sa_delete(DailyPostComment).where(DailyPostComment.post_id == post_id)
        )
        # 再删除帖子
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

