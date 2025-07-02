"""
头像相关API路由
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pathlib import Path

from services.avatar_service import AvatarService
from core.config import settings

router = APIRouter(prefix="/api", tags=["avatars"])


@router.get(
    "/avatar/{avatar_hash}",
    summary="获取头像文件",
    description="根据头像哈希获取头像文件，返回二进制流"
)
async def get_avatar(avatar_hash: str):
    """获取头像文件"""
    # 验证哈希格式（64位十六进制字符串）
    if not avatar_hash or len(avatar_hash) != 64:
        raise HTTPException(status_code=400, detail="无效的头像哈希")
    
    # 验证哈希只包含十六进制字符
    try:
        int(avatar_hash, 16)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的头像哈希格式")
    
    try:
        # 获取头像文件路径
        avatar_path = AvatarService.get_avatar_path(avatar_hash)
        
        if not avatar_path or not avatar_path.exists():
            raise HTTPException(status_code=404, detail="头像文件不存在")
        
        # 返回文件
        return FileResponse(
            path=avatar_path,
            media_type="image/webp",
            headers={
                "Cache-Control": "public, max-age=86400",  # 缓存1天
                "ETag": f'"{avatar_hash}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取头像失败: {str(e)}")


@router.head(
    "/avatar/{avatar_hash}",
    summary="检查头像文件是否存在",
    description="检查指定哈希的头像文件是否存在"
)
async def check_avatar(avatar_hash: str):
    """检查头像文件是否存在"""
    # 验证哈希格式
    if not avatar_hash or len(avatar_hash) != 64:
        raise HTTPException(status_code=400, detail="无效的头像哈希")
    
    try:
        int(avatar_hash, 16)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的头像哈希格式")
    
    try:
        # 检查文件是否存在
        avatar_path = AvatarService.get_avatar_path(avatar_hash)
        
        if not avatar_path or not avatar_path.exists():
            raise HTTPException(status_code=404, detail="头像文件不存在")
        
        # 返回头部信息
        return Response(
            status_code=200,
            headers={
                "Cache-Control": "public, max-age=86400",
                "ETag": f'"{avatar_hash}"',
                "Content-Type": "image/webp"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查头像失败: {str(e)}")
