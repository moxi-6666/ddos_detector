from pymongo import MongoClient
from ..config.config import config

class MongoHelper:
    def __init__(self):
        self.config = config['default']
        self.client = MongoClient(self.config.MONGO_URI)
        self.db = self.client.ddos_detection
        
    def save_capture_record(self, record):
        """保存捕获记录"""
        return self.db.captures.insert_one(record)
        
    def save_detection_result(self, result):
        """保存检测结果"""
        return self.db.detections.insert_one(result)
        
    def get_recent_captures(self, limit=100):
        """获取最近的捕获记录"""
        return list(self.db.captures.find().sort('timestamp', -1).limit(limit))
        
    def get_recent_detections(self, limit=100):
        """获取最近的检测结果"""
        return list(self.db.detections.find().sort('timestamp', -1).limit(limit))
        
    def get_attack_statistics(self, start_time=None, end_time=None):
        """获取攻击统计信息"""
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