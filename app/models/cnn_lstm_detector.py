import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint

class CNNLSTMDetector:
    """基于CNN-LSTM的DDoS检测器"""
    
    def __init__(self, seq_length=100, n_features=12, n_classes=2):
        self.seq_length = seq_length
        self.n_features = n_features
        self.n_classes = n_classes
        self.model = self._build_model()
        
    def _build_model(self):
        """构建CNN-LSTM模型"""
        model = Sequential([
            # CNN层
            Conv1D(filters=64, kernel_size=3, activation='relu', 
                   input_shape=(self.seq_length, self.n_features)),
            MaxPooling1D(pool_size=2),
            Conv1D(filters=32, kernel_size=3, activation='relu'),
            MaxPooling1D(pool_size=2),
            
            # LSTM层
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            
            # 全连接层
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(self.n_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
    def fit(self, X, y, epochs=10, batch_size=32, validation_split=0.2):
        """训练模型"""
        # 确保输入数据形状正确
        if len(X.shape) == 2:
            X = X.reshape((X.shape[0], self.seq_length, self.n_features))
            
        # 转换标签为one-hot编码
        y = tf.keras.utils.to_categorical(y, num_classes=self.n_classes)
        
        # 添加模型检查点
        checkpoint = ModelCheckpoint(
            'best_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )
        
        # 训练模型
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[checkpoint]
        )
        
        return history
        
    def predict(self, X):
        """预测新样本"""
        # 确保输入数据形状正确
        if len(X.shape) == 2:
            X = X.reshape((X.shape[0], self.seq_length, self.n_features))
            
        # 获取预测结果
        predictions = self.model.predict(X)
        
        # 获取预测类别和置信度
        predicted_classes = np.argmax(predictions, axis=1)
        confidence_scores = np.max(predictions, axis=1)
        
        return predicted_classes, confidence_scores
        
    def load_model(self, model_path):
        """加载预训练模型"""
        self.model = tf.keras.models.load_model(model_path)
        
    def save_model(self, model_path):
        """保存模型"""
        self.model.save(model_path) 