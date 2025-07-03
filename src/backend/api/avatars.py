"""
头像相关API路由
"""
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from services.deps import get_session
from core.crypto import decrypt_uin

router = APIRouter(prefix="/api", tags=["avatars"])


@router.get(
    "/avatar/{member_id}",
    summary="获取头像文件",
    description="根据成员ID获取头像文件，返回二进制流"
)
async def get_avatar(member_id: int, session: AsyncSession = Depends(get_session)):
    """获取头像文件"""
    # 验证成员ID
    if member_id < 1:
        raise HTTPException(status_code=400, detail="无效的成员ID")

    try:
        # 根据ID查询成员
        from services.database.models.member import Member
        member = await session.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        # 解密得到UIN
        uin = decrypt_uin(member.uin_encrypted, member.salt)

        # 构建头像文件路径
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"

        if not avatar_path.exists():
            raise HTTPException(status_code=404, detail="头像文件不存在")

        # 返回文件
        return FileResponse(
            path=avatar_path,
            media_type="image/webp",
            headers={
                "Cache-Control": "public, max-age=86400",  # 缓存1天
                "ETag": f'"{member_id}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取头像失败: {str(e)}")


@router.head(
    "/avatar/{member_id}",
    summary="检查头像文件是否存在",
    description="检查指定成员ID的头像文件是否存在"
)
async def check_avatar(member_id: int, session: AsyncSession = Depends(get_session)):
    """检查头像文件是否存在"""
    # 验证成员ID
    if member_id < 1:
        raise HTTPException(status_code=400, detail="无效的成员ID")

    try:
        # 根据ID查询成员
        from services.database.models.member import Member
        member = await session.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="成员不存在")

        # 解密得到UIN
        uin = decrypt_uin(member.uin_encrypted, member.salt)

        # 构建头像文件路径
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"

        if not avatar_path.exists():
            raise HTTPException(status_code=404, detail="头像文件不存在")

        # 返回头部信息
        return Response(
            status_code=200,
            headers={
                "Cache-Control": "public, max-age=86400",
                "ETag": f'"{member_id}"',
                "Content-Type": "image/webp"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查头像失败: {str(e)}")
