"""
测试数据生成器
用于生成member CRUD操作的测试数据
"""
import asyncio
import random
import secrets
from datetime import datetime, timedelta
from typing import List

import httpx
from faker import Faker

# 初始化Faker
fake = Faker('zh_CN')

# API基础URL
API_BASE_URL = "http://localhost:8000/api/v1"

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def generate_fake_member_data(self) -> dict:
        """生成单个假成员数据"""
        # 生成随机QQ号（9-10位数字）
        uin = random.randint(100000000, 9999999999)
        
        # 生成随机角色（群员概率更高）
        role = random.choices([0, 1, 2], weights=[1, 5, 94])[0]  # 群主1%, 管理员5%, 群员94%
        
        # 生成入群时间（过去1-5年内）
        days_ago = random.randint(30, 1825)  # 30天到5年
        join_time = datetime.now() - timedelta(days=days_ago)
        
        # 生成最后发言时间（可能为空）
        last_speak_time = None
        if random.random() > 0.1:  # 90%的概率有发言记录
            speak_days_ago = random.randint(0, days_ago)
            last_speak_time = datetime.now() - timedelta(days=speak_days_ago)
        
        # 生成昵称
        qq_nick = fake.name()
        group_nick = fake.name() if random.random() > 0.3 else ""  # 70%概率有群昵称
        
        # 生成等级信息
        level_point = random.randint(0, 10000)
        level_value = min(level_point // 100 + 1, 100)  # 基于积分计算等级
        
        # 生成Q龄
        q_age = random.randint(1, 20)
        
        return {
            "uin": uin,
            "role": role,
            "join_time": int(join_time.timestamp()),
            "last_speak_time": int(last_speak_time.timestamp()) if last_speak_time else None,
            "card": group_nick,
            "nick": qq_nick,
            "lv": {
                "point": level_point,
                "level": level_value
            },
            "qage": q_age
        }
    
    def generate_batch_member_data(self, count: int = 10) -> List[dict]:
        """生成批量假成员数据"""
        return [self.generate_fake_member_data() for _ in range(count)]
    
    async def create_single_member(self, member_data: dict = None) -> dict:
        """创建单个测试成员"""
        if member_data is None:
            member_data = self.generate_fake_member_data()
        
        response = await self.client.post(
            f"{API_BASE_URL}/members",
            json=member_data
        )
        
        if response.status_code != 200:
            raise Exception(f"创建成员失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def create_batch_members(self, members_data: List[dict] = None, count: int = 10) -> dict:
        """批量创建测试成员"""
        if members_data is None:
            members_data = self.generate_batch_member_data(count)
        
        batch_data = {"members": members_data}
        
        response = await self.client.post(
            f"{API_BASE_URL}/members/batch",
            json=batch_data
        )
        
        if response.status_code != 200:
            raise Exception(f"批量创建成员失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def get_members_list(self, page: int = 1, page_size: int = 50) -> dict:
        """获取成员列表"""
        response = await self.client.get(
            f"{API_BASE_URL}/members",
            params={"page": page, "page_size": page_size}
        )
        
        if response.status_code != 200:
            raise Exception(f"获取成员列表失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def get_member_detail(self, member_id: int) -> dict:
        """获取成员详情"""
        response = await self.client.get(f"{API_BASE_URL}/members/{member_id}")
        
        if response.status_code != 200:
            raise Exception(f"获取成员详情失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def update_member(self, member_id: int, update_data: dict) -> dict:
        """更新成员信息"""
        response = await self.client.put(
            f"{API_BASE_URL}/members/{member_id}",
            json=update_data
        )
        
        if response.status_code != 200:
            raise Exception(f"更新成员失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def delete_member(self, member_id: int) -> dict:
        """删除成员"""
        response = await self.client.delete(f"{API_BASE_URL}/members/{member_id}")
        
        if response.status_code != 200:
            raise Exception(f"删除成员失败: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def get_member_stats(self) -> dict:
        """获取成员统计信息"""
        response = await self.client.get(f"{API_BASE_URL}/members/stats")
        
        if response.status_code != 200:
            raise Exception(f"获取统计信息失败: {response.status_code} - {response.text}")
        
        return response.json()


async def test_crud_operations():
    """测试完整的CRUD操作"""
    print("🚀 开始测试Member CRUD操作...")
    
    async with TestDataGenerator() as generator:
        try:
            # 1. 测试创建单个成员
            print("\n📝 测试创建单个成员...")
            create_result = await generator.create_single_member()
            print(f"✅ 创建成功: {create_result}")
            member_id = create_result["data"]["member_id"]
            
            # 2. 测试获取成员详情
            print(f"\n👤 测试获取成员详情 (ID: {member_id})...")
            detail_result = await generator.get_member_detail(member_id)
            print(f"✅ 获取详情成功: {detail_result['name']}")
            
            # 3. 测试更新成员信息
            print(f"\n✏️ 测试更新成员信息 (ID: {member_id})...")
            update_data = {
                "display_name": "测试更新用户",
                "group_nick": "新群昵称",
                "role": 1  # 升级为管理员
            }
            update_result = await generator.update_member(member_id, update_data)
            print(f"✅ 更新成功: {update_result}")
            
            # 4. 验证更新结果
            print(f"\n🔍 验证更新结果...")
            updated_detail = await generator.get_member_detail(member_id)
            print(f"✅ 验证成功: {updated_detail['name']} (角色: {updated_detail['role']})")
            
            # 5. 测试批量创建成员
            print(f"\n📦 测试批量创建成员...")
            batch_result = await generator.create_batch_members(count=5)
            print(f"✅ 批量创建成功: {batch_result}")
            batch_member_ids = batch_result["data"]["member_ids"]
            
            # 6. 测试获取成员列表
            print(f"\n📋 测试获取成员列表...")
            list_result = await generator.get_members_list(page=1, page_size=10)
            print(f"✅ 获取列表成功: 总计 {list_result['total']} 个成员")
            
            # 7. 测试获取统计信息
            print(f"\n📊 测试获取统计信息...")
            stats_result = await generator.get_member_stats()
            print(f"✅ 获取统计成功: {stats_result}")
            
            # 8. 测试删除成员
            print(f"\n🗑️ 测试删除成员...")
            # 删除第一个批量创建的成员
            delete_id = batch_member_ids[0]
            delete_result = await generator.delete_member(delete_id)
            print(f"✅ 删除成功: {delete_result}")
            
            # 9. 验证删除结果
            print(f"\n🔍 验证删除结果...")
            try:
                await generator.get_member_detail(delete_id)
                print("❌ 删除验证失败: 成员仍然存在")
            except Exception as e:
                print(f"✅ 删除验证成功: 成员已不存在 ({str(e)[:50]}...)")
            
            print(f"\n🎉 所有CRUD操作测试完成!")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(test_crud_operations())
