import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from app.utils.logger import model_logger

class CNNLSTMDetector:
    """基于CNN+LSTM的DDoS检测器"""
    
    def __init__(self, input_shape=(100, 1), learning_rate=0.001):
        self.input_shape = input_shape
        self.learning_rate = learning_rate
        self.model = None
        self.history = None
        
    def build_model(self):
        """构建CNN+LSTM模型"""
        try:
            model = Sequential([
                # CNN层
                Conv1D(64, 3, activation='relu', input_shape=self.input_shape),
                BatchNormalization(),
                MaxPooling1D(2),
                Dropout(0.2),
                
                Conv1D(32, 3, activation='relu'),
                BatchNormalization(),
                MaxPooling1D(2),
                Dropout(0.2),
                
                # LSTM层
                LSTM(32, return_sequences=True),
                BatchNormalization(),
                Dropout(0.2),
                
                LSTM(16),
                BatchNormalization(),
                Dropout(0.2),
                
                # 输出层
                Dense(8, activation='relu'),
                BatchNormalization(),
                Dense(1, activation='sigmoid')
            ])
            
            # 编译模型
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy', tf.keras.metrics.AUC()]
            )
            
            self.model = model
            model_logger.info("CNN+LSTM模型构建完成")
            return model
            
        except Exception as e:
            model_logger.error(f"模型构建失败: {str(e)}")
            raise
    
    def train(self, X_train, y_train, X_val=None, y_val=None, 
              batch_size=32, epochs=100, validation_split=0.2):
        """训练模型"""
        try:
            if self.model is None:
                self.build_model()
            
            # 数据预处理
            X_train = self._preprocess_data(X_train)
            if X_val is not None:
                X_val = self._preprocess_data(X_val)
            
            # 回调函数
            callbacks = [
                ModelCheckpoint(
                    'models/cnn_lstm_best.h5',
                    monitor='val_accuracy',
                    save_best_only=True,
                    mode='max'
                ),
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                )
            ]
            
            # 训练模型
            self.history = self.model.fit(
                X_train, y_train,
                batch_size=batch_size,
                epochs=epochs,
                validation_data=(X_val, y_val) if X_val is not None else None,
                validation_split=validation_split if X_val is None else None,
                callbacks=callbacks,
                verbose=1
            )
            
            model_logger.info("CNN+LSTM模型训练完成")
            return self.history
            
        except Exception as e:
            model_logger.error(f"模型训练失败: {str(e)}")
            raise
    
    def predict(self, X):
        """预测样本类别"""
        try:
            # 数据预处理
            X = self._preprocess_data(X)
            
            # 预测
            predictions = self.model.predict(X)
            return predictions
            
        except Exception as e:
            model_logger.error(f"模型预测失败: {str(e)}")
            raise
    
    def evaluate(self, X, y):
        """评估模型"""
        try:
            # 数据预处理
            X = self._preprocess_data(X)
            
            # 评估
            results = self.model.evaluate(X, y)
            metrics = dict(zip(self.model.metrics_names, results))
            
            model_logger.info(f"模型评估结果: {metrics}")
            return metrics
            
        except Exception as e:
            model_logger.error(f"模型评估失败: {str(e)}")
            raise
    
    def _preprocess_data(self, X):
        """数据预处理"""
        try:
            # 确保数据形状正确
            if len(X.shape) == 2:
                X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # 标准化
            X = (X - np.mean(X)) / (np.std(X) + 1e-10)
            
            return X
            
        except Exception as e:
            model_logger.error(f"数据预处理失败: {str(e)}")
            raise
    
    def save_model(self, path):
        """保存模型"""
        try:
            self.model.save(path)
            model_logger.info(f"模型已保存到: {path}")
        except Exception as e:
            model_logger.error(f"模型保存失败: {str(e)}")
            raise
    
    def load_model(self, path):
        """加载模型"""
        try:
            self.model = load_model(path)
            model_logger.info(f"模型已从 {path} 加载")
        except Exception as e:
            model_logger.error(f"模型加载失败: {str(e)}")
            raise
    
    def get_model_summary(self):
        """获取模型摘要"""
        if self.model is None:
            return "模型尚未构建"
        return self.model.summary() 