import os
import logging
from logging.handlers import RotatingFileHandler
from config.config import config

class Logger:
    """日志管理类"""
    
    def __init__(self, name, config_name='default'):
        self.config = config[config_name]
        self.logger = logging.getLogger(name)
        self.setup_logger()
    
    def setup_logger(self):
        """配置日志记录器"""
        # 设置日志级别
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # 创建日志目录
        os.makedirs(self.config.LOG_DIR, exist_ok=True)
        
        # 创建文件处理器
        log_file = os.path.join(self.config.LOG_DIR, f'{self.logger.name}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.LOG_MAX_BYTES,
            backupCount=self.config.LOG_BACKUP_COUNT
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        
        # 设置日志格式
        formatter = logging.Formatter(self.config.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """获取日志记录器"""
        return self.logger

# 创建应用日志记录器
app_logger = Logger('ddos_detector').get_logger()
# 创建检测模型日志记录器
model_logger = Logger('detector_model').get_logger()
# 创建流量捕获日志记录器
capture_logger = Logger('traffic_capture').get_logger() 