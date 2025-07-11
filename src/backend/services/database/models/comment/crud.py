"""
评论CRUD操作
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base import Comment, CommentCreate, CommentUpdate, CommentStats


class CommentCRUD:
    """评论CRUD操作类"""
    
    @staticmethod
    async def create(db: AsyncSession, comment_data: CommentCreate) -> Comment:
        """创建新评论"""
        comment = Comment(**comment_data.model_dump())
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    
    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """根据ID获取评论"""
        result = await db.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_member_id(
        db: AsyncSession, 
        member_id: int, 
        page: int = 1, 
        page_size: int = 20,
        include_deleted: bool = False
    ) -> List[Comment]:
        """获取某成员的评论列表（分页）"""
        offset = (page - 1) * page_size
        
        query = select(Comment).where(Comment.member_id == member_id)
        
        if not include_deleted:
            query = query.where(Comment.is_deleted == False)
        
        query = query.order_by(desc(Comment.created_at)).offset(offset).limit(page_size)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_member_id(
        db: AsyncSession, 
        member_id: int, 
        include_deleted: bool = False
    ) -> int:
        """统计某成员的评论数量"""
        query = select(func.count(Comment.id)).where(Comment.member_id == member_id)
        
        if not include_deleted:
            query = query.where(Comment.is_deleted == False)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        comment_id: int, 
        comment_data: CommentUpdate
    ) -> Optional[Comment]:
        """更新评论"""
        comment = await CommentCRUD.get_by_id(db, comment_id)
        if not comment:
            return None
        
        update_data = comment_data.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            for field, value in update_data.items():
                setattr(comment, field, value)
            
            await db.commit()
            await db.refresh(comment)
        
        return comment
    
    @staticmethod
    async def like_comment(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """点赞评论"""
        comment = await CommentCRUD.get_by_id(db, comment_id)
        if not comment or comment.is_deleted:
            return None
        
        comment.likes += 1
        comment.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(comment)
        return comment
    
    @staticmethod
    async def dislike_comment(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """点踩评论"""
        comment = await CommentCRUD.get_by_id(db, comment_id)
        if not comment or comment.is_deleted:
            return None
        
        comment.dislikes += 1
        comment.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(comment)
        return comment
    
    @staticmethod
    async def soft_delete(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """软删除评论"""
        comment = await CommentCRUD.get_by_id(db, comment_id)
        if not comment:
            return None
        
        comment.is_deleted = True
        comment.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(comment)
        return comment
    
    @staticmethod
    async def get_stats(db: AsyncSession) -> CommentStats:
        """获取评论统计信息"""
        # 总评论数
        total_result = await db.execute(select(func.count(Comment.id)))
        total_comments = total_result.scalar() or 0
        
        # 活跃评论数
        active_result = await db.execute(
            select(func.count(Comment.id)).where(Comment.is_deleted == False)
        )
        active_comments = active_result.scalar() or 0
        
        # 已删除评论数
        deleted_comments = total_comments - active_comments
        
        # 总点赞数
        likes_result = await db.execute(
            select(func.sum(Comment.likes)).where(Comment.is_deleted == False)
        )
        total_likes = likes_result.scalar() or 0
        
        # 总点踩数
        dislikes_result = await db.execute(
            select(func.sum(Comment.dislikes)).where(Comment.is_deleted == False)
        )
        total_dislikes = dislikes_result.scalar() or 0
        
        return CommentStats(
            total_comments=total_comments,
            total_likes=total_likes,
            total_dislikes=total_dislikes,
            active_comments=active_comments,
            deleted_comments=deleted_comments
        )
    
    @staticmethod
    async def get_high_dislike_comments(
        db: AsyncSession, 
        threshold: int = 10, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[Comment]:
        """获取高点踩数的评论（用于管理员清理）"""
        offset = (page - 1) * page_size
        
        query = select(Comment).where(
            and_(
                Comment.dislikes >= threshold,
                Comment.is_deleted == False
            )
        ).order_by(desc(Comment.dislikes)).offset(offset).limit(page_size)
        
        result = await db.execute(query)
        return result.scalars().all()
