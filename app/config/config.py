import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 基础路径配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    LOG_DIR = os.getenv('LOG_DIR', '/var/log/ddos_detector')
    DATA_DIR = os.getenv('DATA_DIR', '/var/lib/ddos_detector')
    MODEL_DIR = os.getenv('MODEL_DIR', '/opt/ddos_detector/models')

    # 数据库配置
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGO_DB = os.getenv('MONGODB_DB', 'ddos_detector')
    MONGO_USER = os.getenv('MONGODB_USER')
    MONGO_PASSWORD = os.getenv('MONGODB_PASSWORD')
    REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    # 网络配置
    CAPTURE_INTERFACE = os.getenv('CAPTURE_INTERFACE', 'eth0')
    CAPTURE_FILTER = os.getenv('CAPTURE_FILTER', 'ip')
    PORT = int(os.getenv('APP_PORT', 5000))
    HOST = os.getenv('APP_HOST', '0.0.0.0')

    # 检测配置
    ALERT_THRESHOLD = float(os.getenv('ALERT_THRESHOLD', 0.7))
    DETECTION_INTERVAL = int(os.getenv('DETECTION_INTERVAL', 60))
    PACKET_BUFFER_SIZE = int(os.getenv('PACKET_BUFFER_SIZE', 10000))

    # 模型配置
    MODEL_UPDATE_INTERVAL = int(os.getenv('MODEL_UPDATE_INTERVAL', 3600))
    FEATURE_WINDOW_SIZE = int(os.getenv('FEATURE_WINDOW_SIZE', 100))
    
    # 系统监控配置
    SYSTEM_MONITOR_INTERVAL = int(os.getenv('SYSTEM_MONITOR_INTERVAL', 5))
    CPU_ALERT_THRESHOLD = int(os.getenv('CPU_ALERT_THRESHOLD', 80))
    MEMORY_ALERT_THRESHOLD = int(os.getenv('MEMORY_ALERT_THRESHOLD', 80))
    DISK_ALERT_THRESHOLD = int(os.getenv('DISK_ALERT_THRESHOLD', 80))

    # 日志配置
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 30))
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB

    # 告警配置
    ALERT_METHODS = os.getenv('ALERT_METHODS', 'email').split(',')
    SMTP_SERVER = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    ALERT_EMAIL = os.getenv('ALERT_EMAIL')

    # 安全配置
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    @classmethod
    def validate(cls):
        """验证配置"""
        required_vars = [
            'MONGO_URI',
            'MONGO_DB',
            'REDIS_URI',
            'SECRET_KEY',
            'JWT_SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # 生产环境使用更严格的安全设置
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