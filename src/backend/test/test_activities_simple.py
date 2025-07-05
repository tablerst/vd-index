"""
活动API简单测试用例
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """HTTP客户端"""
    with TestClient(app) as client:
        yield client


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
        
        # 验证活动数据结构
        if data["activities"]:
            activity = data["activities"][0]
            assert "id" in activity
            assert "title" in activity
            assert "description" in activity
            assert "date" in activity
            assert "tags" in activity
            assert "participants" in activity
            assert "participants_total" in activity
    
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
        
        # 验证统计数据合理性
        assert data["total_activities"] >= 0
        assert data["total_participants"] >= 0
        assert data["unique_participants"] >= 0
        assert data["unique_participants"] <= data["total_participants"]
    
    def test_get_activity_by_id_existing(self, client):
        """测试获取存在的活动"""
        # 先获取活动列表
        response = client.get("/api/star_calendar/activities")
        assert response.status_code == 200
        
        data = response.json()
        if data["activities"]:
            activity_id = data["activities"][0]["id"]
            
            # 获取具体活动
            response = client.get(f"/api/star_calendar/activity/{activity_id}")
            assert response.status_code == 200
            
            activity_data = response.json()
            assert activity_data["id"] == activity_id
            assert "title" in activity_data
            assert "description" in activity_data
            assert "participants" in activity_data
            assert "participants_total" in activity_data
    
    def test_get_nonexistent_activity(self, client):
        """测试获取不存在的活动"""
        response = client.get("/api/star_calendar/activity/99999")
        assert response.status_code == 404
    
    def test_activities_pagination(self, client):
        """测试活动分页"""
        # 测试第一页
        response = client.get("/api/star_calendar/activities?page=1&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["activities"]) <= 5
        
        # 测试页面大小限制
        response = client.get("/api/star_calendar/activities?page=1&page_size=100")
        assert response.status_code == 200

        data = response.json()
        assert data["page_size"] == 100  # 最大值为100
    
    def test_activities_with_invalid_params(self, client):
        """测试无效参数"""
        # 测试无效页码
        response = client.get("/api/star_calendar/activities?page=0")
        assert response.status_code == 422
        
        # 测试无效页面大小
        response = client.get("/api/star_calendar/activities?page_size=0")
        assert response.status_code == 422
    
    def test_api_response_structure(self, client):
        """测试API响应结构的完整性"""
        # 测试活动列表响应结构
        response = client.get("/api/star_calendar/activities")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["activities", "total", "page", "page_size", "total_pages"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # 测试统计响应结构
        response = client.get("/api/star_calendar/activities/stats")
        assert response.status_code == 200
        
        stats_data = response.json()
        stats_fields = ["total_activities", "total_participants", "unique_participants"]
        for field in stats_fields:
            assert field in stats_data, f"Missing required stats field: {field}"
    
    def test_activity_participants_structure(self, client):
        """测试活动参与者数据结构"""
        response = client.get("/api/star_calendar/activities")
        assert response.status_code == 200
        
        data = response.json()
        if data["activities"]:
            activity = data["activities"][0]
            if activity["participants"]:
                participant = activity["participants"][0]
                assert "id" in participant
                assert "name" in participant
                assert "avatar_url" in participant
                
                # 验证头像URL格式
                assert participant["avatar_url"].startswith("/api/avatar/")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
