from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ..config.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MongoHelper:
    def __init__(self):
        self.config = config['default']
        self.client = None
        self.db = None
        self._connect()
        
    def _connect(self):
        """建立数据库连接"""
        try:
            self.client = MongoClient(
                self.config.MONGO_URI,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=2000
            )
            # 验证连接
            self.client.server_info()
            self.db = self.client[self.config.MONGO_DB]
            logger.info("MongoDB连接成功")
        except ConnectionFailure as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            raise
            
    def _ensure_connection(self):
        """确保数据库连接有效"""
        try:
            self.client.server_info()
        except ConnectionFailure:
            logger.warning("MongoDB连接已断开，尝试重新连接")
            self._connect()
            
    def save_capture_record(self, record):
        """保存捕获记录"""
        try:
            self._ensure_connection()
            return self.db.captures.insert_one(record)
        except Exception as e:
            logger.error(f"保存捕获记录失败: {str(e)}")
            return None
        
    def save_detection_result(self, result):
        """保存检测结果"""
        try:
            self._ensure_connection()
            return self.db.detections.insert_one(result)
        except Exception as e:
            logger.error(f"保存检测结果失败: {str(e)}")
            return None
        
    def get_recent_captures(self, limit=100):
        """获取最近的捕获记录"""
        try:
            self._ensure_connection()
            return list(self.db.captures.find().sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"获取捕获记录失败: {str(e)}")
            return []
        
    def get_recent_detections(self, limit=100):
        """获取最近的检测结果"""
        try:
            self._ensure_connection()
            return list(self.db.detections.find().sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"获取检测结果失败: {str(e)}")
            return []
        
    def get_attack_statistics(self, start_time=None, end_time=None):
        """获取攻击统计信息"""
        try:
            self._ensure_connection()
            query = {}
            if start_time:
                query['timestamp'] = {'$gte': start_time}
            if end_time:
                query['timestamp'] = {'$lte': end_time}
                
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': '$attack_type',
                    'count': {'$sum': 1},
                    'avg_confidence': {'$avg': '$confidence'}
                }}
            ]
            
            return list(self.db.detections.aggregate(pipeline))
        except Exception as e:
            logger.error(f"获取攻击统计信息失败: {str(e)}")
            return []
            
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭") 