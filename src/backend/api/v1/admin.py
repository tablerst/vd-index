"""
管理员API路由
"""
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session
from services.auth.utils import require_admin
from schema.member_schemas import ImportBatchRequest, ApiResponse, ImportMemberRequest
from domain.avatar_service import AvatarService
from domain.member_service import MemberService
from services.deps import get_crypto_service
from services.qq_group.fetcher import fetch_members, QQGroupFetcherError

router = APIRouter(prefix="/admin", tags=["admin"])


class QQImportParams(BaseModel):
    """通过QQ群官网获取成员的参数"""
    group_id: str = Field(..., description="群号")
    cookie: str = Field(..., description="Cookie")
    bkn: str = Field(..., description="bkn 参数")
    user_agent: Optional[str] = Field(default="Apifox/1.0.0 (https://apifox.com)")
    page_size: Optional[int] = Field(default=10, ge=1, le=200)
    request_delay: Optional[float] = Field(default=0.5, ge=0, le=5)


@router.post(
    "/import-json",
    response_model=ApiResponse,
    summary="导入JSON成员数据",
    description="从QQ群导出的JSON数据批量导入成员数据（存在则更新，不存在则创建）"
)
async def import_members_from_json(
    batch_request: ImportBatchRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """从JSON数据批量导入成员（Upsert）"""
    try:
        result = await MemberService.upsert_members_from_json(session, batch_request.members)
        created_ids = result.get("created_ids", [])
        updated_ids = result.get("updated_ids", [])

        # 批量下载头像（新建+更新）
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
            latest_uins = [m.uin for m in batch_request.members]
            departures = await MemberService.reconcile_departures(session, latest_uins)
        except Exception:
            departures = {"deleted": 0}

        return ApiResponse(
            success=True,
            message=f"导入完成：创建 {len(created_ids)} 个，更新 {len(updated_ids)} 个，清理 {departures.get('deleted', 0)} 个退群成员",
            data={**result, "departures": departures}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")


@router.post(
    "/import-file",
    response_model=ApiResponse,
    summary="上传JSON文件导入",
    description="上传QQ群成员JSON文件进行批量导入（存在则更新，不存在则创建）"
)
async def import_members_from_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """从上传的JSON文件导入成员"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON文件")

    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))

        if 'mems' not in data:
            raise HTTPException(status_code=400, detail="JSON文件格式错误，缺少mems字段")

        members_data: List[ImportMemberRequest] = []
        for mem in data['mems']:
            member_request = ImportMemberRequest(
                uin=mem['uin'],
                role=mem['role'],
                join_time=mem['join_time'],
                last_speak_time=mem.get('last_speak_time'),
                card=mem['card'],
                nick=mem['nick'],
                lv=mem['lv'],
                qage=mem.get('qage', 0)
            )
            members_data.append(member_request)

        return await import_members_from_json(ImportBatchRequest(members=members_data), session)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件导入失败: {str(e)}")


@router.post(
    "/import-from-qq",
    response_model=ApiResponse,
    summary="通过QQ群官网获取并导入成员",
    description="通过 Cookie 等参数从 qun.qq.com 获取成员数据后执行批量导入（存在则更新，不存在则创建）"
)
async def import_members_from_qq(
    params: QQImportParams,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
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

        # 批量下载头像（对新创建与更新的 UIN）
        try:
            from domain.avatar_service import AvatarService
            updated_uins = result.get("updated_uins", [])
            created_details = result.get("created_details", [])
            created_uins = [d.get("uin") for d in created_details if d.get("uin")]
            target_uins = list({*updated_uins, *created_uins})  # 去重
            if target_uins:
                await AvatarService.batch_fetch_and_save_avatars_webp(target_uins)
        except Exception:
            pass

        # 清理已退群成员
        try:
            latest_uins = [m.uin for m in members_data]
            departures = await MemberService.reconcile_departures(session, latest_uins)
        except Exception:
            departures = {"deleted": 0}

        return ApiResponse(
            success=True,
            message=f"导入完成：创建 {len(created_ids)} 个，更新 {len(updated_ids)} 个，清理 {departures.get('deleted', 0)} 个退群成员",
            data={
                **result,
                "departures": departures,
                "source": "qq",
                "group_id": params.group_id,
                "fetched_count": len(members_data),
            }
        )
    except QQGroupFetcherError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"从QQ群获取或导入失败: {str(e)}")


@router.get(
    "/decrypt-uin/{member_id}",
    summary="解密成员UIN（调试用）",
    description="解密指定成员的UIN，仅用于调试和验证"
)
async def decrypt_member_uin(
    member_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """解密成员UIN（仅用于调试）"""
    from services.database.models.member.base import Member

    member = await session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")

    try:
        crypto_service = get_crypto_service()
        decrypted_uin = crypto_service.decrypt_uin(member.uin_encrypted, member.salt)
        return {
            "member_id": member_id,
            "display_name": member.display_name,
            "decrypted_uin": decrypted_uin,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解密失败: {str(e)}")


@router.get(
    "/database-stats",
    summary="获取数据库统计信息",
    description="获取数据库的详细统计信息"
)
async def get_database_stats(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(require_admin)
):
    """获取数据库统计信息"""
    try:
        from sqlmodel import select, func
        from services.database.models.member.base import Member

        # 基本统计
        total_members_result = await session.exec(select(func.count(Member.id)))
        total_members = total_members_result.one()

        # 最新和最早的成员
        latest_member_result = await session.exec(
            select(Member).order_by(Member.created_at.desc()).limit(1)
        )
        latest_member = latest_member_result.first()

        earliest_member_result = await session.exec(
            select(Member).order_by(Member.created_at.asc()).limit(1)
        )
        earliest_member = earliest_member_result.first()

        return {
            "total_members": total_members,
            "latest_member": {
                "id": latest_member.id,
                "name": latest_member.display_name,
                "created_at": latest_member.created_at.isoformat()
            } if latest_member else None,
            "earliest_member": {
                "id": earliest_member.id,
                "name": earliest_member.display_name,
                "created_at": earliest_member.created_at.isoformat()
            } if earliest_member else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
