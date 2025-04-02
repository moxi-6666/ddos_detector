import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from ..config.config import config
from ..utils.mongo_helper import MongoHelper

class AlertService:
    def __init__(self):
        self.config = config['default']
        self.mongo_helper = MongoHelper()
        self.alert_levels = {
            'low': 0,
            'medium': 1,
            'high': 2,
            'critical': 3
        }
        
    def create_alert(self, message, level='medium', data=None):
        """创建新告警"""
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'level': level,
            'data': data or {},
            'status': 'new',
            'handled_by': None,
            'handled_at': None
        }
        
        # 保存到数据库
        self.mongo_helper.save_alert(alert)
        
        # 根据告警级别决定通知方式
        if self.alert_levels[level] >= self.alert_levels['high']:
            self._send_urgent_notification(alert)
            
        return alert
        
    def handle_alert(self, alert_id, handler):
        """处理告警"""
        alert = self.mongo_helper.get_alert(alert_id)
        if not alert:
            return False
            
        alert['status'] = 'handled'
        alert['handled_by'] = handler
        alert['handled_at'] = datetime.now()
        
        return self.mongo_helper.update_alert(alert_id, alert)
        
    def get_active_alerts(self):
        """获取活动告警"""
        return self.mongo_helper.get_alerts({'status': 'new'})
        
    def get_alert_statistics(self, start_time=None, end_time=None):
        """获取告警统计信息"""
        return self.mongo_helper.get_alert_statistics(start_time, end_time)
        
    def _send_urgent_notification(self, alert):
        """发送紧急通知"""
        if 'email' in self.config.ALERT_METHODS:
            self._send_email_alert(alert)
            
    def _send_email_alert(self, alert):
        """发送邮件告警"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.SMTP_USER
            msg['To'] = self.config.ALERT_EMAIL
            msg['Subject'] = f"[DDoS检测系统] {alert['level'].upper()} 级别告警"
            
            body = f"""
            告警时间: {alert['timestamp']}
            告警级别: {alert['level']}
            告警内容: {alert['message']}
            
            详细信息:
            {json.dumps(alert['data'], indent=2, ensure_ascii=False)}
            
            请及时处理！
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.send_message(msg)
                
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            
    def create_attack_alert(self, detection_result):
        """创建攻击告警"""
        confidence = detection_result['confidence']
        
        # 根据置信度确定告警级别
        if confidence > 0.9:
            level = 'critical'
        elif confidence > 0.8:
            level = 'high'
        elif confidence > 0.6:
            level = 'medium'
        else:
            level = 'low'
            
        message = f"检测到可能的DDoS攻击，置信度: {confidence:.2%}"
        
        return self.create_alert(
            message=message,
            level=level,
            data={
                'detection_result': detection_result,
                'source_ip': detection_result.get('source_ip'),
                'target_ip': detection_result.get('target_ip'),
                'attack_type': detection_result.get('attack_type')
            }
        ) 