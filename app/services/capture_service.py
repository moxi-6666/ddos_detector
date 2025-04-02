import scapy.all as scapy
import threading
import time
from datetime import datetime
from collections import deque
from app.utils.logger import get_logger
from app.utils.mongo_helper import MongoHelper
from app.config.config import config
import backoff
from typing import Optional, Dict, Any
import queue

logger = get_logger(__name__)

class CaptureService:
    """网络流量捕获服务"""
    
    DEFAULT_CONFIG = {
        'CAPTURE_INTERFACE': 'eth0',
        'CAPTURE_FILTER': 'ip',
        'PACKET_BUFFER_SIZE': 1000,
        'MAX_ERRORS': 100,
        'ERROR_THRESHOLD': 10,
        'RETRY_DELAY': 5,
        'MONGODB_ENABLED': True
    }
    
    def __init__(self):
        """初始化捕获服务"""
        try:
            # 加载配置，使用默认值作为后备
            self.config = self._load_config()
            
            # 初始化基本属性
            self.interface = self.config['CAPTURE_INTERFACE']
            self.filter = self.config['CAPTURE_FILTER']
            self.packet_buffer = deque(maxlen=self.config['PACKET_BUFFER_SIZE'])
            
            # 线程安全计数器
            self._error_count = 0
            self._lock = threading.Lock()
            
            # 延迟初始化MongoDB
            self.mongo: Optional[MongoHelper] = None
            self._mongo_initialized = False
            
            # 状态标志
            self.is_running = False
            self.capture_thread: Optional[threading.Thread] = None
            
            # 错误处理参数
            self.max_errors = self.config['MAX_ERRORS']
            self.error_threshold = self.config['ERROR_THRESHOLD']
            self.retry_delay = self.config['RETRY_DELAY']
            
            # 数据包处理队列
            self.packet_queue = queue.Queue(maxsize=1000)
            
            logger.info("捕获服务初始化完成")
            
        except Exception as e:
            logger.error(f"捕获服务初始化失败: {str(e)}")
            raise
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置，使用默认值作为后备"""
        try:
            user_config = config.get('default', {})
            merged_config = self.DEFAULT_CONFIG.copy()
            merged_config.update(user_config)
            return merged_config
        except Exception as e:
            logger.error(f"加载配置失败，使用默认配置: {str(e)}")
            return self.DEFAULT_CONFIG
            
    def _init_mongo(self):
        """延迟初始化MongoDB连接"""
        if not self._mongo_initialized and self.config['MONGODB_ENABLED']:
            try:
                self.mongo = MongoHelper()
                self._mongo_initialized = True
                logger.info("MongoDB连接初始化成功")
            except Exception as e:
                logger.error(f"MongoDB连接初始化失败: {str(e)}")
                self.mongo = None
                
    def _increment_error_count(self) -> int:
        """线程安全地增加错误计数"""
        with self._lock:
            self._error_count += 1
            return self._error_count
            
    def _reset_error_count(self):
        """线程安全地重置错误计数"""
        with self._lock:
            self._error_count = 0
            
    def start_capture(self):
        """启动流量捕获"""
        if self.is_running:
            logger.warning("流量捕获服务已经在运行")
            return
            
        try:
            # 设置网卡混杂模式
            scapy.conf.iface = self.interface
            scapy.conf.L3socket = scapy.L3RawSocket
            
            # 初始化MongoDB连接
            self._init_mongo()
            
            # 启动捕获线程
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_packets)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            # 启动处理线程
            self.process_thread = threading.Thread(target=self._process_packets)
            self.process_thread.daemon = True
            self.process_thread.start()
            
            logger.info(f"流量捕获服务已启动，监听接口: {self.interface}")
            
        except Exception as e:
            logger.error(f"启动流量捕获服务失败: {str(e)}")
            self.stop_capture()
            raise
            
    def stop_capture(self):
        """停止流量捕获"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=5)
        logger.info("流量捕获服务已停止")
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _capture_packets(self):
        """捕获数据包"""
        while self.is_running:
            try:
                # 开始捕获数据包
                scapy.sniff(
                    iface=self.interface,
                    filter=self.filter,
                    prn=self._queue_packet,
                    store=0
                )
            except Exception as e:
                logger.error(f"数据包捕获失败: {str(e)}")
                error_count = self._increment_error_count()
                
                # 检查错误次数是否超过阈值
                if error_count >= self.error_threshold:
                    logger.error("错误次数过多，停止捕获服务")
                    self.stop_capture()
                    break
                    
                # 等待一段时间后重试
                time.sleep(self.retry_delay)
                
    def _queue_packet(self, packet):
        """将数据包加入处理队列"""
        try:
            self.packet_queue.put(packet, timeout=1)
        except queue.Full:
            logger.warning("数据包处理队列已满，丢弃数据包")
            
    def _process_packets(self):
        """处理数据包队列"""
        while self.is_running:
            try:
                packet = self.packet_queue.get(timeout=1)
                self._process_packet(packet)
                self.packet_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"处理数据包失败: {str(e)}")
                self._increment_error_count()
                
    def _process_packet(self, packet):
        """处理单个数据包"""
        try:
            # 提取数据包信息
            packet_info = {
                'timestamp': datetime.now(),
                'length': len(packet),
                'protocol': packet.name,
                'src_ip': packet[scapy.IP].src if scapy.IP in packet else None,
                'dst_ip': packet[scapy.IP].dst if scapy.IP in packet else None,
                'src_port': packet[scapy.TCP].sport if scapy.TCP in packet else None,
                'dst_port': packet[scapy.TCP].dport if scapy.TCP in packet else None,
                'flags': self._get_tcp_flags(packet) if scapy.TCP in packet else None
            }
            
            # 添加到缓冲区
            self.packet_buffer.append(packet_info)
            
            # 尝试保存到MongoDB
            if self.mongo:
                try:
                    self.mongo.save_capture_record(packet_info)
                except Exception as e:
                    logger.error(f"保存数据包到MongoDB失败: {str(e)}")
                    
            # 重置错误计数
            self._reset_error_count()
            
        except Exception as e:
            logger.error(f"处理数据包失败: {str(e)}")
            self._increment_error_count()
            
    def _get_tcp_flags(self, packet):
        """获取TCP标志"""
        if not scapy.TCP in packet:
            return None
            
        tcp = packet[scapy.TCP]
        return {
            'SYN': bool(tcp.flags & 0x02),
            'ACK': bool(tcp.flags & 0x10),
            'FIN': bool(tcp.flags & 0x01),
            'RST': bool(tcp.flags & 0x04),
            'PSH': bool(tcp.flags & 0x08),
            'URG': bool(tcp.flags & 0x20)
        }
        
    def get_packet_buffer(self):
        """获取数据包缓冲区"""
        return list(self.packet_buffer)
        
    def clear_buffer(self):
        """清空数据包缓冲区"""
        self.packet_buffer.clear() 