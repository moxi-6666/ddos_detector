import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.utils.logger import model_logger

class SKMHFSDetector:
    """基于半监督加权K-means的DDoS检测器"""
    
    def __init__(self, n_clusters=2, max_iter=300, random_state=42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = None
        self.feature_weights = None
        
    def fit(self, X, y=None):
        """训练模型"""
        try:
            # 标准化数据
            X_scaled = self.scaler.fit_transform(X)
            
            # 初始化特征权重
            n_features = X.shape[1]
            self.feature_weights = np.ones(n_features) / n_features
            
            # 半监督学习过程
            for _ in range(self.max_iter):
                # 1. 使用当前权重计算加权距离
                weighted_X = X_scaled * self.feature_weights
                
                # 2. 执行K-means聚类
                self.kmeans = KMeans(
                    n_clusters=self.n_clusters,
                    random_state=self.random_state
                )
                self.kmeans.fit(weighted_X)
                
                # 3. 更新特征权重
                self._update_weights(X_scaled, self.kmeans.labels_)
                
                # 4. 检查收敛
                if self._check_convergence():
                    break
            
            model_logger.info("SKM-HFS模型训练完成")
            return self
            
        except Exception as e:
            model_logger.error(f"SKM-HFS模型训练失败: {str(e)}")
            raise
    
    def predict(self, X):
        """预测样本类别"""
        try:
            # 标准化数据
            X_scaled = self.scaler.transform(X)
            
            # 使用训练好的权重和模型进行预测
            weighted_X = X_scaled * self.feature_weights
            predictions = self.kmeans.predict(weighted_X)
            
            # 将聚类标签转换为攻击/正常标签
            # 假设较大的簇为正常流量
            if np.mean(self.kmeans.cluster_centers_, axis=1)[0] > np.mean(self.kmeans.cluster_centers_, axis=1)[1]:
                predictions = 1 - predictions
            
            return predictions
            
        except Exception as e:
            model_logger.error(f"SKM-HFS模型预测失败: {str(e)}")
            raise
    
    def _update_weights(self, X, labels):
        """更新特征权重"""
        try:
            # 计算每个簇的特征方差
            variances = []
            for i in range(self.n_clusters):
                cluster_data = X[labels == i]
                variances.append(np.var(cluster_data, axis=0))
            
            # 计算平均方差
            mean_variances = np.mean(variances, axis=0)
            
            # 更新权重
            self.feature_weights = 1 / (mean_variances + 1e-10)
            self.feature_weights /= np.sum(self.feature_weights)
            
        except Exception as e:
            model_logger.error(f"特征权重更新失败: {str(e)}")
            raise
    
    def _check_convergence(self, tol=1e-4):
        """检查算法是否收敛"""
        if not hasattr(self, '_prev_weights'):
            self._prev_weights = np.zeros_like(self.feature_weights)
            return False
        
        # 计算权重变化
        weight_change = np.sum(np.abs(self.feature_weights - self._prev_weights))
        self._prev_weights = self.feature_weights.copy()
        
        return weight_change < tol
    
    def get_feature_importance(self):
        """获取特征重要性"""
        return dict(zip(range(len(self.feature_weights)), self.feature_weights))
    
    def save_model(self, path):
        """保存模型"""
        try:
            import joblib
            model_data = {
                'kmeans': self.kmeans,
                'scaler': self.scaler,
                'feature_weights': self.feature_weights
            }
            joblib.dump(model_data, path)
            model_logger.info(f"模型已保存到: {path}")
        except Exception as e:
            model_logger.error(f"模型保存失败: {str(e)}")
            raise
    
    def load_model(self, path):
        """加载模型"""
        try:
            import joblib
            model_data = joblib.load(path)
            self.kmeans = model_data['kmeans']
            self.scaler = model_data['scaler']
            self.feature_weights = model_data['feature_weights']
            model_logger.info(f"模型已从 {path} 加载")
        except Exception as e:
            model_logger.error(f"模型加载失败: {str(e)}")
            raise 