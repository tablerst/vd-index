"""
评论功能集成测试
测试完整的评论流程：创建成员 -> 创建评论 -> 点赞点踩 -> 获取列表
"""
import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from services.database.models import (
    Member, MemberCreate, MemberCRUD,
    Comment, CommentCreate, CommentCRUD
)


class TestCommentIntegration:
    """评论功能集成测试"""
    
    @pytest.fixture
    async def test_member(self, db_session: AsyncSession):
        """创建测试成员"""
        member_data = MemberCreate(
            display_name="集成测试用户",
            uin_encrypted="integration_test_uin",
            salt="integration_salt_123",
            role=2,
            join_time=datetime.utcnow()
        )
        member = await MemberCRUD.create(db_session, member_data)
        return member
    
    async def test_complete_comment_workflow(self, db_session: AsyncSession, test_member):
        """测试完整的评论工作流程"""
        
        # 1. 创建评论
        comment_data = CommentCreate(
            member_id=test_member.id,
            content="这是一条集成测试评论",
            is_anonymous=True,
            author_ip="127.0.0.1"
        )
        comment = await CommentCRUD.create(db_session, comment_data)
        
        assert comment.id is not None
        assert comment.content == "这是一条集成测试评论"
        assert comment.likes == 0
        assert comment.dislikes == 0
        
        # 2. 点赞评论
        liked_comment = await CommentCRUD.like_comment(db_session, comment.id)
        assert liked_comment.likes == 1
        
        # 再次点赞
        liked_comment = await CommentCRUD.like_comment(db_session, comment.id)
        assert liked_comment.likes == 2
        
        # 3. 点踩评论
        disliked_comment = await CommentCRUD.dislike_comment(db_session, comment.id)
        assert disliked_comment.dislikes == 1
        assert disliked_comment.likes == 2  # 点赞数不变
        
        # 4. 获取成员评论列表
        comments = await CommentCRUD.get_by_member_id(db_session, test_member.id)
        assert len(comments) == 1
        assert comments[0].id == comment.id
        assert comments[0].likes == 2
        assert comments[0].dislikes == 1
        
        # 5. 统计评论数量
        count = await CommentCRUD.count_by_member_id(db_session, test_member.id)
        assert count == 1
        
        # 6. 获取统计信息
        stats = await CommentCRUD.get_stats(db_session)
        assert stats.total_comments >= 1
        assert stats.active_comments >= 1
        assert stats.total_likes >= 2
        assert stats.total_dislikes >= 1
    
    async def test_multiple_comments_ordering(self, db_session: AsyncSession, test_member):
        """测试多条评论的排序"""
        
        # 创建多条评论（有时间间隔）
        comments_data = [
            "第一条评论",
            "第二条评论", 
            "第三条评论"
        ]
        
        created_comments = []
        for i, content in enumerate(comments_data):
            comment_data = CommentCreate(
                member_id=test_member.id,
                content=content,
                is_anonymous=True,
                author_ip="127.0.0.1"
            )
            comment = await CommentCRUD.create(db_session, comment_data)
            created_comments.append(comment)
            
            # 模拟时间间隔
            await asyncio.sleep(0.01)
        
        # 获取评论列表（应该按时间倒序）
        comments = await CommentCRUD.get_by_member_id(db_session, test_member.id)
        
        assert len(comments) == 3
        assert comments[0].content == "第三条评论"  # 最新的在前
        assert comments[1].content == "第二条评论"
        assert comments[2].content == "第一条评论"
        
        # 验证时间顺序
        assert comments[0].created_at >= comments[1].created_at >= comments[2].created_at
    
    async def test_comment_pagination(self, db_session: AsyncSession, test_member):
        """测试评论分页"""
        
        # 创建10条评论
        for i in range(10):
            comment_data = CommentCreate(
                member_id=test_member.id,
                content=f"分页测试评论 {i+1}",
                is_anonymous=True,
                author_ip="127.0.0.1"
            )
            await CommentCRUD.create(db_session, comment_data)
        
        # 测试第一页（5条）
        page1_comments = await CommentCRUD.get_by_member_id(
            db_session, test_member.id, page=1, page_size=5
        )
        assert len(page1_comments) == 5
        
        # 测试第二页（5条）
        page2_comments = await CommentCRUD.get_by_member_id(
            db_session, test_member.id, page=2, page_size=5
        )
        assert len(page2_comments) == 5
        
        # 验证分页内容不重复
        page1_ids = {c.id for c in page1_comments}
        page2_ids = {c.id for c in page2_comments}
        assert page1_ids.isdisjoint(page2_ids)
        
        # 验证总数
        total_count = await CommentCRUD.count_by_member_id(db_session, test_member.id)
        assert total_count == 10
    
    async def test_soft_delete_workflow(self, db_session: AsyncSession, test_member):
        """测试软删除工作流程"""
        
        # 创建评论
        comment_data = CommentCreate(
            member_id=test_member.id,
            content="将要被删除的评论",
            is_anonymous=True,
            author_ip="127.0.0.1"
        )
        comment = await CommentCRUD.create(db_session, comment_data)
        
        # 点赞评论
        await CommentCRUD.like_comment(db_session, comment.id)
        
        # 软删除评论
        deleted_comment = await CommentCRUD.soft_delete(db_session, comment.id)
        assert deleted_comment.is_deleted is True
        
        # 验证删除后的行为
        # 1. 直接获取仍然可以找到
        found_comment = await CommentCRUD.get_by_id(db_session, comment.id)
        assert found_comment is not None
        assert found_comment.is_deleted is True
        
        # 2. 在成员评论列表中不显示（默认不包含已删除）
        active_comments = await CommentCRUD.get_by_member_id(
            db_session, test_member.id, include_deleted=False
        )
        assert len(active_comments) == 0
        
        # 3. 包含已删除的查询可以找到
        all_comments = await CommentCRUD.get_by_member_id(
            db_session, test_member.id, include_deleted=True
        )
        assert len(all_comments) == 1
        assert all_comments[0].is_deleted is True
        
        # 4. 统计数据正确
        active_count = await CommentCRUD.count_by_member_id(
            db_session, test_member.id, include_deleted=False
        )
        total_count = await CommentCRUD.count_by_member_id(
            db_session, test_member.id, include_deleted=True
        )
        assert active_count == 0
        assert total_count == 1
        
        # 5. 已删除评论不能再点赞点踩
        like_result = await CommentCRUD.like_comment(db_session, comment.id)
        assert like_result is None
        
        dislike_result = await CommentCRUD.dislike_comment(db_session, comment.id)
        assert dislike_result is None
    
    async def test_high_dislike_comments(self, db_session: AsyncSession, test_member):
        """测试高点踩评论查询"""
        
        # 创建评论并设置不同的点踩数
        comments_data = [
            ("正常评论", 2),
            ("争议评论", 8),
            ("高点踩评论1", 15),
            ("高点踩评论2", 20)
        ]
        
        for content, dislike_count in comments_data:
            comment_data = CommentCreate(
                member_id=test_member.id,
                content=content,
                is_anonymous=True,
                author_ip="127.0.0.1"
            )
            comment = await CommentCRUD.create(db_session, comment_data)
            
            # 模拟点踩
            for _ in range(dislike_count):
                await CommentCRUD.dislike_comment(db_session, comment.id)
        
        # 查询点踩数 >= 10 的评论
        high_dislike_comments = await CommentCRUD.get_high_dislike_comments(
            db_session, threshold=10
        )
        
        assert len(high_dislike_comments) == 2
        assert high_dislike_comments[0].dislikes >= high_dislike_comments[1].dislikes  # 按点踩数倒序
        assert all(c.dislikes >= 10 for c in high_dislike_comments)


# 数据库fixture（需要根据实际配置调整）
@pytest.fixture
async def db_session():
    """
    数据库会话fixture
    实际使用时需要配置测试数据库
    """
    # 这里应该返回实际的数据库会话
    # 例如使用pytest-asyncio和测试数据库
    pass


if __name__ == "__main__":
    """
    运行集成测试的示例
    """
    print("评论功能集成测试")
    print("请确保已配置测试数据库并运行：")
    print("cd src/backend && python -m pytest test/test_integration_comments.py -v")
