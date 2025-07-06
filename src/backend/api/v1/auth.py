"""
认证API路由
处理用户登录、登出、token验证等功能
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from services.database.models.user import User, UserCreate, UserRead, UserLogin, UserCRUD
from services.deps import get_session, get_auth_service
from services.auth.service import AuthService
from services.auth.utils import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", summary="用户登录")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    用户登录接口
    
    Args:
        form_data: OAuth2密码表单数据
        session: 数据库会话
        auth_service: 认证服务
    
    Returns:
        包含access_token和用户信息的响应
    """
    # 验证用户
    user = await UserCRUD.get_by_username(session, username=form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    await UserCRUD.update_last_login(session, user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    }


@router.get("/me", response_model=UserRead, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    获取当前登录用户的信息
    
    Args:
        current_user: 当前用户
    
    Returns:
        用户信息
    """
    return current_user


@router.post("/logout", summary="用户登出")
async def logout():
    """
    用户登出接口
    
    Note:
        由于使用JWT，服务端无状态，登出主要由前端处理（删除token）
        这里提供接口用于记录登出日志或其他业务逻辑
    """
    return {"message": "登出成功"}


@router.post("/refresh", summary="刷新令牌")
async def refresh_token(
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    刷新访问令牌
    
    Args:
        current_user: 当前用户
        auth_service: 认证服务
    
    Returns:
        新的访问令牌
    """
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
