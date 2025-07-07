"""
成员相关API路由
"""
import math
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from schema.member_schemas import (
    MemberListResponse,
    MemberDetailResponse,
    CreateMemberRequest,
    ImportMemberRequest,
    ImportBatchRequest,
    ApiResponse
)
from domain.member_service import MemberService
from services.database.models.member import MemberCreate, MemberUpdate, MemberCRUD

router = APIRouter(tags=["members"])


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
        from services.database.models.member.base import Member

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


@router.post(
    "/members",
    response_model=ApiResponse,
    summary="创建新成员",
    description="手动创建一个新的群成员记录"
)
async def create_member(
    member_data: CreateMemberRequest,
    session: AsyncSession = Depends(get_session)
):
    """手动创建新成员"""
    try:
        from services.database.models.member.base import Member
        from datetime import datetime
        import secrets

        # 生成随机UIN（用于测试，实际应该是真实QQ号）
        fake_uin = secrets.randbelow(900000000) + 100000000

        # 生成随机salt（16字节hex）
        salt = secrets.token_hex(16)

        # 创建成员对象
        member = Member(
            uin_encrypted=str(fake_uin),  # 这里应该加密，但为了简化先用明文
            salt=salt,  # 添加必需的salt字段
            display_name=member_data.display_name,
            group_nick=member_data.group_nick or member_data.display_name,
            qq_nick=member_data.display_name,
            role=member_data.role,
            join_time=datetime.now(),
            bio=member_data.bio
        )

        session.add(member)
        await session.commit()
        await session.refresh(member)

        return ApiResponse(
            success=True,
            message="成员创建成功",
            data={"member_id": member.id}
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"创建成员失败: {str(e)}")


@router.post(
    "/members/import",
    response_model=ApiResponse,
    summary="从JSON导入成员数据",
    description="从QQ群导出的JSON数据批量导入成员记录"
)
async def import_members_from_json(
    batch_data: ImportBatchRequest,
    session: AsyncSession = Depends(get_session)
):
    """从JSON导入成员数据"""
    try:
        created_members = []
        for member_data in batch_data.members:
            member = await MemberService.import_member_from_json(session, member_data)
            created_members.append(member.id)

        return ApiResponse(
            success=True,
            message=f"批量创建成功，共创建 {len(created_members)} 个成员",
            data={"member_ids": created_members}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量创建成员失败: {str(e)}")


@router.put(
    "/members/{member_id}",
    response_model=ApiResponse,
    summary="更新成员信息",
    description="更新指定成员的信息"
)
async def update_member(
    member_id: int,
    member_data: MemberUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新成员信息"""
    if member_id < 1:
        raise HTTPException(status_code=400, detail="成员ID必须大于0")

    try:
        # 使用CRUD操作更新成员
        updated_member = await MemberCRUD.update(session, member_id, member_data)

        if not updated_member:
            raise HTTPException(status_code=404, detail="成员不存在")

        return ApiResponse(
            success=True,
            message="成员信息更新成功",
            data={"member_id": updated_member.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新成员信息失败: {str(e)}")


@router.delete(
    "/members/{member_id}",
    response_model=ApiResponse,
    summary="删除成员",
    description="删除指定的成员记录"
)
async def delete_member(
    member_id: int,
    session: AsyncSession = Depends(get_session)
):
    """删除成员"""
    if member_id < 1:
        raise HTTPException(status_code=400, detail="成员ID必须大于0")

    try:
        # 使用CRUD操作删除成员
        success = await MemberCRUD.delete(session, member_id)

        if not success:
            raise HTTPException(status_code=404, detail="成员不存在")

        return ApiResponse(
            success=True,
            message="成员删除成功",
            data={"member_id": member_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除成员失败: {str(e)}")
