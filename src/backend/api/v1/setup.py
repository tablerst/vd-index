"""
系统初始化API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.deps import get_session
from services.database.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/setup", tags=["setup"])


class SetupResponse(BaseModel):
    """设置响应"""
    success: bool
    message: str
    admin_created: bool = False


@router.get("/status", response_model=SetupResponse)
async def get_setup_status(session: AsyncSession = Depends(get_session)):
    """
    获取系统设置状态
    """
    try:
        # 检查是否存在管理员用户
        admin_statement = select(User).where(User.role == "admin")
        result = await session.exec(admin_statement)
        existing_admins = result.all()

        if existing_admins:
            return SetupResponse(
                success=True,
                message="系统已完成初始化设置",
                admin_created=True
            )
        else:
            return SetupResponse(
                success=True,
                message="系统需要创建管理员用户",
                admin_created=False
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取设置状态失败: {str(e)}"
        )
