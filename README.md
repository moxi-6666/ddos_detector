# DDoS检测系统

基于机器学习的DDoS攻击检测系统，支持实时流量监控、攻击检测和域名分析。

## 功能特点

- 实时流量监控
  - 网络流量捕获和分析
  - 流量统计和可视化
  - 实时告警通知
- DDoS攻击检测
  - 基于CNN-LSTM的深度学习模型
  - 基于SKM-HFS的检测模型
  - 实时攻击检测和分类
- 恶意域名检测
  - 黑名单管理
  - 规则检测
  - 特征分析
- 系统资源监控
  - CPU使用率
  - 内存使用
  - 磁盘空间
  - 网络带宽
- 攻击地图可视化
  - 全球攻击分布
  - 攻击类型统计
  - 实时更新
- 实时告警通知
  - 攻击告警
  - 系统告警
  - 域名告警

## 系统要求

### 硬件要求
- CPU: 至少双核处理器，推荐4核及以上
- 内存: 最少4GB RAM，推荐8GB及以上
- 硬盘空间: 最少20GB可用空间
- 网卡: 支持混杂模式的网卡

### 软件要求
- 操作系统: Ubuntu 20.04 LTS（推荐）
- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+

## 安装步骤

### 1. 系统环境准备

#### 1.1 更新系统
```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装基础工具
sudo apt install -y build-essential git curl wget
```

#### 1.2 安装Python环境
```bash
# 安装Python和pip
sudo apt install -y python3 python3-pip python3-dev

# 安装虚拟环境工具
sudo apt install -y python3-venv

# 创建虚拟环境
python3 -m venv /opt/ddos_detector/venv

# 激活虚拟环境
source /opt/ddos_detector/venv/bin/activate
```

### 2. 安装数据库

#### 2.1 安装MongoDB
```bash
# 导入MongoDB公钥
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

# 添加MongoDB源
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

# 更新包列表
sudo apt update

# 安装MongoDB
sudo apt install -y mongodb-org

# 启动MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 检查MongoDB状态
sudo systemctl status mongod
```

#### 2.2 安装Redis
```bash
# 安装Redis
sudo apt install -y redis-server

# 启动Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 检查Redis状态
sudo systemctl status redis-server
```

### 3. 安装系统依赖

#### 3.1 安装网络工具
```bash
# 安装网络相关工具
sudo apt install -y libpcap-dev tcpdump net-tools
```

#### 3.2 安装编译工具
```bash
# 安装编译工具
sudo apt install -y build-essential gcc g++ make
```

### 4. 部署项目

#### 4.1 创建项目目录
```bash
# 创建项目目录
sudo mkdir -p /opt/ddos_detector
sudo chown -R $USER:$USER /opt/ddos_detector

# 创建必要的子目录
sudo mkdir -p /var/log/ddos_detector
sudo mkdir -p /var/lib/ddos_detector
sudo mkdir -p /opt/ddos_detector/models
sudo mkdir -p /opt/ddos_detector/data
```

#### 4.2 克隆项目代码
```bash
# 进入项目目录
cd /opt/ddos_detector

# 克隆项目代码
git clone https://github.com/moxi-6666/ddos_detector.git .
```

#### 4.3 安装Python依赖
```bash
# 确保在虚拟环境中
source /opt/ddos_detector/venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 5. 配置项目

#### 5.1 配置数据库连接
```bash
# 编辑配置文件
nano /opt/ddos_detector/app/config/config.py

# 修改数据库配置
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_DB = 'ddos_detector'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
```

#### 5.2 配置系统权限
```bash
# 设置目录权限
sudo chown -R $USER:$USER /var/log/ddos_detector
sudo chown -R $USER:$USER /var/lib/ddos_detector
sudo chown -R $USER:$USER /opt/ddos_detector

# 设置执行权限
sudo chmod +x /opt/ddos_detector/app/app.py
```

### 6. 启动服务

#### 6.1 启动数据库服务
```bash
# 启动MongoDB
sudo systemctl start mongod

# 启动Redis
sudo systemctl start redis-server
```

#### 6.2 启动应用
```bash
# 进入项目目录
cd /opt/ddos_detector

# 激活虚拟环境
source venv/bin/activate

# 启动应用
sudo python3 app/app.py
```

### 7. 验证部署

#### 7.1 检查服务状态
```bash
# 检查MongoDB
sudo systemctl status mongod

# 检查Redis
sudo systemctl status redis-server
```

#### 7.2 访问Web界面
- 打开浏览器访问：`http://服务器IP:5000`
- 检查日志：`tail -f /var/log/ddos_detector/app.log`

## API文档

### 域名检测
```
POST /api/domain/detect
Content-Type: application/json

{
    "domain": "example.com"
}
```

### 黑名单管理
```
POST /api/domain/blacklist
Content-Type: application/json

{
    "domain": "example.com",
    "action": "add"  # 或 "remove"
}
```

## 维护指南

### 数据库备份
```bash
# MongoDB备份
mongodump --db ddos_detector --out /backup/mongodb

# Redis备份
redis-cli save
```

### 日志管理
```bash
# 查看应用日志
tail -f /var/log/ddos_detector/app.log

# 查看模型日志
tail -f /var/log/ddos_detector/model.log

# 查看捕获日志
tail -f /var/log/ddos_detector/capture.log
```

### 系统监控
```bash
# 监控系统资源
top
htop

# 监控网络流量
iftop
nethogs
```

## 常见问题

### 权限问题
```bash
# 修复权限
sudo chown -R $USER:$USER /opt/ddos_detector
sudo chown -R $USER:$USER /var/log/ddos_detector
sudo chown -R $USER:$USER /var/lib/ddos_detector
```

### 数据库连接问题
```bash
# 检查MongoDB连接
mongo --eval "db.version()"

# 检查Redis连接
redis-cli ping
```

### 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 安全建议

1. 定期更新系统和依赖包
2. 配置防火墙规则
3. 使用强密码
4. 定期备份数据
5. 监控系统资源使用情况

## 联系方式

如有问题，请联系系统管理员：
- 邮箱：2790739170@qq.com
- 电话：15724405133
- 工作时间：周一至周五 9:00-18:00

## 许可证

本项目采用MIT许可证，详见LICENSE文件。 