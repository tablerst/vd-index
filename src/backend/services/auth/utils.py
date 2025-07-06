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
