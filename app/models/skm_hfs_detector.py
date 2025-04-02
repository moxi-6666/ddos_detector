import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class SKMHFSDetector:
    """基于SKM-HFS的DDoS检测器"""
    
    def __init__(self, n_clusters=3, feature_layers=3):
        self.n_clusters = n_clusters
        self.feature_layers = feature_layers
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.feature_importance = None
        
    def fit(self, X):
        """训练模型"""
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练KMeans
        self.kmeans.fit(X_scaled)
        
        # 计算特征重要性
        self._calculate_feature_importance(X_scaled)
        
        return self
        
    def predict(self, X):
        """预测是否为攻击"""
        # 标准化特征
        X_scaled = self.scaler.transform(X)
        
        # 获取聚类标签
        labels = self.kmeans.predict(X_scaled)
        
        # 计算到聚类中心的距离
        distances = self.kmeans.transform(X_scaled)
        min_distances = np.min(distances, axis=1)
        
        # 根据距离判断是否为攻击
        predictions = min_distances > np.percentile(min_distances, 95)
        scores = min_distances / np.max(min_distances)
        
        return predictions, scores
        
    def _calculate_feature_importance(self, X):
        """计算特征重要性"""
        # 使用聚类中心计算特征重要性
        centers = self.kmeans.cluster_centers_
        std = np.std(centers, axis=0)
        self.feature_importance = std / np.sum(std)
        
    def get_feature_importance(self):
        """获取特征重要性"""
        return self.feature_importance 