import os
from datetime import timedelta

class Config:
    """基础配置类"""
    # 基础路径配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LOG_DIR = '/var/log/ddos_detector'
    DATA_DIR = '/var/lib/ddos_detector'
    MODEL_DIR = '/opt/ddos_detector/models'

    # 数据库配置
    MONGO_URI = 'mongodb://localhost:27017/'  # 统一使用MONGO_URI
    MONGO_DB = 'ddos_detector'
    REDIS_URI = 'redis://localhost:6379/0'

    # 网络配置
    CAPTURE_INTERFACE = 'eth0'
    CAPTURE_FILTER = 'ip'
    PORT = 5000
    HOST = '0.0.0.0'

    # 检测配置
    ALERT_THRESHOLD = 0.7
    DETECTION_INTERVAL = 60
    PACKET_BUFFER_SIZE = 10000

    # 模型配置
    MODEL_UPDATE_INTERVAL = 3600
    FEATURE_WINDOW_SIZE = 100
    
    # 系统监控配置
    SYSTEM_MONITOR_INTERVAL = 5
    CPU_ALERT_THRESHOLD = 80
    MEMORY_ALERT_THRESHOLD = 80
    DISK_ALERT_THRESHOLD = 80

    # 日志配置
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_BACKUP_COUNT = 30
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB

    # 告警配置
    ALERT_METHODS = ['email']
    SMTP_SERVER = 'smtp.example.com'
    SMTP_PORT = 587
    SMTP_USER = 'alert@example.com'
    SMTP_PASSWORD = 'your-password'
    ALERT_EMAIL = 'admin@example.com'

    # OSS配置
    OSS_ACCESS_KEY_ID = 'your-access-key'
    OSS_ACCESS_KEY_SECRET = 'your-secret-key'
    OSS_ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    OSS_BUCKET_NAME = 'your-bucket-name'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # 生产环境使用更严格的安全设置
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
    
    # 生产环境的日志配置
    LOG_DIR = '/var/log/ddos_detector'
    
    # 生产环境的系统监控配置
    SYSTEM_MONITOR_INTERVAL = 10
    CPU_ALERT_THRESHOLD = 70
    MEMORY_ALERT_THRESHOLD = 70

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    MONGO_DB = 'ddos_detector_test'
    LOG_LEVEL = 'DEBUG'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 