#!/bin/bash

# 更新系统
echo "正在更新系统..."
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
echo "正在安装系统依赖..."
sudo apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev git

# 安装MongoDB
echo "正在安装MongoDB..."
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb

# 安装Redis
echo "正在安装Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 克隆项目
echo "正在克隆项目..."
git clone https://github.com/moxi-6666/ddos_detector.git
cd ddos_detector

# 创建虚拟环境
echo "正在创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
echo "正在安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "正在创建必要的目录..."
mkdir -p logs data models

# 设置环境变量
echo "正在设置环境变量..."
cp .env.example .env
# 编辑.env文件，设置必要的配置项
sed -i 's/MONGODB_URI=mongodb:\/\/localhost:27017\/ddos_detector/MONGODB_URI=mongodb:\/\/localhost:27017\/ddos_detector/' .env
sed -i 's/REDIS_URI=redis:\/\/localhost:6379\/0/REDIS_URI=redis:\/\/localhost:6379\/0/' .env

# 初始化数据库
echo "正在初始化数据库..."
python scripts/init_db.py

# 设置日志
echo "正在设置日志..."
python scripts/setup_logging.py

# 设置模型
echo "正在设置模型..."
python scripts/setup_models.py

# 设置权限
echo "正在设置权限..."
chmod +x scripts/*.sh

echo "部署完成！"
echo "请运行以下命令启动服务："
echo "1. 启动Web服务：python app.py"
echo "2. 启动检测服务：python scripts/start_detector.py" 