"""
头像相关API路由
"""
import logging
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from services.deps import get_session
from core.crypto import decrypt_uin

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["avatars"])


@router.get(
    "/avatar/{member_id}",
    summary="获取头像文件",
    description="根据成员ID获取头像文件，返回二进制流"
)
async def get_avatar(member_id: int, session: AsyncSession = Depends(get_session)):
    """获取头像文件"""
    logger.info(f"[GET_AVATAR] 开始处理头像请求 - member_id: {member_id}")

    # 验证成员ID
    if member_id < 1:
        logger.warning(f"[GET_AVATAR] 无效的成员ID: {member_id}")
        raise HTTPException(status_code=400, detail="无效的成员ID")

    try:
        # 根据ID查询成员
        from services.database.models.member import Member
        logger.debug(f"[GET_AVATAR] 查询数据库中的成员信息 - member_id: {member_id}")
        member = await session.get(Member, member_id)
        if not member:
            logger.warning(f"[GET_AVATAR] 成员不存在 - member_id: {member_id}")
            raise HTTPException(status_code=404, detail="成员不存在")

        logger.debug(f"[GET_AVATAR] 找到成员 - member_id: {member_id}, display_name: {member.display_name}")
        logger.debug(f"[GET_AVATAR] 加密UIN长度: {len(member.uin_encrypted) if member.uin_encrypted else 0}")
        logger.debug(f"[GET_AVATAR] Salt: {member.salt}")

        # 解密得到UIN
        logger.debug(f"[GET_AVATAR] 开始解密UIN - member_id: {member_id}")
        uin = decrypt_uin(member.uin_encrypted, member.salt)
        logger.info(f"[GET_AVATAR] UIN解密成功 - member_id: {member_id}, uin: {uin}")

        # 构建头像文件路径
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
        logger.debug(f"[GET_AVATAR] 头像文件路径: {avatar_path}")
        logger.debug(f"[GET_AVATAR] 头像根目录: {settings.avatar_root}")
        logger.debug(f"[GET_AVATAR] 头像文件存在: {avatar_path.exists()}")

        if not avatar_path.exists():
            logger.warning(f"[GET_AVATAR] 头像文件不存在 - path: {avatar_path}")
            # 列出目录中的文件以便调试
            avatar_dir = Path(settings.avatar_root)
            if avatar_dir.exists():
                files = list(avatar_dir.glob("*.webp"))
                logger.debug(f"[GET_AVATAR] 目录中的头像文件数量: {len(files)}")
                if len(files) <= 10:  # 只记录少量文件避免日志过长
                    logger.debug(f"[GET_AVATAR] 目录中的文件: {[f.name for f in files]}")
            else:
                logger.error(f"[GET_AVATAR] 头像根目录不存在: {avatar_dir}")
            raise HTTPException(status_code=404, detail="头像文件不存在")

        logger.info(f"[GET_AVATAR] 成功返回头像文件 - member_id: {member_id}, uin: {uin}")
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
        logger.error(f"[GET_AVATAR] 获取头像失败 - member_id: {member_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取头像失败: {str(e)}")


@router.head(
    "/avatar/{member_id}",
    summary="检查头像文件是否存在",
    description="检查指定成员ID的头像文件是否存在"
)
async def check_avatar(member_id: int, session: AsyncSession = Depends(get_session)):
    """检查头像文件是否存在"""
    logger.info(f"[CHECK_AVATAR] 开始检查头像 - member_id: {member_id}")

    # 验证成员ID
    if member_id < 1:
        logger.warning(f"[CHECK_AVATAR] 无效的成员ID: {member_id}")
        raise HTTPException(status_code=400, detail="无效的成员ID")

    try:
        # 根据ID查询成员
        from services.database.models.member import Member
        logger.debug(f"[CHECK_AVATAR] 查询数据库中的成员信息 - member_id: {member_id}")
        member = await session.get(Member, member_id)
        if not member:
            logger.warning(f"[CHECK_AVATAR] 成员不存在 - member_id: {member_id}")
            raise HTTPException(status_code=404, detail="成员不存在")

        logger.debug(f"[CHECK_AVATAR] 找到成员 - member_id: {member_id}, display_name: {member.display_name}")
        logger.debug(f"[CHECK_AVATAR] 加密UIN: {member.uin_encrypted[:20]}..." if member.uin_encrypted and len(member.uin_encrypted) > 20 else f"[CHECK_AVATAR] 加密UIN: {member.uin_encrypted}")
        logger.debug(f"[CHECK_AVATAR] Salt: {member.salt}")

        # 解密得到UIN
        logger.debug(f"[CHECK_AVATAR] 开始解密UIN - member_id: {member_id}")
        uin = decrypt_uin(member.uin_encrypted, member.salt)
        logger.info(f"[CHECK_AVATAR] UIN解密成功 - member_id: {member_id}, uin: {uin}")

        # 构建头像文件路径
        avatar_path = Path(settings.avatar_root) / f"{uin}.webp"
        logger.debug(f"[CHECK_AVATAR] 头像文件路径: {avatar_path}")
        logger.debug(f"[CHECK_AVATAR] 头像根目录: {settings.avatar_root}")
        logger.debug(f"[CHECK_AVATAR] 头像文件存在: {avatar_path.exists()}")

        if not avatar_path.exists():
            logger.warning(f"[CHECK_AVATAR] 头像文件不存在 - path: {avatar_path}")
            # 列出目录中的文件以便调试
            avatar_dir = Path(settings.avatar_root)
            if avatar_dir.exists():
                files = list(avatar_dir.glob("*.webp"))
                logger.debug(f"[CHECK_AVATAR] 目录中的头像文件数量: {len(files)}")
                if len(files) <= 10:  # 只记录少量文件避免日志过长
                    logger.debug(f"[CHECK_AVATAR] 目录中的文件: {[f.name for f in files]}")
            else:
                logger.error(f"[CHECK_AVATAR] 头像根目录不存在: {avatar_dir}")
            raise HTTPException(status_code=404, detail="头像文件不存在")

        logger.info(f"[CHECK_AVATAR] 头像文件检查成功 - member_id: {member_id}, uin: {uin}")
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
        logger.error(f"[CHECK_AVATAR] 检查头像失败 - member_id: {member_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检查头像失败: {str(e)}")
