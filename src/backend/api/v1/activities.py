"""
活动相关API路由
"""
import math
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from services.auth.utils import require_admin
from services.database.models.activity import ActivityCRUD, ActivityCreate, ActivityUpdate
from services.database.models.member import MemberCRUD
from schema.activity_schemas import (
    ActivityResponse, ActivityListResponse, ActivityStatsResponse,
    ActivityCreateRequest, ActivityUpdateRequest, ApiResponse, ParticipantInfo
)

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(tags=["activities"])


async def build_activity_response(activity, session: AsyncSession) -> ActivityResponse:
    """构建活动响应对象，包含参与者信息（优化版本）"""
    participants = []

    # 批量获取参与者详细信息（使用缓存优化）
    if activity.participant_ids:
        members_dict = await MemberCRUD.get_many_by_ids(session, activity.participant_ids)

        # 按原始顺序构建参与者列表
        for member_id in activity.participant_ids:
            member = members_dict.get(member_id)
            if member:
                participants.append(ParticipantInfo(
                    id=member.id,
                    name=member.display_name,
                    avatar_url=f"/api/v1/avatar/{member.id}"
                ))

    return ActivityResponse(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        date=activity.date,
        tags=activity.tags,
        participants=participants,
        participants_total=activity.participants_total,
        created_at=activity.created_at,
        updated_at=activity.updated_at
    )


@router.get(
    "/star_calendar/activities",
    response_model=ActivityListResponse,
    summary="获取活动列表",
    description="分页获取活动列表，包含参与者信息"
)
async def get_activities(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页大小"),
    session: AsyncSession = Depends(get_session)
):
    """获取活动列表"""
    try:
        # 获取活动总数
        total = await ActivityCRUD.count_total(session)
        
        # 获取活动列表
        activities, total = await ActivityCRUD.get_paginated(session, page=page, page_size=page_size)

        # 计算分页
        total_pages = math.ceil(total / page_size)
        
        # 构建响应
        activity_responses = []
        for activity in activities:
            activity_response = await build_activity_response(activity, session)
            activity_responses.append(activity_response)
        
        return ActivityListResponse(
            activities=activity_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        logger.error(f"获取活动列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活动列表失败: {str(e)}")


@router.get(
    "/star_calendar/activities/stats",
    response_model=ActivityStatsResponse,
    summary="获取活动统计信息",
    description="获取活动总数、参与人次等统计信息"
)
async def get_activity_stats(session: AsyncSession = Depends(get_session)):
    """获取活动统计信息（带缓存）"""
    try:
        from services.deps import get_cache_service

        # 尝试从缓存获取
        cache_key = "activity:stats:all"
        try:
            cache_service = get_cache_service()
            cached_stats = await cache_service.get(cache_key)
            if cached_stats is not None:
                return cached_stats
        except Exception as e:
            logger.warning(f"Failed to get activity stats from cache: {e}")

        # 缓存未命中，从数据库获取
        # 获取活动总数
        total_activities = await ActivityCRUD.count_total(session)

        # 获取所有活动
        all_activities = await ActivityCRUD.get_all(session)

        # 计算总参与人次
        total_participants = sum(activity.participants_total for activity in all_activities)

        # 计算独立参与成员数
        unique_participant_ids = set()
        for activity in all_activities:
            unique_participant_ids.update(activity.participant_ids)
        unique_participants = len(unique_participant_ids)

        stats_response = ActivityStatsResponse(
            total_activities=total_activities,
            total_participants=total_participants,
            unique_participants=unique_participants
        )

        # 缓存结果（使用配置的统计TTL）
        try:
            cache_service = get_cache_service()
            from services.deps import get_config_service
            config_service = get_config_service()
            settings = config_service.get_settings()
            await cache_service.set(cache_key, stats_response, ttl=settings.cache_stats_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache activity stats: {e}")

        return stats_response

    except Exception as e:
        logger.error(f"获取活动统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活动统计信息失败: {str(e)}")


@router.get(
    "/star_calendar/activity/{activity_id}",
    response_model=ActivityResponse,
    summary="获取单个活动详情",
    description="根据活动ID获取单个活动的详细信息"
)
async def get_activity(
    activity_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取单个活动详情"""
    try:
        activity = await ActivityCRUD.get_by_id(session, activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        return await build_activity_response(activity, session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取活动详情失败: {str(e)}")


@router.post(
    "/star_calendar/activity/create",
    response_model=ActivityResponse,
    summary="创建新活动",
    description="创建新的活动记录"
)
async def create_activity(
    activity_data: ActivityCreateRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """创建新活动"""
    try:
        # 验证参与成员是否存在
        for member_id in activity_data.participant_ids:
            member = await MemberCRUD.get_by_id(session, member_id)
            if not member:
                raise HTTPException(status_code=400, detail=f"成员ID {member_id} 不存在")
        
        # 创建活动
        activity_create = ActivityCreate(**activity_data.model_dump())
        activity = await ActivityCRUD.create(session, activity_create)
        
        return await build_activity_response(activity, session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建活动失败: {str(e)}")


@router.put(
    "/star_calendar/activity/update/{activity_id}",
    response_model=ActivityResponse,
    summary="更新活动",
    description="更新指定活动的信息"
)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdateRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """更新活动"""
    try:
        # 检查活动是否存在
        existing_activity = await ActivityCRUD.get_by_id(session, activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 验证参与成员是否存在（如果提供了）
        if activity_data.participant_ids is not None:
            for member_id in activity_data.participant_ids:
                member = await MemberCRUD.get_by_id(session, member_id)
                if not member:
                    raise HTTPException(status_code=400, detail=f"成员ID {member_id} 不存在")
        
        # 更新活动
        activity_update = ActivityUpdate(**activity_data.model_dump(exclude_unset=True))
        updated_activity = await ActivityCRUD.update(session, activity_id, activity_update)
        
        if not updated_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        return await build_activity_response(updated_activity, session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新活动失败: {str(e)}")


@router.delete(
    "/star_calendar/activity/delete/{activity_id}",
    response_model=ApiResponse,
    summary="删除活动",
    description="删除指定的活动"
)
async def delete_activity(
    activity_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """删除活动"""
    try:
        # 检查活动是否存在
        existing_activity = await ActivityCRUD.get_by_id(session, activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 删除活动
        success = await ActivityCRUD.delete(session, activity_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        return ApiResponse(
            success=True,
            message="活动删除成功"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除活动失败: {str(e)}")
