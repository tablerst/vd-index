"""
系统初始化API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_session
from services.database.models.user import User
from services.auth.service import AuthService
from services.deps import get_config_service
from pydantic import BaseModel

router = APIRouter(prefix="/setup", tags=["setup"])


class CreateAdminRequest(BaseModel):
    """创建管理员请求"""
    username: str = "admin"
    password: str = "admin123"


class SetupResponse(BaseModel):
    """设置响应"""
    success: bool
    message: str
    admin_created: bool = False


@router.post("/create-admin", response_model=SetupResponse)
async def create_admin_user(
    request: CreateAdminRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    创建管理员用户（仅在没有管理员时可用）
    """
    try:
        # 检查是否已存在管理员用户
        statement = select(User).where(User.username == request.username)
        result = await session.exec(statement)
        existing_admin = result.first()

        if existing_admin:
            return SetupResponse(
                success=False,
                message=f"管理员用户 '{request.username}' 已存在",
                admin_created=False
            )

        # 检查是否已有任何管理员用户
        admin_statement = select(User).where(User.role == "admin")
        admin_result = await session.exec(admin_statement)
        existing_admins = admin_result.all()

        if existing_admins:
            return SetupResponse(
                success=False,
                message="系统中已存在管理员用户，无法创建新的管理员",
                admin_created=False
            )

        # 创建认证服务实例
        config_service = get_config_service()
        settings = config_service.get_settings()
        auth_service = AuthService(settings)

        # 创建管理员用户
        password_hash = auth_service.get_password_hash(request.password)

        admin_user = User(
            username=request.username,
            password_hash=password_hash,
            role="admin",
            is_active=True
        )

        # 保存到数据库
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        return SetupResponse(
            success=True,
            message=f"管理员用户 '{admin_user.username}' 创建成功",
            admin_created=True
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"创建管理员用户失败: {str(e)}"
        )


@router.get("/status", response_model=SetupResponse)
async def get_setup_status(session: AsyncSession = Depends(get_async_session)):
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
