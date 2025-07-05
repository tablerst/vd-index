"""
成员相关API路由
"""
import math
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from schema.member_schemas import MemberListResponse, MemberDetailResponse
from domain.member_service import MemberService

router = APIRouter(prefix="/api", tags=["members"])


@router.get(
    "/members",
    response_model=MemberListResponse,
    summary="获取成员列表",
    description="分页获取群成员列表，返回安全的代理ID和基本信息"
)
async def get_members(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """获取成员列表"""
    # 验证分页参数
    if page < 1:
        raise HTTPException(status_code=400, detail="页码必须大于0")
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="每页大小必须在1-100之间")
    
    try:
        # 构建基础URL
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # 获取成员列表
        members, total = await MemberService.get_members_paginated(
            session=session,
            page=page,
            page_size=page_size,
            base_url=base_url
        )
        
        # 计算总页数
        total_pages = math.ceil(total / page_size)
        
        return MemberListResponse(
            members=members,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员列表失败: {str(e)}")


@router.get(
    "/members/stats",
    summary="获取成员统计信息",
    description="获取群成员的统计信息"
)
async def get_member_stats(session: AsyncSession = Depends(get_session)):
    """获取成员统计信息"""
    try:
        from sqlmodel import select, func
        from backend.services.database.models.member import Member

        # 总成员数
        total_statement = select(func.count(Member.id))
        total_result = await session.exec(total_statement)
        total_members = total_result.one()

        # 按角色统计
        role_statement = select(Member.role, func.count(Member.id)).group_by(Member.role)
        role_result = await session.exec(role_statement)
        role_stats = role_result.all()

        role_counts = {
            "群主": 0,
            "管理员": 0,
            "群员": 0
        }

        for role, count in role_stats:
            if role == 0:
                role_counts["群主"] = count
            elif role == 1:
                role_counts["管理员"] = count
            elif role == 2:
                role_counts["群员"] = count

        # 按年份统计入群人数 (PostgreSQL兼容)
        year_statement = select(
            func.extract('year', Member.join_time).label('year'),
            func.count(Member.id).label('count')
        ).group_by(func.extract('year', Member.join_time))

        year_result = await session.exec(year_statement)
        year_stats = year_result.all()
        join_year_stats = {int(year): count for year, count in year_stats}

        return {
            "total_members": total_members,
            "role_distribution": role_counts,
            "join_year_stats": join_year_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get(
    "/members/{member_id}",
    response_model=MemberDetailResponse,
    summary="获取成员详情",
    description="根据代理ID获取单个成员的详细信息"
)
async def get_member_detail(
    member_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """获取成员详情"""
    if member_id < 1:
        raise HTTPException(status_code=400, detail="成员ID必须大于0")

    try:
        # 构建基础URL
        base_url = f"{request.url.scheme}://{request.url.netloc}"

        # 获取成员详情
        member = await MemberService.get_member_by_id(
            session=session,
            member_id=member_id,
            base_url=base_url
        )

        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        return member

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成员详情失败: {str(e)}")
