#!/bin/bash

# 设置错误时退出
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印带颜色的信息
print_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    print_error "请使用root权限运行此脚本"
    exit 1
fi

# 更新系统
print_info "正在更新系统..."
apt-get update
apt-get upgrade -y

# 安装必要的软件包
print_info "正在安装必要的软件包..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git \
    build-essential \
    python3.8 \
    python3.8-dev \
    python3.8-venv \
    python3-pip \
    libpcap-dev

# 安装Docker
print_info "正在安装Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
print_info "正在安装Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 创建项目目录
print_info "正在创建项目目录..."
mkdir -p /opt/ddos_detector
cd /opt/ddos_detector

# 创建必要的子目录
mkdir -p logs data prometheus_data

# 设置目录权限
chmod -R 755 /opt/ddos_detector

# 创建环境变量文件
print_info "正在创建环境变量文件..."
cat > .env << EOL
# 应用配置
APP_ENV=production
APP_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
APP_PORT=5000
APP_HOST=0.0.0.0

# 数据库配置
MONGODB_URI=mongodb://mongodb:27017/
MONGODB_DB=ddos_detector
MONGODB_USER=admin
MONGODB_PASSWORD=$(openssl rand -hex 16)
REDIS_URI=redis://redis:6379/0
REDIS_PASSWORD=$(openssl rand -hex 16)

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=/app/logs
DATA_DIR=/app/data
MODEL_DIR=/app/models

# 监控配置
GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 16)

# 时区配置
TZ=Asia/Shanghai
EOL

# 设置环境变量文件权限
chmod 600 .env

# 启动服务
print_info "正在启动服务..."
docker-compose up -d

# 等待服务启动
print_info "等待服务启动..."
sleep 30

# 检查服务状态
print_info "检查服务状态..."
docker-compose ps

print_info "部署完成！"
print_info "请访问以下地址："
print_info "Web界面: http://localhost:5000"
print_info "Grafana: http://localhost:3000"
print_info "Prometheus: http://localhost:9090"
print_info "默认Grafana管理员密码: $(grep GRAFANA_ADMIN_PASSWORD .env | cut -d '=' -f2)" 