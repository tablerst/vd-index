#!/usr/bin/env python3
"""
清理测试数据脚本
删除所有测试数据，准备导入真实数据
"""
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.models import Member, engine


def clear_all_data():
    """清理所有成员数据"""
    print("🗑️ 清理所有成员数据...")
    
    try:
        with Session(engine) as session:
            # 查询所有成员
            statement = select(Member)
            members = session.exec(statement).all()
            
            if not members:
                print("✅ 数据库中没有数据需要清理")
                return True
            
            print(f"📊 找到 {len(members)} 个成员记录")
            
            # 确认删除
            response = input("⚠️ 确定要删除所有成员数据吗？(yes/N): ")
            if response.lower() != 'yes':
                print("❌ 取消操作")
                return False
            
            # 删除所有成员
            for member in members:
                session.delete(member)
            
            session.commit()
            
            print(f"✅ 成功删除 {len(members)} 个成员记录")
            return True
            
    except Exception as e:
        print(f"❌ 清理数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🧹 数据清理脚本")
    print("=" * 50)
    
    success = clear_all_data()
    
    if success:
        print("\n🎉 数据清理完成！")
        print("现在可以导入真实的成员数据了")
    else:
        print("\n❌ 数据清理失败！")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
