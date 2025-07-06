"""
认证工具函数
提供依赖注入和认证装饰器
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from services.database.models.user import User, UserCRUD
from services.deps import get_session, get_auth_service
from .service import AuthService

# OAuth2 认证方案
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=False
)


async def get_current_user_by_jwt(
    token: str,
    session: AsyncSession,
    auth_service: AuthService
) -> User:
    """通过JWT获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 验证token
    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # 获取用户名
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # 查询用户
    user = await UserCRUD.get_by_username(session, username=username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user(
    token: Annotated[str, Security(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    """获取当前用户（依赖注入）"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await get_current_user_by_jwt(token, session, auth_service)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """获取管理员用户"""
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """要求管理员权限的依赖"""
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return {"user": current_user, "role": current_user.role}


async def create_super_user(
    session: AsyncSession,
    auth_service: AuthService,
    username: str,
    password: str,
    email: str = None
) -> User:
    """
    创建超级用户

    Args:
        session: 数据库会话
        auth_service: 认证服务
        username: 用户名
        password: 密码
        email: 邮箱（可选）

    Returns:
        User: 创建的超级用户

    Raises:
        ValueError: 如果用户名已存在
    """
    # 检查用户名是否已存在
    existing_user = await UserCRUD.get_by_username(session, username=username)
    if existing_user:
        raise ValueError(f"用户名 '{username}' 已存在")

    # 创建密码哈希
    password_hash = auth_service.get_password_hash(password)

    # 创建超级用户
    super_user = User(
        username=username,
        password_hash=password_hash,
        email=email,
        role="admin",
        is_active=True
    )

    # 保存到数据库
    session.add(super_user)
    await session.commit()
    await session.refresh(super_user)

    return super_user
