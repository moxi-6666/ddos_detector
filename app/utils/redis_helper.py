import redis
import json
from datetime import datetime, timedelta
from app.utils.logger import get_logger
from app.config.config import config

logger = get_logger(__name__)

class RedisHelper:
    """Redis工具类"""
    
    def __init__(self, config):
        self.config = config
        self.redis = redis.from_url(config['REDIS_URI'])
        
    def cache_data(self, key, data, expire_time=3600):
        """缓存数据"""
        try:
            # 将数据转换为JSON字符串
            if isinstance(data, (dict, list)):
                data = json.dumps(data)
                
            # 存储数据
            self.redis.set(key, data, ex=expire_time)
            return True
        except Exception as e:
            logger.error(f"缓存数据失败: {str(e)}")
            return False
            
    def get_cached_data(self, key):
        """获取缓存数据"""
        try:
            data = self.redis.get(key)
            if data:
                # 尝试解析JSON
                try:
                    return json.loads(data)
                except:
                    return data.decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"获取缓存数据失败: {str(e)}")
            return None
            
    def delete_cached_data(self, key):
        """删除缓存数据"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存数据失败: {str(e)}")
            return False
            
    def cache_traffic_stats(self, stats):
        """缓存流量统计"""
        return self.cache_data('traffic_stats', stats, 300)  # 5分钟过期
        
    def get_traffic_stats(self):
        """获取流量统计"""
        return self.get_cached_data('traffic_stats')
        
    def cache_system_status(self, status):
        """缓存系统状态"""
        return self.cache_data('system_status', status, 60)  # 1分钟过期
        
    def get_system_status(self):
        """获取系统状态"""
        return self.get_cached_data('system_status')
        
    def cache_attack_map(self, data):
        """缓存攻击地图数据"""
        return self.cache_data('attack_map', data, 300)  # 5分钟过期
        
    def get_attack_map(self):
        """获取攻击地图数据"""
        return self.get_cached_data('attack_map')
        
    def cache_domain_detection(self, data):
        """缓存域名检测数据"""
        return self.cache_data('domain_detection', data, 300)  # 5分钟过期
        
    def get_domain_detection(self):
        """获取域名检测数据"""
        return self.get_cached_data('domain_detection')
        
    def cache_model_data(self, model_name, data):
        """缓存模型数据"""
        key = f'model_data:{model_name}'
        return self.cache_data(key, data, 3600)  # 1小时过期
        
    def get_model_data(self, model_name):
        """获取模型数据"""
        key = f'model_data:{model_name}'
        return self.get_cached_data(key)
        
    def clear_all_cache(self):
        """清空所有缓存"""
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False 