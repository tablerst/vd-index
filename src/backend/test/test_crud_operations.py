"""
测试CRUD操作
"""
import pytest
import asyncio
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.services.database.models.member import Member, MemberCreate, MemberUpdate, MemberCRUD
from backend.services.database.models.config import Config, ConfigCreate, ConfigUpdate, ConfigCRUD
from backend.services.database.models.activity import Activity, ActivityCreate, ActivityUpdate, ActivityCRUD


class TestMemberCRUD:
    """测试Member CRUD操作"""
    
    @pytest.mark.asyncio
    async def test_member_create(self, async_session: AsyncSession):
        """测试创建成员"""
        member_data = MemberCreate(
            display_name="测试用户",
            group_nick="测试群昵称",
            qq_nick="测试QQ昵称",
            uin_encrypted="encrypted_uin_test",
            salt="test_salt_123456",
            role=2,
            join_time=datetime.utcnow(),
            level_point=100,
            level_value=5,
            q_age=3
        )
        
        member = await MemberCRUD.create(async_session, member_data)
        
        assert member.id is not None
        assert member.display_name == "测试用户"
        assert member.group_nick == "测试群昵称"
        assert member.role == 2
        assert member.level_point == 100
    
    @pytest.mark.asyncio
    async def test_member_get_by_id(self, async_session: AsyncSession):
        """测试根据ID获取成员"""
        # 先创建一个成员
        member_data = MemberCreate(
            display_name="测试用户2",
            uin_encrypted="encrypted_uin_test2",
            salt="test_salt_234567",
            role=1,
            join_time=datetime.utcnow()
        )
        created_member = await MemberCRUD.create(async_session, member_data)
        
        # 根据ID获取成员
        retrieved_member = await MemberCRUD.get_by_id(async_session, created_member.id)
        
        assert retrieved_member is not None
        assert retrieved_member.id == created_member.id
        assert retrieved_member.display_name == "测试用户2"
        assert retrieved_member.role == 1
    
    @pytest.mark.asyncio
    async def test_member_update(self, async_session: AsyncSession):
        """测试更新成员"""
        # 先创建一个成员
        member_data = MemberCreate(
            display_name="原始名称",
            uin_encrypted="encrypted_uin_test3",
            salt="test_salt_345678",
            role=2,
            join_time=datetime.utcnow()
        )
        created_member = await MemberCRUD.create(async_session, member_data)
        
        # 更新成员信息
        update_data = MemberUpdate(
            display_name="更新后名称",
            role=1,
            level_point=200
        )
        updated_member = await MemberCRUD.update(async_session, created_member.id, update_data)
        
        assert updated_member is not None
        assert updated_member.display_name == "更新后名称"
        assert updated_member.role == 1
        assert updated_member.level_point == 200
    
    @pytest.mark.asyncio
    async def test_member_delete(self, async_session: AsyncSession):
        """测试删除成员"""
        # 先创建一个成员
        member_data = MemberCreate(
            display_name="待删除用户",
            uin_encrypted="encrypted_uin_test4",
            salt="test_salt_456789",
            role=2,
            join_time=datetime.utcnow()
        )
        created_member = await MemberCRUD.create(async_session, member_data)
        
        # 删除成员
        result = await MemberCRUD.delete(async_session, created_member.id)
        assert result is True
        
        # 验证成员已被删除
        deleted_member = await MemberCRUD.get_by_id(async_session, created_member.id)
        assert deleted_member is None
    
    @pytest.mark.asyncio
    async def test_member_get_paginated(self, async_session: AsyncSession):
        """测试分页获取成员"""
        # 创建多个成员
        for i in range(5):
            member_data = MemberCreate(
                display_name=f"分页测试用户{i}",
                uin_encrypted=f"encrypted_uin_page_{i}",
                salt=f"salt_page_{i:06d}",
                role=2,
                join_time=datetime.utcnow()
            )
            await MemberCRUD.create(async_session, member_data)
        
        # 测试分页
        members, total = await MemberCRUD.get_paginated(async_session, page=1, page_size=3)
        
        assert len(members) <= 3
        assert total >= 5  # 至少有我们创建的5个成员


class TestConfigCRUD:
    """测试Config CRUD操作"""
    
    @pytest.mark.asyncio
    async def test_config_create(self, async_session: AsyncSession):
        """测试创建配置"""
        config_data = ConfigCreate(
            key="test_key",
            value="test_value",
            description="测试配置"
        )
        
        config = await ConfigCRUD.create(async_session, config_data)
        
        assert config.key == "test_key"
        assert config.value == "test_value"
        assert config.description == "测试配置"
    
    @pytest.mark.asyncio
    async def test_config_upsert(self, async_session: AsyncSession):
        """测试配置的插入或更新"""
        # 第一次插入
        config1 = await ConfigCRUD.upsert(async_session, "upsert_key", "value1", "描述1")
        assert config1.value == "value1"
        assert config1.description == "描述1"
        
        # 第二次更新
        config2 = await ConfigCRUD.upsert(async_session, "upsert_key", "value2", "描述2")
        assert config2.key == config1.key
        assert config2.value == "value2"
        assert config2.description == "描述2"
    
    @pytest.mark.asyncio
    async def test_config_get_all_as_dict(self, async_session: AsyncSession):
        """测试获取所有配置为字典格式"""
        # 创建几个配置
        await ConfigCRUD.upsert(async_session, "dict_key1", "value1")
        await ConfigCRUD.upsert(async_session, "dict_key2", "value2")
        
        config_dict = await ConfigCRUD.get_all_as_dict(async_session)
        
        assert "dict_key1" in config_dict
        assert "dict_key2" in config_dict
        assert config_dict["dict_key1"] == "value1"
        assert config_dict["dict_key2"] == "value2"


class TestActivityCRUD:
    """测试Activity CRUD操作"""
    
    @pytest.mark.asyncio
    async def test_activity_create(self, async_session: AsyncSession):
        """测试创建活动"""
        activity_data = ActivityCreate(
            title="测试活动",
            description="这是一个测试活动",
            date=datetime.utcnow(),
            tags=["测试", "活动"],
            participant_ids=[1, 2, 3]
        )
        
        activity = await ActivityCRUD.create(async_session, activity_data)
        
        assert activity.id is not None
        assert activity.title == "测试活动"
        assert activity.description == "这是一个测试活动"
        assert activity.tags == ["测试", "活动"]
        assert activity.participant_ids == [1, 2, 3]
        assert activity.participants_total == 3
    
    @pytest.mark.asyncio
    async def test_activity_add_participant(self, async_session: AsyncSession):
        """测试为活动添加参与者"""
        # 先创建一个活动
        activity_data = ActivityCreate(
            title="参与者测试活动",
            description="测试添加参与者",
            date=datetime.utcnow(),
            participant_ids=[1, 2]
        )
        created_activity = await ActivityCRUD.create(async_session, activity_data)
        
        # 添加参与者
        updated_activity = await ActivityCRUD.add_participant(async_session, created_activity.id, 3)
        
        assert updated_activity is not None
        assert 3 in updated_activity.participant_ids
        assert updated_activity.participants_total == 3
    
    @pytest.mark.asyncio
    async def test_activity_add_tag(self, async_session: AsyncSession):
        """测试为活动添加标签"""
        # 先创建一个活动
        activity_data = ActivityCreate(
            title="标签测试活动",
            description="测试添加标签",
            date=datetime.utcnow(),
            tags=["原始标签"]
        )
        created_activity = await ActivityCRUD.create(async_session, activity_data)
        
        # 添加标签
        updated_activity = await ActivityCRUD.add_tag(async_session, created_activity.id, "新标签")
        
        assert updated_activity is not None
        assert "新标签" in updated_activity.tags
        assert "原始标签" in updated_activity.tags
    
    @pytest.mark.asyncio
    async def test_activity_get_by_tag(self, async_session: AsyncSession):
        """测试根据标签获取活动"""
        # 创建带有特定标签的活动
        activity_data = ActivityCreate(
            title="标签搜索测试",
            description="测试标签搜索",
            date=datetime.utcnow(),
            tags=["特殊标签", "测试"]
        )
        await ActivityCRUD.create(async_session, activity_data)
        
        # 根据标签搜索
        activities = await ActivityCRUD.get_by_tag(async_session, "特殊标签")
        
        assert len(activities) >= 1
        assert any(activity.title == "标签搜索测试" for activity in activities)
