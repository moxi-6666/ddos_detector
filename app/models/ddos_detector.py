import numpy as np
from .skm_hfs_detector import SKMHFSDetector
from .cnn_lstm_detector import CNNLSTMDetector
import joblib
import os

class DDoSDetector:
    """DDoS攻击检测器，整合SKM-HFS和CNN+LSTM模型"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.feature_names = [
            'packet_rate', 'byte_rate', 'avg_packet_size',
            'tcp_ratio', 'udp_ratio', 'icmp_ratio',
            'syn_ratio', 'fin_ratio', 'rst_ratio',
            'entropy_src_ip', 'entropy_dst_ip',
            'entropy_src_port', 'entropy_dst_port'
        ]
        
        # 初始化检测模型
        self.skm_hfs = SKMHFSDetector(
            n_clusters=3,
            feature_layers=3
        )
        
        self.cnn_lstm = CNNLSTMDetector(
            seq_length=100,
            n_features=len(self.feature_names),
            n_classes=2
        )
        
        # 加载预训练模型（如果存在）
        self._load_models()
        
    def _load_models(self):
        """加载预训练模型"""
        model_dir = self.config.get('model_dir', 'models')
        
        # 加载SKM-HFS模型
        skm_path = os.path.join(model_dir, 'skm_hfs.joblib')
        if os.path.exists(skm_path):
            self.skm_hfs = joblib.load(skm_path)
            
        # 加载CNN+LSTM模型
        cnn_lstm_path = os.path.join(model_dir, 'cnn_lstm.h5')
        if os.path.exists(cnn_lstm_path):
            self.cnn_lstm.load_model(cnn_lstm_path)
    
    def _save_models(self):
        """保存训练好的模型"""
        model_dir = self.config.get('model_dir', 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        # 保存SKM-HFS模型
        skm_path = os.path.join(model_dir, 'skm_hfs.joblib')
        joblib.dump(self.skm_hfs, skm_path)
        
        # 保存CNN+LSTM模型
        cnn_lstm_path = os.path.join(model_dir, 'cnn_lstm.h5')
        self.cnn_lstm.save_model(cnn_lstm_path)
    
    def extract_features(self, traffic_data):
        """从流量数据中提取特征"""
        features = {}
        
        # 计算基本统计特征
        features['packet_rate'] = len(traffic_data) / 60  # 每分钟包数
        features['byte_rate'] = sum(p.get('length', 0) for p in traffic_data) / 60  # 每分钟字节数
        features['avg_packet_size'] = features['byte_rate'] / features['packet_rate'] if features['packet_rate'] > 0 else 0
        
        # 计算协议比例
        total_packets = len(traffic_data)
        tcp_packets = sum(1 for p in traffic_data if p.get('protocol') == 'TCP')
        udp_packets = sum(1 for p in traffic_data if p.get('protocol') == 'UDP')
        icmp_packets = sum(1 for p in traffic_data if p.get('protocol') == 'ICMP')
        
        features['tcp_ratio'] = tcp_packets / total_packets if total_packets > 0 else 0
        features['udp_ratio'] = udp_packets / total_packets if total_packets > 0 else 0
        features['icmp_ratio'] = icmp_packets / total_packets if total_packets > 0 else 0
        
        # 计算TCP标志比例
        tcp_flags = [p.get('tcp_flags', {}) for p in traffic_data if p.get('protocol') == 'TCP']
        if tcp_packets > 0:
            features['syn_ratio'] = sum(1 for f in tcp_flags if f.get('SYN')) / tcp_packets
            features['fin_ratio'] = sum(1 for f in tcp_flags if f.get('FIN')) / tcp_packets
            features['rst_ratio'] = sum(1 for f in tcp_flags if f.get('RST')) / tcp_packets
        else:
            features['syn_ratio'] = features['fin_ratio'] = features['rst_ratio'] = 0
        
        # 计算IP和端口熵
        from scipy.stats import entropy
        def calculate_entropy(values):
            if not values:
                return 0
            _, counts = np.unique(values, return_counts=True)
            return entropy(counts / len(values))
        
        features['entropy_src_ip'] = calculate_entropy([p.get('src_ip') for p in traffic_data])
        features['entropy_dst_ip'] = calculate_entropy([p.get('dst_ip') for p in traffic_data])
        features['entropy_src_port'] = calculate_entropy([p.get('src_port') for p in traffic_data])
        features['entropy_dst_port'] = calculate_entropy([p.get('dst_port') for p in traffic_data])
        
        # 转换为特征向量
        return np.array([features[name] for name in self.feature_names])
    
    def prepare_sequence_data(self, features_list, sequence_length=100):
        """准备序列数据用于CNN+LSTM模型"""
        sequences = []
        for i in range(0, len(features_list) - sequence_length + 1):
            sequence = features_list[i:i + sequence_length]
            sequences.append(sequence)
        return np.array(sequences)
    
    def fit(self, traffic_data_list, labels=None):
        """训练模型"""
        # 提取特征
        features_list = [self.extract_features(data) for data in traffic_data_list]
        features_array = np.array(features_list)
        
        # 训练SKM-HFS模型
        self.skm_hfs.fit(features_array, labeled_indices=None, labels=labels)
        
        # 准备CNN+LSTM的序列数据
        sequence_data = self.prepare_sequence_data(features_list)
        if labels is not None:
            sequence_labels = labels[self.cnn_lstm.seq_length-1:]
        else:
            # 使用SKM-HFS的预测结果作为伪标签
            predictions, _ = self.skm_hfs.predict(features_array)
            sequence_labels = predictions[self.cnn_lstm.seq_length-1:]
        
        # 训练CNN+LSTM模型
        self.cnn_lstm.fit(sequence_data, sequence_labels)
        
        # 保存训练好的模型
        self._save_models()
        
        return self
    
    def predict(self, traffic_data):
        """预测是否为DDoS攻击"""
        # 提取特征
        features = self.extract_features(traffic_data)
        
        # SKM-HFS预测
        skm_prediction, skm_score = self.skm_hfs.predict(features.reshape(1, -1))
        
        # 如果有足够的历史数据，使用CNN+LSTM预测
        if hasattr(self, '_history_features'):
            self._history_features.append(features)
            if len(self._history_features) > self.cnn_lstm.seq_length:
                self._history_features.pop(0)
                
            if len(self._history_features) == self.cnn_lstm.seq_length:
                sequence = np.array([self._history_features])
                cnn_lstm_prediction, cnn_lstm_score = self.cnn_lstm.predict(sequence)
                
                # 综合两个模型的结果
                final_prediction = (skm_prediction[0] + cnn_lstm_prediction[0]) > 0
                final_score = (skm_score[0] + cnn_lstm_score[0]) / 2
            else:
                final_prediction = skm_prediction[0]
                final_score = skm_score[0]
        else:
            self._history_features = [features]
            final_prediction = skm_prediction[0]
            final_score = skm_score[0]
        
        return final_prediction, final_score
    
    def get_feature_importance(self):
        """获取特征重要性"""
        return dict(zip(self.feature_names, self.skm_hfs.get_feature_importance())) 