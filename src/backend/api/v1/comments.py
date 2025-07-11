"""
评论相关API路由
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.deps import get_session
from services.auth.utils import require_admin
from services.database.models import CommentCRUD, CommentCreate, MemberCRUD
from schema.comment_schemas import (
    CommentResponse, 
    CommentCreateRequest, 
    CommentListResponse, 
    CommentActionResponse,
    CommentStatsResponse,
    CommentModerationResponse,
    ErrorResponse
)

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    responses={404: {"model": ErrorResponse}},
)


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/members/{member_id}/comments", response_model=CommentListResponse)
async def get_member_comments(
    member_id: int,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_session)
):
    """获取某成员的评论列表"""
    # 验证成员是否存在
    member = await MemberCRUD.get_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # 参数验证
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    # 获取评论列表
    comments = await CommentCRUD.get_by_member_id(db, member_id, page, page_size)
    total = await CommentCRUD.count_by_member_id(db, member_id)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # 转换为响应模型
    comment_responses = [
        CommentResponse(
            id=comment.id,
            member_id=comment.member_id,
            content=comment.content,
            likes=comment.likes,
            dislikes=comment.dislikes,
            is_anonymous=comment.is_anonymous,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        for comment in comments
    ]
    
    return CommentListResponse(
        comments=comment_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/members/{member_id}/comments", response_model=CommentResponse)
async def create_comment(
    member_id: int,
    comment_data: CommentCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """为成员创建匿名评论"""
    # 验证成员是否存在
    member = await MemberCRUD.get_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # 获取客户端IP
    client_ip = get_client_ip(request)
    
    # 创建评论数据
    create_data = CommentCreate(
        member_id=member_id,
        content=comment_data.content.strip(),
        is_anonymous=comment_data.is_anonymous,
        author_ip=client_ip
    )
    
    # 创建评论
    comment = await CommentCRUD.create(db, create_data)
    
    return CommentResponse(
        id=comment.id,
        member_id=comment.member_id,
        content=comment.content,
        likes=comment.likes,
        dislikes=comment.dislikes,
        is_anonymous=comment.is_anonymous,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@router.put("/{comment_id}/like", response_model=CommentActionResponse)
async def like_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_session)
):
    """点赞评论"""
    comment = await CommentCRUD.like_comment(db, comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or has been deleted"
        )
    
    comment_response = CommentResponse(
        id=comment.id,
        member_id=comment.member_id,
        content=comment.content,
        likes=comment.likes,
        dislikes=comment.dislikes,
        is_anonymous=comment.is_anonymous,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )
    
    return CommentActionResponse(
        success=True,
        message="Comment liked successfully",
        comment=comment_response
    )


@router.put("/{comment_id}/dislike", response_model=CommentActionResponse)
async def dislike_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_session)
):
    """点踩评论"""
    comment = await CommentCRUD.dislike_comment(db, comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or has been deleted"
        )
    
    comment_response = CommentResponse(
        id=comment.id,
        member_id=comment.member_id,
        content=comment.content,
        likes=comment.likes,
        dislikes=comment.dislikes,
        is_anonymous=comment.is_anonymous,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )
    
    return CommentActionResponse(
        success=True,
        message="Comment disliked successfully",
        comment=comment_response
    )


@router.delete("/{comment_id}", response_model=CommentActionResponse)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin)
):
    """删除评论（管理员功能）"""
    comment = await CommentCRUD.soft_delete(db, comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return CommentActionResponse(
        success=True,
        message="Comment deleted successfully",
        comment=None
    )


@router.get("/stats", response_model=CommentStatsResponse)
async def get_comment_stats(
    db: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin)
):
    """获取评论统计信息（管理员功能）"""
    stats = await CommentCRUD.get_stats(db)
    
    return CommentStatsResponse(
        total_comments=stats.total_comments,
        total_likes=stats.total_likes,
        total_dislikes=stats.total_dislikes,
        active_comments=stats.active_comments,
        deleted_comments=stats.deleted_comments
    )


@router.get("/moderation", response_model=CommentModerationResponse)
async def get_high_dislike_comments(
    threshold: int = 10,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_session),
    _: None = Depends(require_admin)
):
    """获取高点踩数的评论（管理员功能）"""
    if threshold < 1:
        threshold = 10
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    comments = await CommentCRUD.get_high_dislike_comments(db, threshold, page, page_size)
    
    comment_responses = [
        CommentResponse(
            id=comment.id,
            member_id=comment.member_id,
            content=comment.content,
            likes=comment.likes,
            dislikes=comment.dislikes,
            is_anonymous=comment.is_anonymous,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        for comment in comments
    ]
    
    return CommentModerationResponse(
        high_dislike_comments=comment_responses,
        total=len(comment_responses),
        threshold=threshold
    )
