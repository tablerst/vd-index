"""
日常动态（Daily Posts）API 路由骨架
"""
from __future__ import annotations
import math
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session, get_auth_service, get_cache_service, get_config_service
from services.auth.utils import get_current_active_user
from services.database.models import DailyPostCRUD, DailyPostCreate, DailyPostUpdate
from services.database.models.user import UserCRUD
from services.database.models.member import MemberCRUD


logger = logging.getLogger(__name__)

router = APIRouter(tags=["daily"])  # 前缀由 api.router v1 统一加 /api/v1

from schema.daily import (
    DailyPostListResponse,
    DailyPostItem,
    UploadImagesResponse,
)


async def _get_author_info(session: AsyncSession, author_user_id: int):
    """根据 author_user_id 返回 (display_name, avatar_url)
    - 若用户绑定了 member_id，则使用成员的 display_name 和 /api/v1/avatar/{member_id}
    - 否则：display_name 回退为用户名，avatar_url 为 None
    """
    try:
        user = await UserCRUD.get_by_id(session, author_user_id)
        if not user:
            return None, None
        display_name = getattr(user, "username", None)
        avatar_url = None
        member_id = getattr(user, "member_id", None)
        if member_id:
            member = await MemberCRUD.get_by_id(session, member_id)
            if member:
                display_name = getattr(member, "display_name", display_name)
                avatar_url = f"/api/v1/avatar/{member.id}"
        return display_name, avatar_url
    except Exception:
        return None, None


async def _to_post_item(session: AsyncSession, post) -> DailyPostItem:
    base = post.model_dump()
    name, avatar = await _get_author_info(session, post.author_user_id)
    if name is not None:
        base["author_display_name"] = name
    if avatar is not None:
        base["author_avatar_url"] = avatar
    return DailyPostItem(**base)


@router.get(
    "/daily/trending",
    response_model=list[DailyPostItem],
    summary="获取首页精选动态（trending）",
)
async def get_trending(
    limit: int = Query(12, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """获取首页精选动态（带缓存）

    Cache key strategy:
    - Use namespaced key with parameter(s) to avoid collision: daily:trending:limit:{limit}
    TTL strategy:
    - Use settings.cache_default_ttl to balance freshness and performance.
    """
    cache_key = f"daily:trending:limit:{limit}"

    # Try to return from cache first
    try:
        cache_service = get_cache_service()
        cached_items = await cache_service.get(cache_key)
        if cached_items is not None:
            return cached_items
    except Exception as e:
        # Cache failure should not break the main flow
        logger.warning(f"Failed to get trending from cache: {e}")

    # Cache miss: query database and build response
    posts = await DailyPostCRUD.list_trending(session, limit=limit)
    items = [await _to_post_item(session, p) for p in posts]

    # Write to cache with configured TTL
    try:
        cache_service = get_cache_service()
        config_service = get_config_service()
        settings = config_service.get_settings()
        await cache_service.set(cache_key, items, ttl=settings.cache_default_ttl)
    except Exception as e:
        logger.warning(f"Failed to cache trending items: {e}")

    return items


@router.get(
    "/daily/posts",
    response_model=DailyPostListResponse,
    summary="获取日常动态列表"
)
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tag: Optional[str] = None,
    author_user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    posts, total = await DailyPostCRUD.list_paginated(
        session=session,
        page=page,
        page_size=page_size,
        tag=tag,
        author_user_id=author_user_id,
        published_only=True,
    )
    total_pages = math.ceil(total / page_size) if page_size else 1
    items = [await _to_post_item(session, p) for p in posts]
    return DailyPostListResponse(
        posts=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/daily/posts/{post_id}",
    response_model=DailyPostItem,
    summary="获取日常动态详情（并自增浏览量）"
)
async def get_post_detail(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    post = await DailyPostCRUD.get_by_id(session, post_id)
    if not post or (post and not post.published):
        raise HTTPException(status_code=404, detail="Post not found")
    await DailyPostCRUD.increment_views(session, post_id)
    return await _to_post_item(session, post)


@router.post(
    "/daily/posts",
    summary="创建日常动态（鉴权）"
)
async def create_post(
    payload: DailyPostCreate,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    post = await DailyPostCRUD.create(session, payload, author_user_id=current_user.id)
    return post


@router.patch(
    "/daily/posts/{post_id}",
    summary="更新日常动态（作者或管理员）"
)
async def update_post(
    post_id: int,
    payload: DailyPostUpdate,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    post = await DailyPostCRUD.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    updated = await DailyPostCRUD.update(session, post_id, payload)
    return updated


@router.delete(
    "/daily/posts/{post_id}",
    summary="删除日常动态（作者或管理员）"
)
async def delete_post(
    post_id: int,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    post = await DailyPostCRUD.get_by_id(session, post_id)
    if not post:
        return {"success": False}
    if post.author_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    ok = await DailyPostCRUD.delete(session, post_id)
    return {"success": ok}


@router.post(
    "/daily/upload",
    response_model=UploadImagesResponse,
    summary="上传日常动态图片（鉴权）"
)
async def upload_images(
    images: List[UploadFile] = File(...),
    current_user=Depends(get_current_active_user),
):
    # 保存到 /static/pics/yyyy/mm 并返回 URL
    from utils.uploads import save_upload_images
    saved = await save_upload_images(images)
    return {
        "files": [
            {"name": name, "url": url, "width": width, "height": height}
            for (name, url, width, height) in saved
        ]
    }

