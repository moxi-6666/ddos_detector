import scapy.all as scapy
import threading
import time
from datetime import datetime
from collections import deque
from app.utils.logger import get_logger
from app.utils.mongo_helper import MongoHelper
from app.config.config import config

logger = get_logger(__name__)

class CaptureService:
    """网络流量捕获服务"""
    
    def __init__(self):
        self.config = config['default']
        self.interface = self.config['CAPTURE_INTERFACE']
        self.filter = self.config['CAPTURE_FILTER']
        self.packet_buffer = deque(maxlen=self.config['PACKET_BUFFER_SIZE'])
        self.mongo = MongoHelper()
        self.is_running = False
        self.capture_thread = None
        
    def start_capture(self):
        """启动流量捕获"""
        if self.is_running:
            logger.warning("流量捕获服务已经在运行")
            return
            
        try:
            # 设置网卡混杂模式
            scapy.conf.iface = self.interface
            scapy.conf.L3socket = scapy.L3RawSocket
            
            # 启动捕获线程
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_packets)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            logger.info(f"流量捕获服务已启动，监听接口: {self.interface}")
            
        except Exception as e:
            logger.error(f"启动流量捕获服务失败: {str(e)}")
            self.stop_capture()
            raise
            
    def stop_capture(self):
        """停止流量捕获"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join()
        logger.info("流量捕获服务已停止")
        
    def _capture_packets(self):
        """捕获数据包"""
        try:
            # 开始捕获数据包
            scapy.sniff(
                iface=self.interface,
                filter=self.filter,
                prn=self._process_packet,
                store=0
            )
        except Exception as e:
            logger.error(f"数据包捕获失败: {str(e)}")
            self.stop_capture()
            
    def _process_packet(self, packet):
        """处理捕获的数据包"""
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
            
            # 保存到MongoDB
            self.mongo.save_capture_record(packet_info)
            
        except Exception as e:
            logger.error(f"处理数据包失败: {str(e)}")
            
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