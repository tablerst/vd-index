# QQ头像下载配置文件

# 成员JSON文件路径 (由main.py生成的文件)
MEMBERS_JSON_FILE = "qq_group_937303337_members.json"

# 群组ID (如果为None，会自动从文件名推断)
GROUP_ID = None

# 头像尺寸选项:
# "40"  - 40x40 像素
# "100" - 100x100 像素  
# "140" - 140x140 像素
# "640" - 640x640 像素 (推荐，高清)
AVATAR_SIZE = "140"

# 请求间隔时间(秒) - 避免请求过快被限制
REQUEST_DELAY = 0.2

# 头像保存目录模板
AVATAR_DIR_TEMPLATE = "./avatars/{group_id}"

# 是否跳过已存在的文件
SKIP_EXISTING = True

# 下载超时时间(秒)
DOWNLOAD_TIMEOUT = 30

# User-Agent
USER_AGENT = 'Apifox/1.0.0 (https://apifox.com)'

# 支持的图片格式
SUPPORTED_FORMATS = ['.jpg', '.png', '.gif']

# 默认图片格式 (当无法确定时使用)
DEFAULT_FORMAT = '.jpg'
