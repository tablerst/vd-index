"""
业务逻辑服务层
"""
import secrets
from datetime import datetime
from typing import List, Optional, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.services.database.models.member import Member, MemberCreate, MemberCRUD
from schema.member_schemas import MemberResponse, MemberDetailResponse, ImportMemberRequest
from core.crypto import encrypt_uin


class MemberService:
    """成员服务"""
    
    @staticmethod
    def get_role_text(role: int) -> str:
        """获取群权限显示文本"""
        role_map = {0: "群主", 1: "管理员", 2: "群员"}
        return role_map.get(role, "未知")
    
    @staticmethod
    def format_datetime(dt: Optional[datetime]) -> Optional[str]:
        """格式化日期时间"""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def create_member_response(member: Member, base_url: str = "") -> MemberResponse:
        """创建成员响应对象"""
        # 生成头像URL - 使用成员ID而不是avatar_hash
        avatar_url = f"{base_url}/api/avatar/{member.id}"

        # 生成简介
        join_date_str = MemberService.format_datetime(member.join_time)
        bio = f"加入于 {join_date_str}"

        return MemberResponse(
            id=member.id,
            name=member.display_name,
            avatar_url=avatar_url,
            bio=bio,
            join_date=join_date_str,
            role=member.role,
            group_nick=member.group_nick,
            qq_nick=member.qq_nick
        )
    
    @staticmethod
    def create_member_detail_response(member: Member, base_url: str = "") -> MemberDetailResponse:
        """创建成员详情响应对象"""
        # 生成头像URL - 使用成员ID而不是avatar_hash
        avatar_url = f"{base_url}/api/avatar/{member.id}"

        # 生成简介
        join_date_str = MemberService.format_datetime(member.join_time)
        bio = f"加入于 {join_date_str}"

        return MemberDetailResponse(
            id=member.id,
            name=member.display_name,
            avatar_url=avatar_url,
            bio=bio,
            join_date=join_date_str,
            role=member.role,
            group_nick=member.group_nick,
            qq_nick=member.qq_nick,
            level_point=member.level_point,
            level_value=member.level_value,
            q_age=member.q_age,
            last_speak_time=MemberService.format_datetime(member.last_speak_time)
        )
    
    @staticmethod
    async def get_members_paginated(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        base_url: str = ""
    ) -> Tuple[List[MemberResponse], int]:
        """分页获取成员列表"""
        # 使用CRUD操作获取分页数据
        members, total = await MemberCRUD.get_paginated(session, page, page_size)

        # 转换为响应对象
        member_responses = [
            MemberService.create_member_response(member, base_url)
            for member in members
        ]

        return member_responses, total
    
    @staticmethod
    async def get_member_by_id(session: AsyncSession, member_id: int, base_url: str = "") -> Optional[MemberDetailResponse]:
        """根据ID获取成员详情"""
        member = await MemberCRUD.get_by_id(session, member_id)
        if not member:
            return None

        return MemberService.create_member_detail_response(member, base_url)
    
    @staticmethod
    async def import_member_from_json(session: AsyncSession, member_data: ImportMemberRequest) -> Member:
        """从JSON数据导入成员"""
        # 生成随机salt
        salt = secrets.token_hex(8)

        # 加密UIN
        encrypted_uin = encrypt_uin(member_data.uin, salt)

        # 确定显示名称
        display_name = member_data.card.strip() or member_data.nick.strip()

        # 创建成员数据对象
        member_create = MemberCreate(
            display_name=display_name,
            group_nick=member_data.card.strip() if member_data.card.strip() else None,
            qq_nick=member_data.nick.strip() if member_data.nick.strip() else None,
            uin_encrypted=encrypted_uin,
            salt=salt,
            role=member_data.role,
            join_time=datetime.fromtimestamp(member_data.join_time),
            last_speak_time=datetime.fromtimestamp(member_data.last_speak_time) if member_data.last_speak_time else None,
            level_point=member_data.lv.get("point", 0),
            level_value=member_data.lv.get("level", 1),
            q_age=member_data.qage or 0
        )

        # 使用CRUD操作创建成员
        member = await MemberCRUD.create(session, member_create)
        return member



