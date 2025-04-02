#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import psutil
from datetime import datetime
import threading
import time
from services.capture_service import CaptureService
from models.ddos_detector import DDoSDetector
from utils.mongo_helper import MongoHelper
from config.config import config
from services.domain_detection_service import DomainDetectionService
from utils.logger import app_logger

# 确保在正确的目录中运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(config['production'])  # 使用生产环境配置
socketio = SocketIO(app)

try:
    # 初始化服务
    capture_service = CaptureService()
    ddos_detector = DDoSDetector()
    mongo_helper = MongoHelper()
    domain_detection_service = DomainDetectionService(app.config)
except Exception as e:
    app_logger.error(f"服务初始化失败: {str(e)}")
    sys.exit(1)

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')

def get_system_status():
    """获取系统状态"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        app_logger.error(f"获取系统状态失败: {str(e)}")
        return None

def get_traffic_stats():
    """获取流量统计"""
    try:
        recent_detections = mongo_helper.get_recent_detections(limit=100)
        
        stats = {
            'total': 0,
            'normal': 0,
            'attack': 0,
            'malware': 0
        }
        
        for detection in recent_detections:
            if detection['is_attack']:
                stats['attack'] += detection['features']['byte_rate']
            else:
                stats['normal'] += detection['features']['byte_rate']
                
        stats['total'] = stats['normal'] + stats['attack'] + stats['malware']
        return stats
    except Exception as e:
        app_logger.error(f"获取流量统计失败: {str(e)}")
        return None

def get_attack_map_data():
    """获取攻击地图数据"""
    try:
        recent_attacks = mongo_helper.get_recent_detections(
            limit=1000,
            query={'is_attack': True}
        )
        
        attack_counts = {}
        for attack in recent_attacks:
            country = attack.get('source_country', 'Unknown')
            attack_counts[country] = attack_counts.get(country, 0) + 1
            
        return [{'country': k, 'count': v} for k, v in attack_counts.items()]
    except Exception as e:
        app_logger.error(f"获取攻击地图数据失败: {str(e)}")
        return []

def update_dashboard():
    """后台任务：更新仪表盘数据"""
    while True:
        try:
            # 获取系统状态
            system_status = get_system_status()
            
            # 获取流量数据
            traffic_data = get_traffic_stats()
            
            # 获取攻击检测数据
            detection_data = {
                'attacks': get_attack_map_data(),
                'stats': traffic_data
            }
            
            # 获取域名检测数据
            domain_data = {
                'total': domain_detection_service.stats['total'],
                'normal': domain_detection_service.stats['normal'],
                'suspicious': domain_detection_service.stats['suspicious'],
                'malicious': domain_detection_service.stats['malicious'],
                'domains': domain_detection_service.get_recent_detections()
            }
            
            # 发送更新
            socketio.emit('dashboard_update', {
                'system': system_status,
                'traffic': traffic_data,
                'detection': detection_data,
                'domain_detection': domain_data
            })
            
        except Exception as e:
            app_logger.error(f"更新仪表盘失败: {str(e)}")
        
        time.sleep(app.config['SYSTEM_MONITOR_INTERVAL'])

@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    app_logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """处理WebSocket断开"""
    app_logger.info('Client disconnected')

def start_background_tasks():
    """启动后台任务"""
    try:
        # 启动流量捕获
        capture_service.start_capture()
        
        # 启动仪表盘更新
        dashboard_thread = threading.Thread(target=update_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        app_logger.info("后台任务启动成功")
    except Exception as e:
        app_logger.error(f"后台任务启动失败: {str(e)}")
        sys.exit(1)

@app.route('/api/domain/detect', methods=['POST'])
def detect_domain():
    """检测域名API"""
    try:
        data = request.get_json()
        domain = data.get('domain')
        if not domain:
            return jsonify({'error': '域名不能为空'}), 400
            
        result = domain_detection_service.detect_domain(domain)
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
            success = domain_detection_service.add_to_blacklist(domain)
        elif action == 'remove':
            success = domain_detection_service.remove_from_blacklist(domain)
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
    
    # 启动后台任务
    start_background_tasks()
    
    # 启动应用
    app_logger.info("DDoS检测系统启动")
    socketio.run(
        app,
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    ) 