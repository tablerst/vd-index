"""
成员业务逻辑服务
"""
import secrets
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession

from services.database.models.member import Member, MemberCreate, MemberCRUD, MemberUpdate
from services.database.models.base import to_naive_beijing

from services.database.models import ActivityCRUD
from services.database.models.comment.crud import CommentCRUD
from schema.member import MemberResponse, MemberDetailResponse, ImportMemberRequest
from services.deps import get_crypto_service
from utils.avatar import AvatarService


class MemberService:
    """成员服务"""


    @staticmethod
    def _decode_html_text(s: Optional[str]) -> str:
        """Decode common HTML entities and normalize spaces.
        - Converts &nbsp; to normal space
        - Strips leading/trailing whitespace
        """
        if not s:
            return ""
        import html as _html
        text = _html.unescape(s)
        return text.replace("\xa0", " ").strip()

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
        avatar_url = f"{base_url}/api/v1/avatar/{member.id}"

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
        avatar_url = f"{base_url}/api/v1/avatar/{member.id}"

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
        """从JSON数据导入成员（创建）"""
        # 生成随机salt
        salt = secrets.token_hex(8)

        # 加密UIN
        crypto_service = get_crypto_service()
        encrypted_uin = crypto_service.encrypt_uin(member_data.uin, salt)

        # 确定显示名称（解码HTML实体）
        card_decoded = MemberService._decode_html_text(member_data.card)
        nick_decoded = MemberService._decode_html_text(member_data.nick)
        display_name = card_decoded or nick_decoded

        # 创建成员数据对象
        member_create = MemberCreate(
            display_name=display_name,
            group_nick=card_decoded or None,
            qq_nick=nick_decoded or None,
            uin_encrypted=encrypted_uin,
            salt=salt,
            role=member_data.role,
            join_time=to_naive_beijing(datetime.fromtimestamp(member_data.join_time, tz=timezone.utc)),
            last_speak_time=to_naive_beijing(datetime.fromtimestamp(member_data.last_speak_time, tz=timezone.utc)) if member_data.last_speak_time else None,
            level_point=member_data.lv.get("point", 0),
            level_value=member_data.lv.get("level", 1),
            q_age=member_data.qage or 0
        )

        # 使用CRUD操作创建成员
        member = await MemberCRUD.create(session, member_create)
        return member

    @staticmethod
    async def upsert_members_from_json(
        session: AsyncSession,
        members_data: List[ImportMemberRequest]
    ) -> Dict[str, Any]:
        """
        批量根据UIN进行Upsert（存在则更新，不存在则创建）。
        - 为性能考虑，一次性加载现有成员并解密建立 UIN->Member 映射
        - 更新时不修改 uin_encrypted 与 salt
        返回：{"created_ids": [...], "updated_ids": [...], "created_details": [{"id": int, "uin": int}]}。
        """
        crypto_service = get_crypto_service()

        # 加载现有成员并构建 UIN->Member 映射
        existing_members = await MemberCRUD.get_all(session)
        uin_to_member: Dict[int, Member] = {}
        for m in existing_members:
            try:
                uin_val = crypto_service.decrypt_uin(m.uin_encrypted, m.salt)
                uin_to_member[uin_val] = m
            except Exception:
                # 解密失败则跳过该成员
                continue

        created_ids: List[int] = []
        updated_ids: List[int] = []
        created_details: List[Dict[str, Any]] = []
        updated_uins: List[int] = []
        all_uins: List[int] = []

        for md in members_data:
            # 累计全部uin用于后续退群对账
            try:
                if md.uin not in all_uins:
                    all_uins.append(md.uin)
            except Exception:
                pass
            # 规范化显示/昵称（解码HTML实体）
            display_name_raw = (md.card or "").strip() or (md.nick or "").strip()
            group_nick_raw = (md.card or "").strip() or None
            qq_nick_raw = (md.nick or "").strip() or None

            display_name = MemberService._decode_html_text(display_name_raw)
            group_nick = MemberService._decode_html_text(group_nick_raw) if group_nick_raw else None
            qq_nick = MemberService._decode_html_text(qq_nick_raw) if qq_nick_raw else None

            # 现有则更新
            if md.uin in uin_to_member:
                existing = uin_to_member[md.uin]
                update_payload = MemberUpdate(
                    display_name=display_name,
                    group_nick=group_nick,
                    qq_nick=qq_nick,
                    role=md.role,
                    last_speak_time=to_naive_beijing(datetime.fromtimestamp(md.last_speak_time, tz=timezone.utc)) if md.last_speak_time else None,
                    level_point=md.lv.get("point", 0) if md.lv else None,
                    level_value=md.lv.get("level", 1) if md.lv else None,
                    q_age=md.qage or 0
                )
                updated = await MemberCRUD.update(session, existing.id, update_payload)
                if updated:
                    updated_ids.append(updated.id)
                    updated_uins.append(md.uin)
                # 保持映射不变
            else:
                # 不存在则创建
                salt = secrets.token_hex(8)
                encrypted_uin = crypto_service.encrypt_uin(md.uin, salt)
                create_payload = MemberCreate(
                    display_name=display_name,
                    group_nick=group_nick,
                    qq_nick=qq_nick,
                    uin_encrypted=encrypted_uin,
                    salt=salt,
                    role=md.role,
                    join_time=to_naive_beijing(datetime.fromtimestamp(md.join_time, tz=timezone.utc)),
                    last_speak_time=to_naive_beijing(datetime.fromtimestamp(md.last_speak_time, tz=timezone.utc)) if md.last_speak_time else None,
                    level_point=md.lv.get("point", 0) if md.lv else 0,
                    level_value=md.lv.get("level", 1) if md.lv else 1,
                    q_age=md.qage or 0
                )
                created = await MemberCRUD.create(session, create_payload)
                created_ids.append(created.id)
                created_details.append({"id": created.id, "uin": md.uin})
                # 更新映射，避免同批次重复创建
                uin_to_member[md.uin] = created

        return {
            "created_ids": created_ids,
            "updated_ids": updated_ids,
            "created_details": created_details,
            "updated_uins": updated_uins,
            "all_uins": all_uins,
        }

    @staticmethod
    async def reconcile_departures(session: AsyncSession, latest_uins: List[int]) -> Dict[str, Any]:
        """对比数据库与最新成员UIN列表，清理已退群成员。
        返回统计信息：{"deleted": n, "details": [...]}。
        """
        logger = logging.getLogger(__name__)
        crypto = get_crypto_service()
        # 加载所有成员并映射 uin->Member
        existing_members = await MemberCRUD.get_all(session)
        logger.info(f"[RECONCILE] existing members: {len(existing_members)}; latest_uins input size: {len(latest_uins)}")
        uin_to_member: Dict[int, Member] = {}
        for m in existing_members:
            try:
                u = crypto.decrypt_uin(m.uin_encrypted, m.salt)
                uin_to_member[u] = m
            except Exception as e:
                logger.warning(f"[RECONCILE] failed to decrypt member id={m.id}: {e}")
                continue
        latest_set = set(int(x) for x in latest_uins if x is not None)
        logger.info(f"[RECONCILE] mapped existing UINs: {len(uin_to_member)}; latest_set size: {len(latest_set)}")
        departed = [ (u, m) for u, m in uin_to_member.items() if u not in latest_set ]
        logger.info(f"[RECONCILE] departed candidates: {len(departed)}")
        details = []
        for u, m in departed:
            info = await MemberService._cleanup_member_departure(session, m, u)
            details.append(info)
        logger.info(f"[RECONCILE] deleted count: {len(details)}")
        return {"deleted": len(details), "details": details}


    @staticmethod
    async def _cleanup_member_departure(session: AsyncSession, member: Member, uin: int) -> Dict[str, Any]:
        """清理退群成员的相关数据并删除成员记录。
        步骤：删除评论 -> 从所有活动的参与者中移除 -> 删除头像文件 -> 删除成员。
        """
        logger = logging.getLogger(__name__)
        removed = {
            "member_id": member.id,
            "uin": uin,
            "comments_deleted": 0,
            "activities_updated": 0,
            "avatar_deleted": False,
            "member_deleted": False,
            "errors": []
        }
        # 删除评论
        try:
            from services.database.models.comment.crud import CommentCRUD
            deleted_cnt = await CommentCRUD.delete_by_member_id(session, member.id)
            removed["comments_deleted"] = deleted_cnt
            logger.info(f"[RECONCILE] member {member.id} comments deleted: {deleted_cnt}")
        except Exception as e:
            logger.warning(f"[RECONCILE] delete comments failed for member {member.id}: {e}")
            removed["errors"].append(f"comments:{e}")
        # 从活动中移除
        try:
            activities = await ActivityCRUD.get_by_participant(session, member.id)
            count = 0
            for act in activities:
                updated = await ActivityCRUD.remove_participant(session, act.id, member.id)
                if updated:
                    count += 1
            removed["activities_updated"] = count
            logger.info(f"[RECONCILE] member {member.id} removed from activities: {count}")
        except Exception as e:
            logger.warning(f"[RECONCILE] remove from activities failed for member {member.id}: {e}")
            removed["errors"].append(f"activities:{e}")
        # 删除头像文件
        try:
            removed["avatar_deleted"] = AvatarService.delete_avatar_file_by_uin(uin)
            logger.info(f"[RECONCILE] member {member.id} avatar_deleted={removed['avatar_deleted']}")
        except Exception as e:
            logger.warning(f"[RECONCILE] delete avatar failed for member {member.id}: {e}")
            removed["errors"].append(f"avatar:{e}")
        # 最后删除成员
        try:
            ok = await MemberCRUD.delete(session, member.id)
            removed["member_deleted"] = bool(ok)
            # 二次核验：再查一次
            try:
                from services.database.models.member.base import Member as MemberModel
                check = await session.get(MemberModel, member.id)
                logger.info(f"[RECONCILE] member {member.id} deleted={ok}, verify_exists={check is not None}")
            except Exception as e2:
                logger.warning(f"[RECONCILE] verify after delete failed for member {member.id}: {e2}")
        except Exception as e:
            logger.error(f"[RECONCILE] delete member failed for member {member.id}: {e}")
            removed["errors"].append(f"member:{e}")
        return removed

