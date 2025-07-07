"""
Member CRUD操作的简化pytest测试用例
使用TestClient进行测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from main import app

# 创建测试客户端
client = TestClient(app)


class TestMemberCRUDSimple:
    """Member CRUD操作简化测试类"""
    
    def test_create_single_member(self):
        """测试创建单个成员"""
        member_data = {
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
        
        response = client.post("/api/v1/members", json=member_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "member_id" in data["data"]
        assert data["message"] == "成员创建成功"
        
        return data["data"]["member_id"]

    def test_create_batch_members(self):
        """测试批量创建成员"""
        base_time = int(datetime.now().timestamp())
        batch_data = {
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
                }
            ]
        }
        
        response = client.post("/api/v1/members/batch", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "member_ids" in data["data"]
        assert len(data["data"]["member_ids"]) == 2
        assert "批量创建成功" in data["message"]
        
        return data["data"]["member_ids"]

    def test_get_member_detail(self):
        """测试获取成员详情"""
        # 先创建一个成员
        member_data = {
            "uin": 987654321,
            "role": 1,
            "join_time": int(datetime.now().timestamp()),
            "last_speak_time": int(datetime.now().timestamp()),
            "card": "详情测试用户",
            "nick": "详情测试QQ",
            "lv": {"point": 2000, "level": 20},
            "qage": 8
        }
        
        create_response = client.post("/api/v1/members", json=member_data)
        member_id = create_response.json()["data"]["member_id"]
        
        # 获取成员详情
        response = client.get(f"/api/v1/members/{member_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == member_id
        assert data["name"] is not None
        assert data["role"] == member_data["role"]
        assert "avatar_url" in data
        assert "join_date" in data

    def test_get_members_list(self):
        """测试获取成员列表"""
        # 获取成员列表
        response = client.get("/api/v1/members", params={"page": 1, "page_size": 10})
        
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

    def test_update_member(self):
        """测试更新成员信息"""
        # 先创建一个成员
        member_data = {
            "uin": 555666777,
            "role": 2,
            "join_time": int(datetime.now().timestamp()),
            "last_speak_time": int(datetime.now().timestamp()),
            "card": "更新测试用户",
            "nick": "更新测试QQ",
            "lv": {"point": 800, "level": 8},
            "qage": 4
        }
        
        create_response = client.post("/api/v1/members", json=member_data)
        member_id = create_response.json()["data"]["member_id"]
        
        # 更新成员信息
        update_data = {
            "display_name": "更新后的名称",
            "group_nick": "更新后的群昵称",
            "role": 1,
            "level_point": 2000,
            "level_value": 20
        }
        
        response = client.put(f"/api/v1/members/{member_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["member_id"] == member_id
        assert data["message"] == "成员信息更新成功"
        
        # 验证更新结果
        detail_response = client.get(f"/api/v1/members/{member_id}")
        detail_data = detail_response.json()
        assert detail_data["name"] == update_data["display_name"]
        assert detail_data["role"] == update_data["role"]

    def test_delete_member(self):
        """测试删除成员"""
        # 先创建一个成员
        member_data = {
            "uin": 888999000,
            "role": 2,
            "join_time": int(datetime.now().timestamp()),
            "last_speak_time": int(datetime.now().timestamp()),
            "card": "删除测试用户",
            "nick": "删除测试QQ",
            "lv": {"point": 300, "level": 3},
            "qage": 2
        }
        
        create_response = client.post("/api/v1/members", json=member_data)
        member_id = create_response.json()["data"]["member_id"]
        
        # 删除成员
        response = client.delete(f"/api/v1/members/{member_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["member_id"] == member_id
        assert data["message"] == "成员删除成功"
        
        # 验证删除结果 - 应该返回404
        detail_response = client.get(f"/api/v1/members/{member_id}")
        assert detail_response.status_code == 404

    def test_get_member_stats(self):
        """测试获取成员统计信息"""
        # 获取统计信息
        response = client.get("/api/v1/members/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_members" in data
        assert "role_distribution" in data
        assert "join_year_stats" in data
        assert isinstance(data["total_members"], int)
        assert isinstance(data["role_distribution"], dict)
        assert isinstance(data["join_year_stats"], dict)

    def test_invalid_member_id(self):
        """测试无效的成员ID"""
        # 测试获取不存在的成员
        response = client.get("/api/v1/members/99999")
        assert response.status_code == 404
        
        # 测试更新不存在的成员
        update_data = {"display_name": "测试"}
        response = client.put("/api/v1/members/99999", json=update_data)
        assert response.status_code == 404
        
        # 测试删除不存在的成员
        response = client.delete("/api/v1/members/99999")
        assert response.status_code == 404

    def test_invalid_parameters(self):
        """测试无效参数"""
        # 测试无效的页码
        response = client.get("/api/v1/members", params={"page": 0})
        assert response.status_code == 400
        
        # 测试无效的页面大小
        response = client.get("/api/v1/members", params={"page_size": 101})
        assert response.status_code == 400
        
        # 测试无效的成员ID
        response = client.get("/api/v1/members/0")
        assert response.status_code == 400

    def test_complete_crud_workflow(self):
        """测试完整的CRUD工作流程"""
        # 1. 创建成员
        member_data = {
            "uin": 777888999,
            "role": 2,
            "join_time": int(datetime.now().timestamp()),
            "last_speak_time": int(datetime.now().timestamp()),
            "card": "完整流程测试用户",
            "nick": "完整流程测试QQ",
            "lv": {"point": 1200, "level": 12},
            "qage": 6
        }
        
        create_response = client.post("/api/v1/members", json=member_data)
        assert create_response.status_code == 200
        member_id = create_response.json()["data"]["member_id"]
        
        # 2. 读取成员
        read_response = client.get(f"/api/v1/members/{member_id}")
        assert read_response.status_code == 200
        original_data = read_response.json()
        
        # 3. 更新成员
        update_data = {
            "display_name": "更新后的完整流程用户",
            "role": 1,
            "level_point": 2500,
            "level_value": 25
        }
        update_response = client.put(f"/api/v1/members/{member_id}", json=update_data)
        assert update_response.status_code == 200
        
        # 4. 验证更新
        updated_read_response = client.get(f"/api/v1/members/{member_id}")
        assert updated_read_response.status_code == 200
        updated_data = updated_read_response.json()
        assert updated_data["name"] != original_data["name"]
        assert updated_data["role"] != original_data["role"]
        
        # 5. 删除成员
        delete_response = client.delete(f"/api/v1/members/{member_id}")
        assert delete_response.status_code == 200
        
        # 6. 验证删除
        final_read_response = client.get(f"/api/v1/members/{member_id}")
        assert final_read_response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
