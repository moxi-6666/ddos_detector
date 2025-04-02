#!/usr/bin/env python3
import os
import sys
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import psutil
import json
from services.capture_service import CaptureService
from models.ddos_detector import DDoSDetector
from utils.mongo_helper import MongoHelper
from config.config import config
from services.domain_detection_service import DomainDetectionService
from utils.logger import app_logger
from utils.redis_helper import RedisHelper
from services.alert_service import AlertService

# 确保在正确的目录中运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config['production'])  # 使用生产环境配置
socketio = SocketIO(app, cors_allowed_origins="*")

# 服务实例字典
services = {}

class ClientManager:
    def __init__(self):
        self.clients = set()
        self.lock = threading.Lock()
        self.last_heartbeat = {}
    
    def add_client(self, sid):
        with self.lock:
            self.clients.add(sid)
            self.last_heartbeat[sid] = time.time()
            app_logger.info(f"客户端连接: {sid}")
    
    def remove_client(self, sid):
        with self.lock:
            self.clients.discard(sid)
            if sid in self.last_heartbeat:
                del self.last_heartbeat[sid]
            app_logger.info(f"客户端断开: {sid}")
    
    def get_client_count(self):
        with self.lock:
            return len(self.clients)
    
    def update_heartbeat(self, sid):
        with self.lock:
            self.last_heartbeat[sid] = time.time()
    
    def check_heartbeats(self):
        with self.lock:
            current_time = time.time()
            for sid in list(self.clients):
                if current_time - self.last_heartbeat.get(sid, 0) > 60:  # 60秒超时
                    app_logger.warning(f"客户端 {sid} 心跳超时")
                    self.remove_client(sid)

client_manager = ClientManager()

def validate_dashboard_data(data):
    """验证仪表盘数据"""
    required_fields = ['system', 'traffic', 'detection', 'domain_detection']
    for field in required_fields:
        if field not in data:
            app_logger.error(f"缺少必要字段: {field}")
            return False
    return True

def init_services():
    """初始化所有服务"""
    try:
        # 1. 初始化数据库连接
        app_logger.info("正在初始化数据库连接...")
        services['mongo'] = MongoHelper()
        services['redis'] = RedisHelper(app.config)
        
        # 2. 初始化检测服务
        app_logger.info("正在初始化检测服务...")
        services['ddos_detector'] = DDoSDetector(app.config)
        services['domain_detection'] = DomainDetectionService(app.config)
        
        # 3. 初始化捕获服务
        app_logger.info("正在初始化捕获服务...")
        services['capture'] = CaptureService()
        
        # 4. 初始化告警服务
        app_logger.info("正在初始化告警服务...")
        services['alert'] = AlertService()
        
        app_logger.info("所有服务初始化完成")
        return True
    except Exception as e:
        app_logger.error(f"服务初始化失败: {str(e)}")
        return False

def cleanup():
    """清理资源"""
    try:
        # 停止捕获服务
        services['capture'].stop_capture()
        
        # 关闭数据库连接
        services['mongo'].close()
        
        app_logger.info("资源清理完成")
    except Exception as e:
        app_logger.error(f"资源清理失败: {str(e)}")

def get_system_status():
    """获取系统状态"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        network = psutil.net_io_counters()
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'network_traffic': network.bytes_sent / 1024 / 1024,  # MB/s
            'connection_count': client_manager.get_client_count(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        app_logger.error(f"获取系统状态失败: {str(e)}")
        return None

def get_traffic_stats():
    """获取流量统计"""
    try:
        network = psutil.net_io_counters()
        return {
            'inbound_traffic': network.bytes_recv / 1024 / 1024,  # MB/s
            'outbound_traffic': network.bytes_sent / 1024 / 1024,  # MB/s
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        app_logger.error(f"获取流量统计失败: {str(e)}")
        return None

def get_attack_map_data():
    """获取攻击地图数据"""
    try:
        return services['ddos_detector'].get_attack_map_data()
    except Exception as e:
        app_logger.error(f"获取攻击地图数据失败: {str(e)}")
        return []

def update_dashboard():
    """更新仪表盘数据"""
    retry_count = 0
    max_retries = 3
    last_update = time.time()
    update_interval = app.config['SYSTEM_MONITOR_INTERVAL']
    
    while True:
        current_time = time.time()
        if current_time - last_update >= update_interval:
            try:
                system_status = get_system_status()
                traffic_stats = get_traffic_stats()
                attack_data = get_attack_map_data()
                
                if not all([system_status, traffic_stats, attack_data]):
                    raise ValueError("数据获取不完整")
                
                data = {
                    'system': system_status,
                    'traffic': traffic_stats,
                    'detection': {
                        'attacks': attack_data,
                        'stats': {
                            'total_attacks': len(attack_data),
                            'active_attacks': len([a for a in attack_data if a['status'] == 'active'])
                        }
                    },
                    'domain_detection': {
                        'total': services['domain_detection'].stats['total'],
                        'normal': services['domain_detection'].stats['normal'],
                        'suspicious': services['domain_detection'].stats['suspicious'],
                        'malicious': services['domain_detection'].stats['malicious'],
                        'domains': services['domain_detection'].get_recent_detections()
                    }
                }
                
                if validate_dashboard_data(data):
                    socketio.emit('dashboard_update', data)
                    last_update = current_time
                    retry_count = 0
                else:
                    raise ValueError("数据验证失败")
            except Exception as e:
                app_logger.error(f"更新仪表盘失败: {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    app_logger.error("达到最大重试次数，停止更新")
                    break
                time.sleep(5)
        
        # 检查客户端心跳
        client_manager.check_heartbeats()
        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    client_manager.add_client(request.sid)
    app_logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    client_manager.remove_client(request.sid)
    app_logger.info('Client disconnected')

@socketio.on('ping')
def handle_ping():
    client_manager.update_heartbeat(request.sid)
    emit('pong')

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')

@app.route('/api/domain/detect', methods=['POST'])
def detect_domain():
    """检测域名API"""
    try:
        data = request.get_json()
        domain = data.get('domain')
        if not domain:
            return jsonify({'error': '域名不能为空'}), 400
            
        result = services['domain_detection'].detect_domain(domain)
        return jsonify(result)
    except Exception as e:
        app_logger.error(f"域名检测失败: {str(e)}")
        return jsonify({'error': '检测失败'}), 500

@app.route('/api/domain/blacklist', methods=['POST'])
def manage_blacklist():
    """管理域名黑名单API"""
    try:
        data = request.get_json()
        domain = data.get('domain')
        action = data.get('action')
        
        if not domain or not action:
            return jsonify({'error': '参数不完整'}), 400
            
        if action == 'add':
            success = services['domain_detection'].add_to_blacklist(domain)
        elif action == 'remove':
            success = services['domain_detection'].remove_from_blacklist(domain)
        else:
            return jsonify({'error': '无效的操作'}), 400
            
        return jsonify({'success': success})
    except Exception as e:
        app_logger.error(f"管理黑名单失败: {str(e)}")
        return jsonify({'error': '操作失败'}), 500

if __name__ == '__main__':
    # 检查是否以root权限运行
    if os.geteuid() != 0:
        print("错误：需要root权限运行此程序")
        sys.exit(1)
        
    # 创建必要的目录
    os.makedirs(app.config['LOG_DIR'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)
    
    try:
        if init_services():
            # 启动后台任务
            socketio.start_background_task(update_dashboard)
            
            # 启动应用
            app_logger.info("DDoS检测系统启动")
            socketio.run(
                app,
                host=app.config['HOST'],
                port=app.config['PORT'],
                debug=app.config['DEBUG']
            )
        else:
            app_logger.error("服务初始化失败，应用退出")
            sys.exit(1)
    except KeyboardInterrupt:
        app_logger.info("收到停止信号，正在关闭服务...")
    finally:
        cleanup() 