"""
用户-成员绑定 API 路由
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from services.deps import get_session, get_crypto_service
from services.auth.utils import get_current_active_user
from services.database.models.member import MemberCRUD
from services.database.models.user import UserCRUD

router = APIRouter(tags=["users"])  # 使用 v1 前缀


from pydantic import BaseModel, Field

class BindMemberRequest(BaseModel):
    member_id: int = Field(ge=1)
    uin: int = Field(ge=10000)


@router.post(
    "/users/bind-member",
    summary="绑定用户到成员（选择成员 + 输入UIN校验）"
)
async def bind_member(
    request: Request,
    payload: BindMemberRequest,
    current_user=Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    crypto=Depends(get_crypto_service)
):
    # 限流：5/min（按IP，若需按用户可改键函数为 user.id）
    try:
        limiter = request.app.state.limiter
        # 按用户ID限流（5/min）
        @limiter.limit("5/minute", key_func=lambda req: str(getattr(current_user, 'id', 'anon')))
        async def _noop(req):
            return None
        await _noop(request)
    except Exception:
        pass
    # 若已绑定，拒绝
    if getattr(current_user, 'member_id', None):
        raise HTTPException(status_code=400, detail="User already bound to a member")

    # 检查 member 是否存在
    member = await MemberCRUD.get_by_id(session, payload.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # 解密该成员的 UIN，进行比对
    try:
        real_uin = crypto.decrypt_uin(member.uin_encrypted, member.salt)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to verify member UIN")

    if int(payload.uin) != int(real_uin):
        # 模糊提示，避免暴露细节
        raise HTTPException(status_code=400, detail="Verification failed")

    # 使用唯一约束兜底并尽量提前检查占用
    existing_user = await UserCRUD.get_by_member_id(session, payload.member_id)
    if existing_user:
        raise HTTPException(status_code=409, detail="Member already bound by another user")

    # 绑定写入
    user = await UserCRUD.get_by_id(session, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.member_id = payload.member_id
    session.add(user)
    try:
        await session.commit()
    except Exception:
        # 冲突或其他错误时回滚并返回 409（数据库唯一约束兜底）
        await session.rollback()
        raise HTTPException(status_code=409, detail="Binding conflict")

    return {"success": True}



from schema.member import BindableMembersResponse, BindableMemberItem


@router.get(
    "/members/bindable",
    response_model=BindableMembersResponse,
    summary="获取可绑定的成员列表（未被任何用户绑定）"
)
async def get_bindable_members(
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_active_user)
):
    """返回未被绑定的成员（未被任何用户占用），分页返回精简字段。"""
    from sqlmodel import select, func
    from services.database.models.member.base import Member
    from services.database.models.user.base import User

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="invalid pagination")

    # 子查询：所有已绑定的 member_id
    bound_stmt = select(User.member_id).where(User.member_id.is_not(None))

    # 主查询：未绑定成员 + 分页
    stmt = (
        select(Member)
        .where(Member.id.not_in(bound_stmt))
        .order_by(Member.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    members = (await session.exec(stmt)).all()

    # 统计总数（未绑定成员总数）
    count_stmt = select(func.count()).select_from(Member).where(Member.id.not_in(bound_stmt))
    total = (await session.exec(count_stmt)).one()

    items = [
        BindableMemberItem(id=m.id, display_name=m.display_name, avatar_url=f"/api/v1/avatar/{m.id}")
        for m in members
    ]

    return BindableMembersResponse(
        members=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )

