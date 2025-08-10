"""
管理员API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session, get_crypto_service
from services.auth.utils import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# 注：成员导入功能已全部迁移至 members 模块。
# 本模块仅保留管理员工具端点：decrypt_member_uin、database-stats。


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
