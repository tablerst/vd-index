import requests
import json
import os
import time
from typing import List, Dict, Any
from pathlib import Path
import avatar_config


class QQAvatarDownloader:
    def __init__(self):
        self.base_url = "https://q.qlogo.cn/g"
        self.headers = {
            'User-Agent': avatar_config.USER_AGENT
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_avatar_url(self, uin: str, size: str = "640") -> str:
        """
        构建QQ头像URL
        
        Args:
            uin: QQ号
            size: 头像尺寸 (40, 100, 140, 640)
            
        Returns:
            头像URL
        """
        return f"{self.base_url}?b=qq&nk={uin}&s={size}"
    
    def download_avatar(self, uin: str, save_path: str, size: str = "640") -> bool:
        """
        下载单个头像
        
        Args:
            uin: QQ号
            save_path: 保存路径
            size: 头像尺寸
            
        Returns:
            是否下载成功
        """
        url = self.get_avatar_url(uin, size)
        
        try:
            response = self.session.get(url, timeout=avatar_config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                print(f"警告: QQ号 {uin} 的响应不是图片类型: {content_type}")
                return False
            
            # 根据内容类型确定文件扩展名
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = avatar_config.DEFAULT_FORMAT  # 默认格式
            
            # 更新保存路径的扩展名
            save_path = save_path.rsplit('.', 1)[0] + ext
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ 下载成功: {uin} -> {os.path.basename(save_path)}")
            return True
            
        except requests.RequestException as e:
            print(f"✗ 下载失败: {uin} - {e}")
            return False
        except Exception as e:
            print(f"✗ 保存失败: {uin} - {e}")
            return False
    
    def load_members_from_json(self, json_file: str) -> List[Dict[str, Any]]:
        """
        从JSON文件加载成员信息
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            成员列表
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            members = data.get('mems', [])
            print(f"从 {json_file} 加载了 {len(members)} 个成员")
            return members
            
        except FileNotFoundError:
            print(f"错误: 文件 {json_file} 不存在")
            return []
        except json.JSONDecodeError as e:
            print(f"错误: JSON解析失败 - {e}")
            return []
        except Exception as e:
            print(f"错误: 加载文件失败 - {e}")
            return []
    
    def create_avatar_directory(self, group_id: str) -> str:
        """
        创建头像保存目录
        
        Args:
            group_id: 群组ID
            
        Returns:
            目录路径
        """
        avatar_dir = avatar_config.AVATAR_DIR_TEMPLATE.format(group_id=group_id)
        Path(avatar_dir).mkdir(parents=True, exist_ok=True)
        return avatar_dir
    
    def download_all_avatars(self, json_file: str, group_id: str = None, 
                           size: str = "640", delay: float = 0.2) -> Dict[str, int]:
        """
        批量下载所有成员头像
        
        Args:
            json_file: 成员JSON文件路径
            group_id: 群组ID，如果为None则从文件名推断
            size: 头像尺寸
            delay: 请求间隔时间(秒)
            
        Returns:
            下载统计信息
        """
        # 加载成员数据
        members = self.load_members_from_json(json_file)
        if not members:
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        # 推断群组ID
        if group_id is None:
            # 从文件名推断群组ID (例如: qq_group_937303337_members.json)
            filename = os.path.basename(json_file)
            if filename.startswith('qq_group_') and filename.endswith('_members.json'):
                group_id = filename[9:-13]  # 提取群组ID
            else:
                group_id = 'unknown'
        
        # 创建保存目录
        avatar_dir = self.create_avatar_directory(group_id)
        print(f"头像保存目录: {avatar_dir}")
        
        # 统计信息
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        total = len(members)
        
        print(f"\n开始下载 {total} 个成员的头像...")
        print(f"头像尺寸: {size}x{size}")
        print(f"请求间隔: {delay}秒")
        print("-" * 50)
        
        for i, member in enumerate(members, 1):
            uin = str(member.get('uin', ''))
            if not uin:
                print(f"跳过: 第{i}个成员没有uin字段")
                stats['skipped'] += 1
                continue
            
            # 检查文件是否已存在
            if avatar_config.SKIP_EXISTING:
                existing_file = None
                for fmt in avatar_config.SUPPORTED_FORMATS:
                    avatar_path = os.path.join(avatar_dir, f"{uin}{fmt}")
                    if os.path.exists(avatar_path):
                        existing_file = avatar_path
                        break

                if existing_file:
                    print(f"跳过: {uin} (文件已存在: {os.path.basename(existing_file)})")
                    stats['skipped'] += 1
                    continue
            
            # 显示进度
            nick = member.get('nick', '未知')
            card = member.get('card', '')
            display_name = card if card else nick
            print(f"[{i}/{total}] 下载: {uin} ({display_name})")
            
            # 下载头像
            avatar_path = os.path.join(avatar_dir, f"{uin}.jpg")  # 默认jpg，实际会根据响应调整
            if self.download_avatar(uin, avatar_path, size):
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            # 添加延迟
            if delay > 0 and i < total:
                time.sleep(delay)
        
        return stats
    
    def print_summary(self, stats: Dict[str, int], group_id: str):
        """
        打印下载摘要
        
        Args:
            stats: 统计信息
            group_id: 群组ID
        """
        total = stats['success'] + stats['failed'] + stats['skipped']
        
        print("\n" + "=" * 50)
        print("下载完成摘要")
        print("=" * 50)
        print(f"群组ID: {group_id}")
        print(f"总成员数: {total}")
        print(f"下载成功: {stats['success']}")
        print(f"下载失败: {stats['failed']}")
        print(f"跳过文件: {stats['skipped']}")
        print(f"成功率: {stats['success']/max(1, total-stats['skipped'])*100:.1f}%")
        print(f"保存位置: ./avatars/{group_id}/")


def find_member_json_files() -> List[str]:
    """查找当前目录下的成员JSON文件"""
    json_files = []
    for file in os.listdir('.'):
        if file.startswith('qq_group_') and file.endswith('_members.json'):
            json_files.append(file)
    return sorted(json_files)


def main():
    """主函数"""
    downloader = QQAvatarDownloader()

    # 使用配置文件中的参数
    json_file = avatar_config.MEMBERS_JSON_FILE
    group_id = avatar_config.GROUP_ID
    avatar_size = avatar_config.AVATAR_SIZE
    request_delay = avatar_config.REQUEST_DELAY

    print("QQ群成员头像批量下载工具")
    print("=" * 50)

    # 检查配置的文件是否存在，如果不存在则尝试自动查找
    if not os.path.exists(json_file):
        print(f"配置的文件 {json_file} 不存在，正在查找可用文件...")
        available_files = find_member_json_files()

        if not available_files:
            print("\n错误: 未找到任何成员JSON文件")
            print("请确保已运行 main.py 生成成员数据文件")
            return

        if len(available_files) == 1:
            json_file = available_files[0]
            print(f"自动选择文件: {json_file}")
        else:
            print(f"\n找到 {len(available_files)} 个成员文件:")
            for i, file in enumerate(available_files, 1):
                print(f"  {i}. {file}")

            try:
                choice = input(f"\n请选择要处理的文件 (1-{len(available_files)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(available_files):
                    json_file = available_files[index]
                    print(f"选择了文件: {json_file}")
                else:
                    print("无效选择，退出")
                    return
            except (ValueError, KeyboardInterrupt):
                print("退出")
                return

    print(f"成员文件: {json_file}")
    print(f"头像尺寸: {avatar_size}x{avatar_size}")
    print(f"请求间隔: {request_delay}秒")
    print(f"跳过已存在: {'是' if avatar_config.SKIP_EXISTING else '否'}")
    
    # 开始下载
    stats = downloader.download_all_avatars(
        json_file=json_file,
        group_id=group_id,
        size=avatar_size,
        delay=request_delay
    )
    
    # 打印摘要
    final_group_id = group_id
    if final_group_id is None:
        filename = os.path.basename(json_file)
        if filename.startswith('qq_group_') and filename.endswith('_members.json'):
            final_group_id = filename[9:-13]
        else:
            final_group_id = 'unknown'
    
    downloader.print_summary(stats, final_group_id)

if __name__ == "__main__":
    main()
