import re
import time
import json
import tldextract
from datetime import datetime
from collections import defaultdict
from app.utils.logger import get_logger
from app.utils.redis_helper import RedisHelper
from app.utils.mongo_helper import MongoHelper

logger = get_logger(__name__)

class DomainDetectionService:
    def __init__(self, config):
        self.config = config
        self.redis = RedisHelper(config)
        self.mongo = MongoHelper(config)
        
        # 加载黑名单
        self.blacklist = self._load_blacklist()
        # 加载规则
        self.rules = self._load_detection_rules()
        # 初始化统计数据
        self.stats = {
            'total': 0,
            'normal': 0,
            'suspicious': 0,
            'malicious': 0
        }
        # 域名检测缓存
        self.domain_cache = {}
        
    def _load_blacklist(self):
        """加载域名黑名单"""
        try:
            blacklist = set()
            # 从MongoDB加载黑名单
            blacklist_data = self.mongo.db.domain_blacklist.find()
            for item in blacklist_data:
                blacklist.add(item['domain'])
            return blacklist
        except Exception as e:
            logger.error(f"加载域名黑名单失败: {str(e)}")
            return set()
    
    def _load_detection_rules(self):
        """加载检测规则"""
        try:
            # 从MongoDB加载规则
            rules_data = self.mongo.db.detection_rules.find()
            rules = []
            for rule in rules_data:
                rules.append({
                    'pattern': re.compile(rule['pattern']),
                    'type': rule['type'],
                    'level': rule['level']
                })
            return rules
        except Exception as e:
            logger.error(f"加载检测规则失败: {str(e)}")
            return []
    
    def detect_domain(self, domain):
        """检测单个域名"""
        # 检查缓存
        if domain in self.domain_cache:
            if time.time() - self.domain_cache[domain]['timestamp'] < 3600:  # 1小时缓存
                return self.domain_cache[domain]
        
        result = {
            'name': domain,
            'timestamp': time.time(),
            'status': '正常',
            'threat_level': '低',
            'method': '规则检测'
        }
        
        # 1. 黑名单检测
        if domain in self.blacklist:
            result.update({
                'status': '恶意',
                'threat_level': '高',
                'method': '黑名单'
            })
            self._update_stats('malicious')
            self._save_detection_result(result)
            return result
        
        # 2. 规则检测
        for rule in self.rules:
            if rule['pattern'].search(domain):
                result.update({
                    'status': '可疑' if rule['level'] == '中' else '恶意',
                    'threat_level': rule['level'],
                    'method': '规则检测'
                })
                self._update_stats('suspicious' if rule['level'] == '中' else 'malicious')
                self._save_detection_result(result)
                return result
        
        # 3. 特征检测
        features = self._extract_features(domain)
        if self._analyze_features(features):
            result.update({
                'status': '可疑',
                'threat_level': '中',
                'method': '特征分析'
            })
            self._update_stats('suspicious')
        else:
            self._update_stats('normal')
        
        # 保存检测结果
        self._save_detection_result(result)
        # 更新缓存
        self.domain_cache[domain] = result
        
        return result
    
    def _extract_features(self, domain):
        """提取域名特征"""
        ext = tldextract.extract(domain)
        domain_name = ext.domain
        
        return {
            'length': len(domain),
            'subdomain_count': len(ext.subdomain.split('.')),
            'digit_ratio': sum(c.isdigit() for c in domain_name) / len(domain_name) if domain_name else 0,
            'special_char_count': sum(not c.isalnum() for c in domain_name),
            'entropy': self._calculate_entropy(domain_name)
        }
    
    def _calculate_entropy(self, text):
        """计算字符熵值"""
        if not text:
            return 0
        
        freq = defaultdict(int)
        for c in text:
            freq[c] += 1
        
        entropy = 0
        for count in freq.values():
            p = count / len(text)
            entropy -= p * (p ** 0.5)  # 使用香农熵公式
        
        return entropy
    
    def _analyze_features(self, features):
        """分析域名特征"""
        # 可疑特征阈值
        suspicious_thresholds = {
            'length': 20,  # 域名长度阈值
            'subdomain_count': 3,  # 子域名数量阈值
            'digit_ratio': 0.4,  # 数字比例阈值
            'special_char_count': 2,  # 特殊字符数量阈值
            'entropy': 3.5  # 熵值阈值
        }
        
        # 计算可疑特征数量
        suspicious_count = sum(
            1 for feature, threshold in suspicious_thresholds.items()
            if features[feature] > threshold
        )
        
        # 如果超过2个特征超过阈值，则认为可疑
        return suspicious_count >= 2
    
    def _update_stats(self, category):
        """更新统计数据"""
        self.stats['total'] += 1
        self.stats[category] += 1
    
    def _save_detection_result(self, result):
        """保存检测结果到MongoDB"""
        try:
            self.mongo.db.domain_detection.insert_one({
                **result,
                'timestamp': datetime.fromtimestamp(result['timestamp'])
            })
        except Exception as e:
            logger.error(f"保存域名检测结果失败: {str(e)}")
    
    def get_detection_stats(self):
        """获取检测统计数据"""
        return self.stats
    
    def get_recent_detections(self, limit=10):
        """获取最近的检测结果"""
        try:
            detections = list(self.mongo.db.domain_detection
                            .find()
                            .sort('timestamp', -1)
                            .limit(limit))
            
            # 转换时间戳
            for detection in detections:
                detection['timestamp'] = detection['timestamp'].timestamp()
                detection['_id'] = str(detection['_id'])
            
            return detections
        except Exception as e:
            logger.error(f"获取最近检测结果失败: {str(e)}")
            return []
    
    def add_to_blacklist(self, domain):
        """添加域名到黑名单"""
        try:
            if domain not in self.blacklist:
                self.mongo.db.domain_blacklist.insert_one({
                    'domain': domain,
                    'added_at': datetime.now()
                })
                self.blacklist.add(domain)
                return True
        except Exception as e:
            logger.error(f"添加域名到黑名单失败: {str(e)}")
        return False
    
    def remove_from_blacklist(self, domain):
        """从黑名单中移除域名"""
        try:
            if domain in self.blacklist:
                self.mongo.db.domain_blacklist.delete_one({'domain': domain})
                self.blacklist.remove(domain)
                return True
        except Exception as e:
            logger.error(f"从黑名单移除域名失败: {str(e)}")
        return False 