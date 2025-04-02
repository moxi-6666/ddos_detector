# DDoS检测系统

基于机器学习的DDoS攻击检测系统，支持实时流量监控、攻击检测和域名分析。

## 功能特点

- 实时流量监控
- DDoS攻击检测
- 恶意域名检测
- 系统资源监控
- 攻击地图可视化
- 实时告警通知

## 系统要求

- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- Ubuntu 20.04 LTS
- 网卡支持混杂模式

## 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/ddos_detector.git
cd ddos_detector
```

2. 安装系统依赖
```bash
sudo apt update
sudo apt install -y python3-pip python3-dev build-essential libpcap-dev
```

3. 安装数据库
```bash
sudo apt install -y mongodb redis-server
```

4. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

5. 安装Python依赖
```bash
pip install -r requirements.txt
```

6. 配置网卡混杂模式
```bash
sudo ifconfig ens33 promisc
```

## 配置说明

1. 数据库配置
```python
# config/config.py
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_DB = 'ddos_detector'
REDIS_URI = 'redis://localhost:6379/0'
```

2. 网络配置
```python
CAPTURE_INTERFACE = 'ens33'  # 网卡名称
CAPTURE_FILTER = 'ip'       # 抓包过滤器
```

3. 检测配置
```python
ALERT_THRESHOLD = 0.7       # 告警阈值
DETECTION_INTERVAL = 60     # 检测间隔（秒）
```

## 使用方法

1. 启动服务
```bash
sudo python app.py
```

2. 访问Web界面
```
http://localhost:5000
```

3. 查看日志
```bash
tail -f /var/log/ddos_detector/app.log
```

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

## 常见问题

1. 网卡不支持混杂模式
- 检查网卡驱动
- 更新网卡固件
- 使用其他网卡

2. 数据库连接失败
- 检查MongoDB服务状态
- 验证数据库连接字符串
- 检查防火墙设置

3. 内存使用过高
- 调整数据包缓冲区大小
- 优化检测间隔
- 清理历史数据

## 维护说明

1. 数据备份
```bash
# MongoDB备份
mongodump --uri="mongodb://localhost:27017/ddos_detector" --out=backup/

# Redis备份
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup/
```

2. 日志清理
```bash
# 清理30天前的日志
find /var/log/ddos_detector -type f -mtime +30 -delete
```

3. 性能优化
- 定期清理历史数据
- 优化数据库索引
- 调整缓存策略

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License 