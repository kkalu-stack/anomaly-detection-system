"""
Real-Time Anomaly Detection Engine

This module implements the core anomaly detection algorithms including:
- Isolation Forest
- One-Class SVM
- Autoencoder Neural Networks
- Statistical Methods
- Ensemble Methods
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger()

@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis"""
    is_anomaly: bool
    confidence: float
    score: float
    timestamp: datetime
    features: Dict[str, float]
    model_used: str
    threshold: float

class AnomalyDetector:
    """
    Real-time anomaly detection engine supporting multiple algorithms
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.models = {}
        self.scalers = {}
        self.thresholds = {}
        self.is_trained = False
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Anomaly detector initialized", 
                   model_count=len(self.models))
    
    def _initialize_models(self):
        """Initialize different anomaly detection models"""
        
        # Isolation Forest
        self.models['isolation_forest'] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # One-Class SVM
        self.models['one_class_svm'] = OneClassSVM(
            kernel='rbf',
            nu=0.1,
            gamma='scale'
        )
        
        # Autoencoder (will be built in train method)
        self.models['autoencoder'] = None
        
        # Statistical model
        self.models['statistical'] = None
        
        # Initialize scalers
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
            self.thresholds[model_name] = 0.8
    
    def build_autoencoder(self, input_dim: int) -> tf.keras.Model:
        """Build autoencoder neural network for anomaly detection"""
        
        # Encoder
        encoder = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu')
        ])
        
        # Decoder
        decoder = tf.keras.Sequential([
            tf.keras.layers.Dense(16, activation='relu', input_shape=(8,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(input_dim, activation='linear')
        ])
        
        # Autoencoder
        autoencoder = tf.keras.Sequential([encoder, decoder])
        
        autoencoder.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return autoencoder
    
    def train(self, data: pd.DataFrame, labels: Optional[pd.Series] = None) -> Dict[str, float]:
        """
        Train all anomaly detection models
        
        Args:
            data: Training data
            labels: Optional labels for supervised learning
            
        Returns:
            Dictionary of training metrics
        """
        
        logger.info("Starting model training", data_shape=data.shape)
        
        training_metrics = {}
        
        # Prepare data
        X = data.values
        feature_names = data.columns.tolist()
        
        # Train Isolation Forest
        logger.info("Training Isolation Forest")
        X_scaled = self.scalers['isolation_forest'].fit_transform(X)
        self.models['isolation_forest'].fit(X_scaled)
        
        # Train One-Class SVM
        logger.info("Training One-Class SVM")
        X_scaled = self.scalers['one_class_svm'].fit_transform(X)
        self.models['one_class_svm'].fit(X_scaled)
        
        # Train Autoencoder
        logger.info("Training Autoencoder")
        X_scaled = self.scalers['autoencoder'].fit_transform(X)
        autoencoder = self.build_autoencoder(X_scaled.shape[1])
        
        # Train autoencoder
        history = autoencoder.fit(
            X_scaled, X_scaled,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        self.models['autoencoder'] = autoencoder
        
        # Train Statistical model
        logger.info("Training Statistical model")
        X_scaled = self.scalers['statistical'].fit_transform(X)
        self.models['statistical'] = {
            'mean': np.mean(X_scaled, axis=0),
            'std': np.std(X_scaled, axis=0),
            'feature_names': feature_names
        }
        
        # Calculate thresholds
        self._calculate_thresholds(X_scaled)
        
        self.is_trained = True
        
        logger.info("Model training completed", 
                   models_trained=list(self.models.keys()))
        
        return training_metrics
    
    def _calculate_thresholds(self, X_scaled: np.ndarray):
        """Calculate optimal thresholds for each model"""
        
        # Isolation Forest threshold
        scores = self.models['isolation_forest'].score_samples(X_scaled)
        self.thresholds['isolation_forest'] = np.percentile(scores, 10)
        
        # One-Class SVM threshold
        scores = self.models['one_class_svm'].score_samples(X_scaled)
        self.thresholds['one_class_svm'] = np.percentile(scores, 10)
        
        # Autoencoder threshold
        reconstructed = self.models['autoencoder'].predict(X_scaled)
        mse_scores = np.mean((X_scaled - reconstructed) ** 2, axis=1)
        self.thresholds['autoencoder'] = np.percentile(mse_scores, 90)
        
        # Statistical threshold
        z_scores = np.abs((X_scaled - self.models['statistical']['mean']) / 
                         self.models['statistical']['std'])
        max_z_scores = np.max(z_scores, axis=1)
        self.thresholds['statistical'] = np.percentile(max_z_scores, 95)
    
    def detect_anomaly(self, data_point: Dict[str, float], 
                       model_name: str = 'ensemble') -> AnomalyResult:
        """
        Detect anomaly in a single data point
        
        Args:
            data_point: Dictionary of feature values
            model_name: Name of the model to use ('ensemble' for all models)
            
        Returns:
            AnomalyResult object
        """
        
        if not self.is_trained:
            raise ValueError("Models must be trained before detection")
        
        # Convert to DataFrame
        df = pd.DataFrame([data_point])
        X = df.values
        
        if model_name == 'ensemble':
            return self._ensemble_detection(X, data_point)
        else:
            return self._single_model_detection(X, data_point, model_name)
    
    def _single_model_detection(self, X: np.ndarray, 
                               data_point: Dict[str, float], 
                               model_name: str) -> AnomalyResult:
        """Detect anomaly using a single model"""
        
        X_scaled = self.scalers[model_name].transform(X)
        
        if model_name == 'isolation_forest':
            score = self.models[model_name].score_samples(X_scaled)[0]
            is_anomaly = score < self.thresholds[model_name]
            confidence = abs(score - self.thresholds[model_name])
            
        elif model_name == 'one_class_svm':
            score = self.models[model_name].score_samples(X_scaled)[0]
            is_anomaly = score < self.thresholds[model_name]
            confidence = abs(score - self.thresholds[model_name])
            
        elif model_name == 'autoencoder':
            reconstructed = self.models[model_name].predict(X_scaled)
            mse = np.mean((X_scaled - reconstructed) ** 2)
            is_anomaly = mse > self.thresholds[model_name]
            confidence = mse / self.thresholds[model_name]
            score = mse
            
        elif model_name == 'statistical':
            z_scores = np.abs((X_scaled - self.models[model_name]['mean']) / 
                             self.models[model_name]['std'])
            max_z_score = np.max(z_scores)
            is_anomaly = max_z_score > self.thresholds[model_name]
            confidence = max_z_score / self.thresholds[model_name]
            score = max_z_score
            
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            confidence=min(confidence, 1.0),
            score=score,
            timestamp=datetime.now(),
            features=data_point,
            model_used=model_name,
            threshold=self.thresholds[model_name]
        )
    
    def _ensemble_detection(self, X: np.ndarray, 
                           data_point: Dict[str, float]) -> AnomalyResult:
        """Detect anomaly using ensemble of all models"""
        
        results = []
        
        for model_name in self.models.keys():
            try:
                result = self._single_model_detection(X, data_point, model_name)
                results.append(result)
            except Exception as e:
                logger.warning(f"Error in {model_name} detection", error=str(e))
        
        if not results:
            raise ValueError("No models could process the data point")
        
        # Ensemble decision (majority vote)
        anomaly_votes = sum(1 for r in results if r.is_anomaly)
        is_anomaly = anomaly_votes > len(results) / 2
        
        # Average confidence
        avg_confidence = np.mean([r.confidence for r in results])
        
        # Average score
        avg_score = np.mean([r.score for r in results])
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            confidence=avg_confidence,
            score=avg_score,
            timestamp=datetime.now(),
            features=data_point,
            model_used='ensemble',
            threshold=np.mean([r.threshold for r in results])
        )
    
    def batch_detect(self, data: pd.DataFrame, 
                     model_name: str = 'ensemble') -> List[AnomalyResult]:
        """
        Detect anomalies in a batch of data points
        
        Args:
            data: DataFrame with multiple data points
            model_name: Name of the model to use
            
        Returns:
            List of AnomalyResult objects
        """
        
        results = []
        
        for idx, row in data.iterrows():
            data_point = row.to_dict()
            result = self.detect_anomaly(data_point, model_name)
            results.append(result)
        
        return results
    
    def save_models(self, path: str):
        """Save trained models to disk"""
        
        for model_name, model in self.models.items():
            if model_name == 'autoencoder':
                model.save(f"{path}/{model_name}.h5")
            elif model_name == 'statistical':
                joblib.dump(model, f"{path}/{model_name}.pkl")
            else:
                joblib.dump(model, f"{path}/{model_name}.pkl")
        
        # Save scalers and thresholds
        joblib.dump(self.scalers, f"{path}/scalers.pkl")
        joblib.dump(self.thresholds, f"{path}/thresholds.pkl")
        
        logger.info("Models saved", path=path)
    
    def load_models(self, path: str):
        """Load trained models from disk"""
        
        for model_name in self.models.keys():
            if model_name == 'autoencoder':
                self.models[model_name] = tf.keras.models.load_model(f"{path}/{model_name}.h5")
            elif model_name == 'statistical':
                self.models[model_name] = joblib.load(f"{path}/{model_name}.pkl")
            else:
                self.models[model_name] = joblib.load(f"{path}/{model_name}.pkl")
        
        # Load scalers and thresholds
        self.scalers = joblib.load(f"{path}/scalers.pkl")
        self.thresholds = joblib.load(f"{path}/thresholds.pkl")
        
        self.is_trained = True
        logger.info("Models loaded", path=path)
    
    def get_model_performance(self, test_data: pd.DataFrame, 
                             test_labels: pd.Series) -> Dict[str, float]:
        """Evaluate model performance on test data"""
        
        if not self.is_trained:
            raise ValueError("Models must be trained before evaluation")
        
        results = self.batch_detect(test_data)
        predictions = [r.is_anomaly for r in results]
        
        # Convert labels to binary (0 for normal, 1 for anomaly)
        y_true = (test_labels == 1).astype(int)
        y_pred = np.array(predictions).astype(int)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        } 