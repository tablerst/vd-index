#!/bin/bash

# 动态生成 nginx 配置文件
# 根据当前项目路径和域名生成正确的配置

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NGINX_CONF="$PROJECT_ROOT/nginx.conf"

# 默认配置 (主项目)
DEFAULT_DOMAIN="tomo-loop.icu"
DEFAULT_ROOT_PATH="$PROJECT_ROOT"

# === 硬编码：第二个项目配置 ===
SECOND_PROJECT_ROOT="/root/workspace/evening-gowm"
SECOND_DOMAIN_PREFIX="evening-gown" # 默认通过路径 /gown/ 暴露，同时可用于二级域名

# 获取参数
DOMAIN="${1:-$DEFAULT_DOMAIN}"
ROOT_PATH="${2:-$DEFAULT_ROOT_PATH}"

echo "生成 nginx 配置文件..."
echo "--------------------------------"
echo "主项目路径: $ROOT_PATH"
echo "主域名: $DOMAIN"
echo "--------------------------------"
echo "新项目路径: $SECOND_PROJECT_ROOT"
echo "新域名: $SECOND_DOMAIN_PREFIX.$DOMAIN"
echo "新项目挂载路径: /$SECOND_DOMAIN_PREFIX/"
echo "--------------------------------"
echo "配置文件: $NGINX_CONF"

# 创建日志目录
mkdir -p "$ROOT_PATH/logs"

# 生成配置文件
cat > "$NGINX_CONF" << EOF
# 独立的项目级别 nginx 配置文件
# 该文件由 generate-nginx-conf.sh 生成，包含双项目配置

# 设置运行用户为 root
user root;

# 设置工作进程数
worker_processes auto;

# 错误日志 (共用主项目的 logs 目录)
error_log $ROOT_PATH/logs/error.log;

# PID 文件
pid $ROOT_PATH/logs/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    # 基本设置
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    
    # 访问日志
    access_log $ROOT_PATH/logs/access.log main;
    
    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # =========================================================
    # 🟢 主项目 Server (后端+前端): $DOMAIN
    # =========================================================
    server {
        listen 80;
        listen [::]:80;
        server_name $DOMAIN www.$DOMAIN;

        # 网站根目录指向后端静态文件目录
        root $ROOT_PATH/src/backend/static;
        index index.html index.htm;
        
        # API 代理到后端服务
        location ^~ /api/ {
            proxy_pass http://localhost:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # 健康检查代理
        location /health {
            proxy_pass http://localhost:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # 头像文件代理
        location /avatars/ {
            proxy_pass http://localhost:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        # 新项目通过路径挂载，避免额外的 DNS 配置
        location ^~ /$SECOND_DOMAIN_PREFIX/ {
            rewrite ^/$SECOND_DOMAIN_PREFIX/(.*)$ /$1 break;
            root $SECOND_PROJECT_ROOT/dist;
            try_files \$uri \$uri/ /index.html;
            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        # 处理 Vue Router 的 history 模式
        location / {
            try_files \$uri \$uri/ /index.html;
        }
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
        
        # 安全设置
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
        
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        # ✅ 已补回原有的安全头
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    }

    # =========================================================
    # 🔵 新项目 Server (纯前端): $SECOND_DOMAIN_PREFIX.$DOMAIN
    # =========================================================
    server {
        listen 80;
        server_name $SECOND_DOMAIN_PREFIX.$DOMAIN;

        # 指向新项目的 dist 目录
        root $SECOND_PROJECT_ROOT/dist;
        index index.html;

        # SPA 路由支持 (解决刷新 404)
        location / {
            try_files \$uri \$uri/ /index.html;
        }

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # 简单的安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
    }
}
EOF

echo "✅ nginx 配置文件生成完成: $NGINX_CONF"
echo ""
echo "使用方法:"
echo "  测试配置: sudo nginx -t -c $NGINX_CONF"
echo "  重载配置: sudo nginx -s reload -c $NGINX_CONF"
echo "  (如果 Nginx 未启动) 启动服务: sudo nginx -c $NGINX_CONF"
echo ""#!/bin/bash