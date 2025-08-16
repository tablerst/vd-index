"""
DailyPost 评论 API 路由
"""
from __future__ import annotations
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from services.auth.utils import get_current_active_user
from services.database.models.daily_post_comment.crud import DailyPostCommentCRUD
from services.database.models.daily_post_comment.base import DailyPostCommentCreate
from services.database.models import DailyPostCRUD
from schema.daily_comment import (
    DailyCommentItem,
    DailyCommentListResponse,
    DailyCommentCreateRequest,
    DailyCommentActionResponse,
)

router = APIRouter(prefix="/daily", tags=["daily-comments"])  # 统一由 api.router 加 /api/v1


@router.get(
    "/posts/{post_id}/comments",
    response_model=DailyCommentListResponse,
    summary="获取某帖子下的评论（顶层+子回复）",
)
async def list_post_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_deleted: bool = False,
    session: AsyncSession = Depends(get_session),
):
    # 帖子存在性校验
    post = await DailyPostCRUD.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    tops, total, children_map = await DailyPostCommentCRUD.list_top_with_children(
        session, post_id=post_id, page=page, page_size=page_size, include_deleted=include_deleted
    )

    # 转换为 schema
    def to_item(c) -> DailyCommentItem:
        return DailyCommentItem(**c.model_dump())

    top_items = [to_item(c) for c in tops]
    children_items = {k: [to_item(c) for c in v] for k, v in children_map.items()}

    total_pages = math.ceil(total / page_size) if page_size else 1
    return DailyCommentListResponse(
        top_comments=top_items,
        children_map=children_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/posts/{post_id}/comments",
    response_model=DailyCommentItem,
    summary="创建评论或回复（鉴权）",
)
async def create_post_comment(
    post_id: int,
    payload: DailyCommentCreateRequest,
    request: Request,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    # 存在性
    post = await DailyPostCRUD.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # 构造创建模型
    author_ip = request.client.host if request and request.client else None
    create_data = DailyPostCommentCreate(
        post_id=post_id,
        content=payload.content,
        parent_id=payload.parent_id,
        author_ip=author_ip,
    )
    c = await DailyPostCommentCRUD.create(session, create_data, author_user_id=current_user.id)
    return DailyCommentItem(**c.model_dump())


@router.put(
    "/comments/{comment_id}/like",
    response_model=DailyCommentActionResponse,
    summary="点赞评论（鉴权）",
)
async def like_comment(
    comment_id: int,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    c = await DailyPostCommentCRUD.like(session, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return DailyCommentActionResponse(success=True, message="liked", comment=DailyCommentItem(**c.model_dump()))


@router.put(
    "/comments/{comment_id}/dislike",
    response_model=DailyCommentActionResponse,
    summary="点踩评论（鉴权）",
)
async def dislike_comment(
    comment_id: int,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    c = await DailyPostCommentCRUD.dislike(session, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return DailyCommentActionResponse(success=True, message="disliked", comment=DailyCommentItem(**c.model_dump()))


@router.delete(
    "/comments/{comment_id}",
    response_model=DailyCommentActionResponse,
    summary="删除评论（作者或管理员，逻辑删除）",
)
async def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    c = await DailyPostCommentCRUD.get_by_id(session, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    # 权限：作者或管理员
    if c.author_user_id != current_user.id and getattr(current_user, 'role', '') != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden")

    c2 = await DailyPostCommentCRUD.soft_delete(session, comment_id)
    if not c2:
        raise HTTPException(status_code=404, detail="Comment not found")
    return DailyCommentActionResponse(success=True, message="deleted", comment=DailyCommentItem(**c2.model_dump()))

