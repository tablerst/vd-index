"""
管理员API路由
"""
import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session

from core.database import get_session
from schema.member_schemas import ImportBatchRequest, ApiResponse, ImportMemberRequest
from domain.avatar_service import AvatarService
from domain.member_service import MemberService
from core.crypto import decrypt_uin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post(
    "/import-json",
    response_model=ApiResponse,
    summary="导入JSON成员数据",
    description="从QQ群导出的JSON文件批量导入成员数据"
)
async def import_members_from_json(
    batch_request: ImportBatchRequest,
    session: Session = Depends(get_session)
):
    """从JSON数据批量导入成员"""
    try:
        imported_count = 0
        failed_count = 0
        failed_members = []
        
        for member_data in batch_request.members:
            try:
                # 导入成员数据
                member = MemberService.import_member_from_json(session, member_data)
                
                # 复制头像文件
                try:
                    AvatarService.copy_avatar_file(member_data.uin, member.salt)
                except Exception as avatar_error:
                    print(f"复制头像失败 UIN {member_data.uin}: {avatar_error}")
                
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_members.append({
                    "uin": member_data.uin,
                    "error": str(e)
                })
                print(f"导入成员失败 UIN {member_data.uin}: {e}")
        
        return ApiResponse(
            success=True,
            message=f"导入完成：成功 {imported_count} 个，失败 {failed_count} 个",
            data={
                "imported_count": imported_count,
                "failed_count": failed_count,
                "failed_members": failed_members
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")


@router.post(
    "/import-file",
    response_model=ApiResponse,
    summary="上传JSON文件导入",
    description="上传QQ群成员JSON文件进行批量导入"
)
async def import_members_from_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """从上传的JSON文件导入成员"""
    # 验证文件类型
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON文件")
    
    try:
        # 读取文件内容
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        # 解析成员数据
        if 'mems' not in data:
            raise HTTPException(status_code=400, detail="JSON文件格式错误，缺少mems字段")
        
        members_data = []
        for mem in data['mems']:
            member_request = ImportMemberRequest(
                uin=mem['uin'],
                role=mem['role'],
                join_time=mem['join_time'],
                last_speak_time=mem.get('last_speak_time'),
                card=mem['card'],
                nick=mem['nick'],
                lv=mem['lv'],
                qage=mem.get('qage', 0)
            )
            members_data.append(member_request)
        
        # 创建批量导入请求
        batch_request = ImportBatchRequest(members=members_data)
        
        # 执行导入
        return await import_members_from_json(batch_request, session)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件导入失败: {str(e)}")


@router.get(
    "/decrypt-uin/{member_id}",
    summary="解密成员UIN（调试用）",
    description="解密指定成员的UIN，仅用于调试和验证"
)
async def decrypt_member_uin(
    member_id: int,
    session: Session = Depends(get_session)
):
    """解密成员UIN（仅用于调试）"""
    from backend.services.database.models.member import Member
    
    member = session.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    try:
        decrypted_uin = decrypt_uin(member.uin_encrypted, member.salt)
        return {
            "member_id": member_id,
            "display_name": member.display_name,
            "decrypted_uin": decrypted_uin,
            "avatar_hash": member.avatar_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解密失败: {str(e)}")


@router.get(
    "/database-stats",
    summary="获取数据库统计信息",
    description="获取数据库的详细统计信息"
)
async def get_database_stats(session: Session = Depends(get_session)):
    """获取数据库统计信息"""
    try:
        from sqlmodel import select, func
        from backend.services.database.models.member import Member
        
        # 基本统计
        total_members = session.exec(select(func.count(Member.id))).one()
        
        # 最新和最早的成员
        latest_member = session.exec(
            select(Member).order_by(Member.created_at.desc()).limit(1)
        ).first()
        
        earliest_member = session.exec(
            select(Member).order_by(Member.created_at.asc()).limit(1)
        ).first()
        
        return {
            "total_members": total_members,
            "latest_member": {
                "id": latest_member.id,
                "name": latest_member.display_name,
                "created_at": latest_member.created_at.isoformat()
            } if latest_member else None,
            "earliest_member": {
                "id": earliest_member.id,
                "name": earliest_member.display_name,
                "created_at": earliest_member.created_at.isoformat()
            } if earliest_member else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
