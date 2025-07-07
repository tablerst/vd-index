"""
Member CRUD操作的pytest测试用例
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from services.database.models.member import Member, MemberCreate, MemberUpdate, MemberCRUD
from services.deps import get_session
from schema.member_schemas import ImportMemberRequest


class TestMemberCRUD:
    """Member CRUD操作测试类"""
    
    @pytest.fixture
    def sample_member_data(self):
        """示例成员数据"""
        return {
            "uin": 123456789,
            "role": 2,
            "join_time": int(datetime.now().timestamp()),
            "last_speak_time": int(datetime.now().timestamp()),
            "card": "测试群昵称",
            "nick": "测试QQ昵称",
            "lv": {
                "point": 1000,
                "level": 10
            },
            "qage": 5
        }
    
    @pytest.fixture
    def sample_update_data(self):
        """示例更新数据"""
        return {
            "display_name": "更新后的名称",
            "group_nick": "更新后的群昵称",
            "role": 1,
            "level_point": 2000,
            "level_value": 20
        }
    
    @pytest.fixture
    def batch_member_data(self):
        """批量成员数据"""
        base_time = int(datetime.now().timestamp())
        return {
            "members": [
                {
                    "uin": 111111111,
                    "role": 2,
                    "join_time": base_time,
                    "last_speak_time": base_time,
                    "card": "批量用户1",
                    "nick": "QQ用户1",
                    "lv": {"point": 500, "level": 5},
                    "qage": 3
                },
                {
                    "uin": 222222222,
                    "role": 1,
                    "join_time": base_time,
                    "last_speak_time": base_time,
                    "card": "批量用户2",
                    "nick": "QQ用户2",
                    "lv": {"point": 1500, "level": 15},
                    "qage": 7
                },
                {
                    "uin": 333333333,
                    "role": 2,
                    "join_time": base_time,
                    "last_speak_time": None,
                    "card": "批量用户3",
                    "nick": "QQ用户3",
                    "lv": {"point": 800, "level": 8},
                    "qage": 2
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_create_single_member(self, sample_member_data):
        """测试创建单个成员"""
        async with AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/api/v1/members", json=sample_member_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "member_id" in data["data"]
            assert data["message"] == "成员创建成功"
            
            # 返回创建的成员ID供后续测试使用
            return data["data"]["member_id"]

    @pytest.mark.asyncio
    async def test_create_batch_members(self, batch_member_data):
        """测试批量创建成员"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/members/batch", json=batch_member_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "member_ids" in data["data"]
            assert len(data["data"]["member_ids"]) == 3
            assert "批量创建成功" in data["message"]
            
            # 返回创建的成员ID列表供后续测试使用
            return data["data"]["member_ids"]

    @pytest.mark.asyncio
    async def test_get_member_detail(self, sample_member_data):
        """测试获取成员详情"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先创建一个成员
            create_response = await client.post("/api/v1/members", json=sample_member_data)
            member_id = create_response.json()["data"]["member_id"]
            
            # 获取成员详情
            response = await client.get(f"/api/v1/members/{member_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == member_id
            assert data["name"] is not None
            assert data["role"] == sample_member_data["role"]
            assert "avatar_url" in data
            assert "join_date" in data

    @pytest.mark.asyncio
    async def test_get_members_list(self, batch_member_data):
        """测试获取成员列表"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先创建一些成员
            await client.post("/api/v1/members/batch", json=batch_member_data)
            
            # 获取成员列表
            response = await client.get("/api/v1/members", params={"page": 1, "page_size": 10})
            
            assert response.status_code == 200
            data = response.json()
            assert "members" in data
            assert "total" in data
            assert "page" in data
            assert "page_size" in data
            assert "total_pages" in data
            assert data["page"] == 1
            assert data["page_size"] == 10
            assert len(data["members"]) <= 10

    @pytest.mark.asyncio
    async def test_update_member(self, sample_member_data, sample_update_data):
        """测试更新成员信息"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先创建一个成员
            create_response = await client.post("/api/v1/members", json=sample_member_data)
            member_id = create_response.json()["data"]["member_id"]
            
            # 更新成员信息
            response = await client.put(f"/api/v1/members/{member_id}", json=sample_update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["member_id"] == member_id
            assert data["message"] == "成员信息更新成功"
            
            # 验证更新结果
            detail_response = await client.get(f"/api/v1/members/{member_id}")
            detail_data = detail_response.json()
            assert detail_data["name"] == sample_update_data["display_name"]
            assert detail_data["role"] == sample_update_data["role"]

    @pytest.mark.asyncio
    async def test_delete_member(self, sample_member_data):
        """测试删除成员"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先创建一个成员
            create_response = await client.post("/api/v1/members", json=sample_member_data)
            member_id = create_response.json()["data"]["member_id"]
            
            # 删除成员
            response = await client.delete(f"/api/v1/members/{member_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["member_id"] == member_id
            assert data["message"] == "成员删除成功"
            
            # 验证删除结果 - 应该返回404
            detail_response = await client.get(f"/api/v1/members/{member_id}")
            assert detail_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_member_stats(self, batch_member_data):
        """测试获取成员统计信息"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 先创建一些成员
            await client.post("/api/v1/members/batch", json=batch_member_data)
            
            # 获取统计信息
            response = await client.get("/api/v1/members/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert "total_members" in data
            assert "role_distribution" in data
            assert "join_year_stats" in data
            assert isinstance(data["total_members"], int)
            assert isinstance(data["role_distribution"], dict)
            assert isinstance(data["join_year_stats"], dict)

    @pytest.mark.asyncio
    async def test_invalid_member_id(self):
        """测试无效的成员ID"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 测试获取不存在的成员
            response = await client.get("/api/v1/members/99999")
            assert response.status_code == 404
            
            # 测试更新不存在的成员
            update_data = {"display_name": "测试"}
            response = await client.put("/api/v1/members/99999", json=update_data)
            assert response.status_code == 404
            
            # 测试删除不存在的成员
            response = await client.delete("/api/v1/members/99999")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_parameters(self):
        """测试无效参数"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 测试无效的页码
            response = await client.get("/api/v1/members", params={"page": 0})
            assert response.status_code == 400
            
            # 测试无效的页面大小
            response = await client.get("/api/v1/members", params={"page_size": 101})
            assert response.status_code == 400
            
            # 测试无效的成员ID
            response = await client.get("/api/v1/members/0")
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self, sample_member_data, sample_update_data):
        """测试完整的CRUD工作流程"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 创建成员
            create_response = await client.post("/api/v1/members", json=sample_member_data)
            assert create_response.status_code == 200
            member_id = create_response.json()["data"]["member_id"]
            
            # 2. 读取成员
            read_response = await client.get(f"/api/v1/members/{member_id}")
            assert read_response.status_code == 200
            original_data = read_response.json()
            
            # 3. 更新成员
            update_response = await client.put(f"/api/v1/members/{member_id}", json=sample_update_data)
            assert update_response.status_code == 200
            
            # 4. 验证更新
            updated_read_response = await client.get(f"/api/v1/members/{member_id}")
            assert updated_read_response.status_code == 200
            updated_data = updated_read_response.json()
            assert updated_data["name"] != original_data["name"]
            assert updated_data["role"] != original_data["role"]
            
            # 5. 删除成员
            delete_response = await client.delete(f"/api/v1/members/{member_id}")
            assert delete_response.status_code == 200
            
            # 6. 验证删除
            final_read_response = await client.get(f"/api/v1/members/{member_id}")
            assert final_read_response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
