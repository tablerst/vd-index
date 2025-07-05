"""
活动API测试用例
"""
import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from main import app
from services.deps import get_db_service
from services.database.models.activity.base import Activity, ActivityCreate
from services.database.models.activity.crud import ActivityCRUD


@pytest.fixture
def client():
    """HTTP客户端"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def db_session():
    """数据库会话"""
    db_service = get_db_service()
    async with db_service.with_session() as session:
        yield session


@pytest.fixture
async def sample_activity(db_session: AsyncSession):
    """创建示例活动"""
    activity_data = ActivityCreate(
        title="测试活动",
        description="这是一个测试活动",
        date=datetime(2024, 1, 15),
        tags=["测试", "活动"],
        participant_ids=[1, 2, 3]
    )
    activity = await ActivityCRUD.create(db_session, activity_data)
    yield activity
    
    # 清理
    await ActivityCRUD.delete(db_session, activity.id)


class TestActivityAPI:
    """活动API测试类"""

    def test_get_activities_list(self, client):
        """测试获取活动列表"""
        response = client.get("/api/star_calendar/activities")
        assert response.status_code == 200

        data = response.json()
        assert "activities" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["activities"], list)

    def test_get_activities_stats(self, client):
        """测试获取活动统计"""
        response = client.get("/api/star_calendar/activities/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_activities" in data
        assert "total_participants" in data
        assert "unique_participants" in data
        assert isinstance(data["total_activities"], int)
        assert isinstance(data["total_participants"], int)
        assert isinstance(data["unique_participants"], int)
    
    async def test_get_activity_by_id(self, async_client: AsyncClient, sample_activity: Activity):
        """测试根据ID获取活动"""
        response = await async_client.get(f"/api/star_calendar/activity/{sample_activity.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_activity.id
        assert data["title"] == sample_activity.title
        assert data["description"] == sample_activity.description
        assert "participants" in data
        assert "participants_total" in data
    
    async def test_get_nonexistent_activity(self, async_client: AsyncClient):
        """测试获取不存在的活动"""
        response = await async_client.get("/api/star_calendar/activity/99999")
        assert response.status_code == 404
    
    async def test_create_activity(self, async_client: AsyncClient):
        """测试创建活动"""
        activity_data = {
            "title": "新测试活动",
            "description": "这是一个新的测试活动",
            "date": "2024-06-15T00:00:00",
            "tags": ["新建", "测试"],
            "participant_ids": [1, 2, 3, 4]
        }
        
        response = await async_client.post("/api/star_calendar/activities", json=activity_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == activity_data["title"]
        assert data["description"] == activity_data["description"]
        assert data["participants_total"] == len(activity_data["participant_ids"])
        
        # 清理创建的活动
        activity_id = data["id"]
        await async_client.delete(f"/api/star_calendar/activity/{activity_id}")
    
    async def test_update_activity(self, async_client: AsyncClient, sample_activity: Activity):
        """测试更新活动"""
        update_data = {
            "title": "更新后的活动标题",
            "description": "更新后的活动描述"
        }
        
        response = await async_client.put(
            f"/api/star_calendar/activity/{sample_activity.id}", 
            json=update_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    async def test_delete_activity(self, async_client: AsyncClient, db_session: AsyncSession):
        """测试删除活动"""
        # 先创建一个活动
        activity_data = ActivityCreate(
            title="待删除活动",
            description="这个活动将被删除",
            date=datetime(2024, 12, 31),
            tags=["删除", "测试"],
            participant_ids=[1, 2]
        )
        activity = await ActivityCRUD.create(db_session, activity_data)
        
        # 删除活动
        response = await async_client.delete(f"/api/star_calendar/activity/{activity.id}")
        assert response.status_code == 200
        
        # 验证活动已被删除
        response = await async_client.get(f"/api/star_calendar/activity/{activity.id}")
        assert response.status_code == 404
    
    async def test_activities_pagination(self, async_client: AsyncClient):
        """测试活动分页"""
        # 测试第一页
        response = await async_client.get("/api/star_calendar/activities?page=1&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["activities"]) <= 5
    
    async def test_activities_with_invalid_params(self, async_client: AsyncClient):
        """测试无效参数"""
        # 测试无效页码
        response = await async_client.get("/api/star_calendar/activities?page=0")
        assert response.status_code == 422
        
        # 测试无效页面大小
        response = await async_client.get("/api/star_calendar/activities?page_size=0")
        assert response.status_code == 422


class TestActivityCRUD:
    """活动CRUD操作测试类"""
    
    async def test_create_activity(self, db_session: AsyncSession):
        """测试创建活动"""
        activity_data = ActivityCreate(
            title="CRUD测试活动",
            description="测试CRUD操作",
            date=datetime(2024, 3, 20),
            tags=["CRUD", "测试"],
            participant_ids=[1, 2, 3, 4, 5]
        )
        
        activity = await ActivityCRUD.create(db_session, activity_data)
        assert activity.id is not None
        assert activity.title == activity_data.title
        assert activity.participants_total == 5
        
        # 清理
        await ActivityCRUD.delete(db_session, activity.id)
    
    async def test_get_activity_by_id(self, db_session: AsyncSession, sample_activity: Activity):
        """测试根据ID获取活动"""
        activity = await ActivityCRUD.get_by_id(db_session, sample_activity.id)
        assert activity is not None
        assert activity.id == sample_activity.id
        assert activity.title == sample_activity.title
    
    async def test_get_all_activities(self, db_session: AsyncSession):
        """测试获取所有活动"""
        activities = await ActivityCRUD.get_all(db_session)
        assert isinstance(activities, list)
        assert len(activities) >= 0
    
    async def test_get_paginated_activities(self, db_session: AsyncSession):
        """测试分页获取活动"""
        activities, total = await ActivityCRUD.get_paginated(db_session, page=1, page_size=5)
        assert isinstance(activities, list)
        assert isinstance(total, int)
        assert len(activities) <= 5
    
    async def test_count_total_activities(self, db_session: AsyncSession):
        """测试统计活动总数"""
        total = await ActivityCRUD.count_total(db_session)
        assert isinstance(total, int)
        assert total >= 0
    
    async def test_get_latest_activities(self, db_session: AsyncSession):
        """测试获取最新活动"""
        activities = await ActivityCRUD.get_latest_activities(db_session, limit=3)
        assert isinstance(activities, list)
        assert len(activities) <= 3
        
        # 验证按创建时间倒序排列
        if len(activities) > 1:
            for i in range(len(activities) - 1):
                assert activities[i].created_at >= activities[i + 1].created_at


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
