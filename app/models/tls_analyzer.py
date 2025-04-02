import numpy as np
import tensorflow as tf
from ..config.config import config
from datetime import datetime

class TLSAnalyzer:
    def __init__(self):
        self.config = config['default']
        self.model = self._load_model()
        self.feature_names = [
            'cert_key_length',
            'cert_valid_days',
            'cert_extension_count',
            'cipher_suite_count',
            'compression_method',
            'tls_version',
            'handshake_duration',
            'session_reuse',
            'cert_chain_length',
            'sni_length'
        ]
        
    def _load_model(self):
        """加载预训练模型"""
        try:
            return tf.keras.models.load_model(self.config.MODEL_PATH['tls'])
        except Exception as e:
            print(f"Failed to load TLS model: {str(e)}")
            return self._create_model()
            
    def _create_model(self):
        """创建新模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(32, activation='relu', input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')  # 正常、加密恶意、未加密恶意
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
    def extract_features(self, tls_session):
        """从TLS会话中提取特征"""
        features = np.zeros(len(self.feature_names))
        
        try:
            # 证书相关特征
            if 'certificate' in tls_session:
                cert = tls_session['certificate']
                features[0] = cert.get('key_length', 0)
                features[1] = (cert.get('not_after', datetime.now()) - 
                             cert.get('not_before', datetime.now())).days
                features[2] = len(cert.get('extensions', []))
                features[8] = len(cert.get('chain', []))
            
            # TLS握手相关特征
            if 'handshake' in tls_session:
                handshake = tls_session['handshake']
                features[3] = len(handshake.get('cipher_suites', []))
                features[4] = handshake.get('compression_method', 0)
                features[5] = handshake.get('version', 0)
                features[6] = handshake.get('duration', 0)
                features[7] = 1 if handshake.get('session_reuse', False) else 0
                features[9] = len(handshake.get('sni', ''))
                
        except Exception as e:
            print(f"Feature extraction error: {str(e)}")
            
        return features
        
    def analyze(self, tls_session):
        """分析TLS流量"""
        features = self.extract_features(tls_session)
        features = features.reshape(1, -1)
        
        prediction = self.model.predict(features)[0]
        traffic_type = np.argmax(prediction)
        confidence = float(prediction[traffic_type])
        
        result = {
            'timestamp': datetime.now(),
            'traffic_type': self._get_traffic_type(traffic_type),
            'confidence': confidence,
            'features': dict(zip(self.feature_names, features[0])),
            'is_malicious': traffic_type > 0
        }
        
        return result
        
    def _get_traffic_type(self, type_id):
        """获取流量类型描述"""
        types = {
            0: 'normal',
            1: 'encrypted_malicious',
            2: 'unencrypted_malicious'
        }
        return types.get(type_id, 'unknown')
        
    def train(self, X, y, epochs=10, batch_size=32):
        """训练模型"""
        return self.model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2)
        
    def save_model(self):
        """保存模型"""
        self.model.save(self.config.MODEL_PATH['tls']) 