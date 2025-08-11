"""
成员相关API路由
"""
import math
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from services.auth.utils import require_admin
from schema.member import (
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
    """获取成员统计信息（带缓存）"""
    try:
        from sqlmodel import select, func
        from services.database.models.member.base import Member
        from services.deps import get_cache_service

        # 尝试从缓存获取
        cache_key = "member:stats:all"
        try:
            cache_service = get_cache_service()
            cached_stats = await cache_service.get(cache_key)
            if cached_stats is not None:
                return cached_stats
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to get member stats from cache: {e}")

        # 缓存未命中，从数据库获取
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

        stats_response = {
            "total_members": total_members,
            "role_distribution": role_counts,
            "join_year_stats": join_year_stats
        }

        # 缓存结果（使用配置的统计TTL）
        try:
            cache_service = get_cache_service()
            from services.deps import get_config_service
            config_service = get_config_service()
            settings = config_service.get_settings()
            await cache_service.set(cache_key, stats_response, ttl=settings.cache_stats_ttl)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to cache member stats: {e}")

        return stats_response

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
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
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
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """从JSON导入成员数据（存在则更新，不存在则创建）"""
    try:
        result = await MemberService.upsert_members_from_json(session, batch_data.members)
        created_cnt = len(result.get("created_ids", []))
        updated_cnt = len(result.get("updated_ids", []))

        # 批量下载头像（新建+更新）
        try:
            from utils.avatar import AvatarService
            updated_uins = result.get("updated_uins", [])
            created_uins = [d.get("uin") for d in result.get("created_details", []) if d.get("uin")]
            target_uins = list({*updated_uins, *created_uins})
            if target_uins:
                await AvatarService.batch_fetch_and_save_avatars_webp(target_uins)
        except Exception:
            pass

        # 退群清理
        try:
            latest_uins = [m.uin for m in batch_data.members]
            departures = await MemberService.reconcile_departures(session, latest_uins)
        except Exception:
            departures = {"deleted": 0}

        return ApiResponse(
            success=True,
            message=f"导入完成：创建 {created_cnt} 个，更新 {updated_cnt} 个，清理 {departures.get('deleted', 0)} 个退群成员",
            data={**result, "departures": departures}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导入成员失败: {str(e)}")


@router.post(
    "/members/refresh-avatars",
    response_model=ApiResponse,
    summary="批量刷新所有成员头像",
    description="管理员操作：解密所有成员UIN并批量下载QQ头像为WebP"
)
async def refresh_all_member_avatars(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """批量刷新头像：
    - 加载所有成员
    - 解密UIN
    - AvatarService 批量下载保存
    - 返回统计结果
    """
    try:
        from services.database.models.member import MemberCRUD
        from services.deps import get_crypto_service
        from utils.avatar import AvatarService

        # 加载全部成员
        members = await MemberCRUD.get_all(session)

        # 解密出全部UIN
        crypto = get_crypto_service()
        uins = []
        for m in members:
            try:
                u = crypto.decrypt_uin(m.uin_encrypted, m.salt)
                if u:
                    uins.append(int(u))
            except Exception:
                # 解密失败跳过该成员
                continue

        # 批量下载
        stats = await AvatarService.batch_fetch_and_save_avatars_webp(uins)

        return ApiResponse(
            success=True,
            message=f"头像刷新完成：成功 {stats.get('success', 0)}，失败 {stats.get('failed', 0)}，共 {stats.get('total', 0)}",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量刷新头像失败: {str(e)}")


@router.put(
    "/members/{member_id}",
    response_model=ApiResponse,
    summary="更新成员信息",
    description="更新指定成员的信息"
)
async def update_member(
    member_id: int,
    member_data: MemberUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
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
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
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


# ---------------- 迁移自 admin：成员导入相关接口（保留管理员鉴权） ---------------- #
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import UploadFile, File
from utils.avatar import AvatarService
from utils.qq_group.fetcher import fetch_members, QQGroupFetcherError


class QQImportParams(BaseModel):
    """通过QQ群官网获取成员的参数"""
    group_id: str = Field(..., description="群号")
    cookie: str = Field(..., description="Cookie")
    bkn: str = Field(..., description="bkn 参数")
    user_agent: Optional[str] = Field(default="Apifox/1.0.0 (https://apifox.com)")
    page_size: Optional[int] = Field(default=10, ge=1, le=200)
    request_delay: Optional[float] = Field(default=0.5, ge=0, le=5)


@router.post(
    "/members/import-file",
    response_model=ApiResponse,
    summary="上传JSON文件导入",
    description="上传QQ群成员JSON文件进行批量导入（存在则更新，不存在则创建）"
)
async def import_members_from_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """从上传的JSON文件导入成员（迁移自 admin）"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON文件")

    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))

        if 'mems' not in data:
            raise HTTPException(status_code=400, detail="JSON文件格式错误，缺少mems字段")

        members_data: List[ImportMemberRequest] = []
        for mem in data['mems']:
            members_data.append(ImportMemberRequest(
                uin=mem['uin'],
                role=mem['role'],
                join_time=mem['join_time'],
                last_speak_time=mem.get('last_speak_time'),
                card=mem['card'],
                nick=mem['nick'],
                lv=mem.get('lv', {}),
                qage=mem.get('qage', 0),
            ))

        # 复用已有导入逻辑
        result = await MemberService.upsert_members_from_json(session, members_data)
        created_cnt = len(result.get("created_ids", []))
        updated_cnt = len(result.get("updated_ids", []))

        # 下载头像
        try:
            updated_uins = result.get("updated_uins", [])
            created_uins = [d.get("uin") for d in result.get("created_details", []) if d.get("uin")]
            target_uins = list({*updated_uins, *created_uins})
            if target_uins:
                await AvatarService.batch_fetch_and_save_avatars_webp(target_uins)
        except Exception:
            pass

        # 退群清理
        try:
            latest_uins = [m.uin for m in members_data]
            departures = await MemberService.reconcile_departures(session, latest_uins)
        except Exception:
            departures = {"deleted": 0}

        return ApiResponse(
            success=True,
            message=f"导入完成：创建 {created_cnt} 个，更新 {updated_cnt} 个，清理 {departures.get('deleted', 0)} 个退群成员",
            data={**result, "departures": departures}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件导入失败: {str(e)}")


@router.post(
    "/members/import-from-qq",
    response_model=ApiResponse,
    summary="通过QQ群官网获取并导入成员",
    description="通过 Cookie 等参数从 qun.qq.com 获取成员数据后执行批量导入（存在则更新，不存在则创建）"
)
async def import_members_from_qq(
    params: QQImportParams,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """通过QQ群抓取后导入（迁移自 admin）"""
    try:
        raw = await fetch_members(
            group_id=params.group_id,
            cookie=params.cookie,
            bkn=params.bkn,
            user_agent=params.user_agent or "Apifox/1.0.0 (https://apifox.com)",
            page_size=params.page_size or 10,
            request_delay=params.request_delay or 0.5,
        )
        mems = raw.get("mems", [])
        members_data: List[ImportMemberRequest] = []
        for mem in mems:
            members_data.append(ImportMemberRequest(
                uin=mem['uin'],
                role=mem['role'],
                join_time=mem['join_time'],
                last_speak_time=mem.get('last_speak_time'),
                card=mem['card'],
                nick=mem['nick'],
                lv=mem.get('lv', {}),
                qage=mem.get('qage', 0),
            ))

        result = await MemberService.upsert_members_from_json(session, members_data)
        created_ids = result.get("created_ids", [])
        updated_ids = result.get("updated_ids", [])

        # 下载头像
        try:
            updated_uins = result.get("updated_uins", [])
            created_details = result.get("created_details", [])
            created_uins = [d.get("uin") for d in created_details if d.get("uin")]
            target_uins = list({*updated_uins, *created_uins})
            if target_uins:
                await AvatarService.batch_fetch_and_save_avatars_webp(target_uins)
        except Exception:
            pass

        # 清理退群
        try:
            latest_uins = [m.uin for m in members_data]
            departures = await MemberService.reconcile_departures(session, latest_uins)
        except Exception:
            departures = {"deleted": 0}

        return ApiResponse(
            success=True,
            message=f"导入完成：创建 {len(created_ids)} 个，更新 {len(updated_ids)} 个，清理 {departures.get('deleted', 0)} 个退群成员",
            data={**result, "departures": departures, "source": "qq", "group_id": params.group_id, "fetched_count": len(members_data)}
        )
    except QQGroupFetcherError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"从QQ群获取或导入失败: {str(e)}")
