"""
评论功能测试用例
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from services.database.models import Comment, CommentCreate, CommentCRUD, Member, MemberCRUD
from main import app


class TestCommentCRUD:
    """评论CRUD操作测试"""
    
    @pytest.fixture
    async def sample_member(self, db_session: AsyncSession):
        """创建测试用的成员"""
        from services.database.models import MemberCreate
        member_data = MemberCreate(
            display_name="测试用户",
            uin_encrypted="encrypted_uin_test",
            salt="test_salt_123456",
            role=2,
            join_time=datetime.utcnow()
        )
        member = await MemberCRUD.create(db_session, member_data)
        return member
    
    @pytest.fixture
    async def sample_comment(self, db_session: AsyncSession, sample_member):
        """创建测试用的评论"""
        comment_data = CommentCreate(
            member_id=sample_member.id,
            content="这是一条测试评论",
            is_anonymous=True,
            author_ip="127.0.0.1"
        )
        comment = await CommentCRUD.create(db_session, comment_data)
        return comment
    
    async def test_create_comment(self, db_session: AsyncSession, sample_member):
        """测试创建评论"""
        comment_data = CommentCreate(
            member_id=sample_member.id,
            content="这是一条新评论",
            is_anonymous=True,
            author_ip="192.168.1.1"
        )
        
        comment = await CommentCRUD.create(db_session, comment_data)
        
        assert comment.id is not None
        assert comment.member_id == sample_member.id
        assert comment.content == "这是一条新评论"
        assert comment.likes == 0
        assert comment.dislikes == 0
        assert comment.is_anonymous is True
        assert comment.author_ip == "192.168.1.1"
        assert comment.is_deleted is False
    
    async def test_get_comment_by_id(self, db_session: AsyncSession, sample_comment):
        """测试根据ID获取评论"""
        comment = await CommentCRUD.get_by_id(db_session, sample_comment.id)
        
        assert comment is not None
        assert comment.id == sample_comment.id
        assert comment.content == sample_comment.content
    
    async def test_get_comments_by_member_id(self, db_session: AsyncSession, sample_member):
        """测试获取成员的评论列表"""
        # 创建多条评论
        for i in range(3):
            comment_data = CommentCreate(
                member_id=sample_member.id,
                content=f"评论内容 {i+1}",
                is_anonymous=True,
                author_ip="127.0.0.1"
            )
            await CommentCRUD.create(db_session, comment_data)
        
        # 获取评论列表
        comments = await CommentCRUD.get_by_member_id(db_session, sample_member.id, page=1, page_size=10)
        
        assert len(comments) == 3
        # 验证按时间倒序排列
        assert comments[0].created_at >= comments[1].created_at >= comments[2].created_at
    
    async def test_count_comments_by_member_id(self, db_session: AsyncSession, sample_member):
        """测试统计成员评论数量"""
        # 创建评论
        for i in range(5):
            comment_data = CommentCreate(
                member_id=sample_member.id,
                content=f"评论 {i+1}",
                is_anonymous=True
            )
            await CommentCRUD.create(db_session, comment_data)
        
        count = await CommentCRUD.count_by_member_id(db_session, sample_member.id)
        assert count == 5
    
    async def test_like_comment(self, db_session: AsyncSession, sample_comment):
        """测试点赞评论"""
        original_likes = sample_comment.likes
        
        comment = await CommentCRUD.like_comment(db_session, sample_comment.id)
        
        assert comment is not None
        assert comment.likes == original_likes + 1
    
    async def test_dislike_comment(self, db_session: AsyncSession, sample_comment):
        """测试点踩评论"""
        original_dislikes = sample_comment.dislikes
        
        comment = await CommentCRUD.dislike_comment(db_session, sample_comment.id)
        
        assert comment is not None
        assert comment.dislikes == original_dislikes + 1
    
    async def test_soft_delete_comment(self, db_session: AsyncSession, sample_comment):
        """测试软删除评论"""
        comment = await CommentCRUD.soft_delete(db_session, sample_comment.id)
        
        assert comment is not None
        assert comment.is_deleted is True
    
    async def test_get_stats(self, db_session: AsyncSession, sample_member):
        """测试获取评论统计"""
        # 创建一些测试数据
        for i in range(3):
            comment_data = CommentCreate(
                member_id=sample_member.id,
                content=f"评论 {i+1}",
                is_anonymous=True
            )
            comment = await CommentCRUD.create(db_session, comment_data)
            
            # 给第一条评论点赞和点踩
            if i == 0:
                await CommentCRUD.like_comment(db_session, comment.id)
                await CommentCRUD.like_comment(db_session, comment.id)
                await CommentCRUD.dislike_comment(db_session, comment.id)
        
        # 删除一条评论
        comments = await CommentCRUD.get_by_member_id(db_session, sample_member.id)
        if comments:
            await CommentCRUD.soft_delete(db_session, comments[0].id)
        
        stats = await CommentCRUD.get_stats(db_session)
        
        assert stats.total_comments >= 3
        assert stats.active_comments >= 2
        assert stats.deleted_comments >= 1
        assert stats.total_likes >= 2
        assert stats.total_dislikes >= 1


class TestCommentAPI:
    """评论API测试"""
    
    def setup_method(self):
        """设置测试客户端"""
        self.client = TestClient(app)
    
    def test_get_member_comments_not_found(self):
        """测试获取不存在成员的评论"""
        response = self.client.get("/api/v1/comments/members/99999/comments")
        assert response.status_code == 404
        assert "Member not found" in response.json()["detail"]
    
    def test_create_comment_invalid_member(self):
        """测试为不存在的成员创建评论"""
        comment_data = {
            "content": "测试评论",
            "is_anonymous": True
        }
        response = self.client.post("/api/v1/comments/members/99999/comments", json=comment_data)
        assert response.status_code == 404
        assert "Member not found" in response.json()["detail"]
    
    def test_like_nonexistent_comment(self):
        """测试点赞不存在的评论"""
        response = self.client.put("/api/v1/comments/99999/like")
        assert response.status_code == 404
        assert "Comment not found" in response.json()["detail"]
    
    def test_dislike_nonexistent_comment(self):
        """测试点踩不存在的评论"""
        response = self.client.put("/api/v1/comments/99999/dislike")
        assert response.status_code == 404
        assert "Comment not found" in response.json()["detail"]
    
    def test_delete_nonexistent_comment(self):
        """测试删除不存在的评论"""
        # 注意：这个测试需要认证，实际测试时需要添加认证头
        response = self.client.delete("/api/v1/comments/99999")
        # 可能返回401（未认证）或404（未找到）
        assert response.status_code in [401, 404]


class TestCommentValidation:
    """评论验证测试"""
    
    def test_comment_content_validation(self):
        """测试评论内容验证"""
        from schema.comment_schemas import CommentCreateRequest
        from pydantic import ValidationError
        
        # 测试空内容
        with pytest.raises(ValidationError):
            CommentCreateRequest(content="")
        
        # 测试过长内容
        with pytest.raises(ValidationError):
            CommentCreateRequest(content="a" * 501)
        
        # 测试正常内容
        valid_comment = CommentCreateRequest(content="这是一条正常的评论")
        assert valid_comment.content == "这是一条正常的评论"
        assert valid_comment.is_anonymous is True  # 默认值


@pytest.fixture
async def db_session():
    """数据库会话fixture（需要根据实际数据库配置调整）"""
    # 这里需要根据实际的数据库测试配置来实现
    # 通常会使用测试数据库或内存数据库
    pass
