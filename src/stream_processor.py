"""
Real-Time Stream Processor

This module handles real-time data ingestion from Kafka streams,
processes the data through anomaly detection models, and publishes
results back to Kafka topics.
"""

import json
import asyncio
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import structlog
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import threading
from queue import Queue
import redis

from .anomaly_detector import AnomalyDetector, AnomalyResult

logger = structlog.get_logger()

@dataclass
class StreamConfig:
    """Configuration for stream processing"""
    kafka_bootstrap_servers: str
    input_topic: str
    output_topic: str
    alert_topic: str
    consumer_group_id: str
    batch_size: int = 100
    batch_timeout: int = 5  # seconds
    max_retries: int = 3
    retry_delay: int = 1  # seconds

@dataclass
class StreamMessage:
    """Message structure for stream processing"""
    id: str
    timestamp: datetime
    data: Dict[str, float]
    source: str
    metadata: Dict = None

class StreamProcessor:
    """
    Real-time stream processor for anomaly detection
    """
    
    def __init__(self, config: StreamConfig, anomaly_detector: AnomalyDetector):
        self.config = config
        self.anomaly_detector = anomaly_detector
        self.producer = None
        self.consumer = None
        self.redis_client = None
        self.is_running = False
        self.message_queue = Queue(maxsize=1000)
        self.processing_thread = None
        
        # Initialize connections
        self._initialize_connections()
        
        logger.info("Stream processor initialized", 
                   config=asdict(config))
    
    def _initialize_connections(self):
        """Initialize Kafka and Redis connections"""
        
        try:
            # Initialize Kafka producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3
            )
            
            # Initialize Kafka consumer
            self.consumer = KafkaConsumer(
                self.config.input_topic,
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                group_id=self.config.consumer_group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            
            # Initialize Redis client
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            
            logger.info("Connections initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize connections", error=str(e))
            raise
    
    def start(self):
        """Start the stream processor"""
        
        if self.is_running:
            logger.warning("Stream processor is already running")
            return
        
        self.is_running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_messages)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Start consuming messages
        self._consume_messages()
        
        logger.info("Stream processor started")
    
    def stop(self):
        """Stop the stream processor"""
        
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        if self.consumer:
            self.consumer.close()
        
        if self.producer:
            self.producer.close()
        
        logger.info("Stream processor stopped")
    
    def _consume_messages(self):
        """Consume messages from Kafka topic"""
        
        logger.info("Starting message consumption", 
                   topic=self.config.input_topic)
        
        try:
            for message in self.consumer:
                if not self.is_running:
                    break
                
                try:
                    # Parse message
                    stream_message = self._parse_message(message)
                    
                    # Add to processing queue
                    if not self.message_queue.full():
                        self.message_queue.put(stream_message)
                    else:
                        logger.warning("Message queue is full, dropping message")
                        
                except Exception as e:
                    logger.error("Error processing message", 
                               error=str(e), 
                               message=message.value)
                    
        except Exception as e:
            logger.error("Error in message consumption", error=str(e))
        finally:
            logger.info("Message consumption stopped")
    
    def _parse_message(self, message) -> StreamMessage:
        """Parse Kafka message into StreamMessage"""
        
        data = message.value
        
        return StreamMessage(
            id=data.get('id', str(time.time())),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            data=data.get('data', {}),
            source=data.get('source', 'unknown'),
            metadata=data.get('metadata', {})
        )
    
    def _process_messages(self):
        """Process messages from the queue"""
        
        logger.info("Starting message processing")
        
        batch = []
        last_batch_time = time.time()
        
        while self.is_running:
            try:
                # Get message from queue with timeout
                try:
                    message = self.message_queue.get(timeout=1)
                    batch.append(message)
                except:
                    # Timeout - check if we should process current batch
                    if batch and (time.time() - last_batch_time) >= self.config.batch_timeout:
                        self._process_batch(batch)
                        batch = []
                        last_batch_time = time.time()
                    continue
                
                # Process batch if it's full or timeout reached
                if len(batch) >= self.config.batch_size or \
                   (time.time() - last_batch_time) >= self.config.batch_timeout:
                    self._process_batch(batch)
                    batch = []
                    last_batch_time = time.time()
                    
            except Exception as e:
                logger.error("Error in message processing", error=str(e))
                time.sleep(1)
        
        # Process remaining messages
        if batch:
            self._process_batch(batch)
        
        logger.info("Message processing stopped")
    
    def _process_batch(self, messages: List[StreamMessage]):
        """Process a batch of messages"""
        
        if not messages:
            return
        
        logger.info("Processing batch", 
                   batch_size=len(messages),
                   first_id=messages[0].id,
                   last_id=messages[-1].id)
        
        try:
            # Convert to DataFrame for batch processing
            data_list = []
            for msg in messages:
                data_list.append(msg.data)
            
            df = pd.DataFrame(data_list)
            
            # Detect anomalies
            results = self.anomaly_detector.batch_detect(df)
            
            # Process results
            for i, (message, result) in enumerate(zip(messages, results)):
                self._handle_anomaly_result(message, result)
                
        except Exception as e:
            logger.error("Error processing batch", 
                        error=str(e),
                        batch_size=len(messages))
    
    def _handle_anomaly_result(self, message: StreamMessage, result: AnomalyResult):
        """Handle individual anomaly detection result"""
        
        # Create output message
        output_message = {
            'id': message.id,
            'timestamp': result.timestamp.isoformat(),
            'source': message.source,
            'is_anomaly': result.is_anomaly,
            'confidence': result.confidence,
            'score': result.score,
            'model_used': result.model_used,
            'features': result.features,
            'metadata': message.metadata or {}
        }
        
        # Publish to output topic
        self._publish_message(self.config.output_topic, output_message)
        
        # If anomaly detected, publish to alert topic
        if result.is_anomaly:
            alert_message = {
                'id': message.id,
                'timestamp': result.timestamp.isoformat(),
                'source': message.source,
                'severity': 'high' if result.confidence > 0.8 else 'medium',
                'confidence': result.confidence,
                'score': result.score,
                'model_used': result.model_used,
                'features': result.features,
                'message': f"Anomaly detected with {result.confidence:.2f} confidence",
                'metadata': message.metadata or {}
            }
            
            self._publish_message(self.config.alert_topic, alert_message)
            
            # Store in Redis for quick access
            self._store_alert(alert_message)
        
        # Update metrics
        self._update_metrics(result)
    
    def _publish_message(self, topic: str, message: Dict):
        """Publish message to Kafka topic"""
        
        try:
            future = self.producer.send(
                topic,
                key=message['id'],
                value=message
            )
            
            # Wait for send confirmation
            record_metadata = future.get(timeout=10)
            
            logger.debug("Message published", 
                        topic=topic,
                        partition=record_metadata.partition,
                        offset=record_metadata.offset)
                        
        except Exception as e:
            logger.error("Failed to publish message", 
                        topic=topic,
                        error=str(e))
    
    def _store_alert(self, alert_message: Dict):
        """Store alert in Redis for quick access"""
        
        try:
            alert_key = f"alert:{alert_message['id']}"
            self.redis_client.setex(
                alert_key,
                3600,  # TTL: 1 hour
                json.dumps(alert_message)
            )
            
            # Add to recent alerts list
            self.redis_client.lpush('recent_alerts', alert_key)
            self.redis_client.ltrim('recent_alerts', 0, 99)  # Keep last 100
            
        except Exception as e:
            logger.error("Failed to store alert in Redis", error=str(e))
    
    def _update_metrics(self, result: AnomalyResult):
        """Update processing metrics"""
        
        try:
            # Update total processed count
            self.redis_client.incr('metrics:total_processed')
            
            # Update anomaly count
            if result.is_anomaly:
                self.redis_client.incr('metrics:anomalies_detected')
            
            # Update confidence histogram
            confidence_bucket = int(result.confidence * 10)
            self.redis_client.hincrby('metrics:confidence_histogram', confidence_bucket, 1)
            
            # Update model usage
            self.redis_client.hincrby('metrics:model_usage', result.model_used, 1)
            
        except Exception as e:
            logger.error("Failed to update metrics", error=str(e))
    
    def get_metrics(self) -> Dict:
        """Get current processing metrics"""
        
        try:
            metrics = {
                'total_processed': int(self.redis_client.get('metrics:total_processed') or 0),
                'anomalies_detected': int(self.redis_client.get('metrics:anomalies_detected') or 0),
                'confidence_histogram': self.redis_client.hgetall('metrics:confidence_histogram'),
                'model_usage': self.redis_client.hgetall('metrics:model_usage'),
                'queue_size': self.message_queue.qsize(),
                'is_running': self.is_running
            }
            
            # Calculate anomaly rate
            if metrics['total_processed'] > 0:
                metrics['anomaly_rate'] = metrics['anomalies_detected'] / metrics['total_processed']
            else:
                metrics['anomaly_rate'] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            return {}
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts from Redis"""
        
        try:
            alert_keys = self.redis_client.lrange('recent_alerts', 0, limit - 1)
            alerts = []
            
            for key in alert_keys:
                alert_data = self.redis_client.get(key)
                if alert_data:
                    alerts.append(json.loads(alert_data))
            
            return alerts
            
        except Exception as e:
            logger.error("Failed to get recent alerts", error=str(e))
            return []

class DataGenerator:
    """Generate synthetic data for testing"""
    
    def __init__(self, feature_count: int = 10):
        self.feature_count = feature_count
        self.base_values = np.random.randn(feature_count)
        self.trend = np.random.randn(feature_count) * 0.01
        
    def generate_normal_data(self) -> Dict[str, float]:
        """Generate normal data point"""
        
        # Add some trend and noise
        values = self.base_values + self.trend + np.random.randn(self.feature_count) * 0.1
        self.base_values = values
        
        return {f'feature_{i}': float(val) for i, val in enumerate(values)}
    
    def generate_anomaly_data(self) -> Dict[str, float]:
        """Generate anomalous data point"""
        
        # Add significant deviation
        anomaly_factor = np.random.choice([-3, 3])  # Large positive or negative deviation
        values = self.base_values + np.random.randn(self.feature_count) * anomaly_factor
        
        return {f'feature_{i}': float(val) for i, val in enumerate(values)}
    
    def generate_message(self, is_anomaly: bool = False) -> Dict:
        """Generate complete message"""
        
        data = self.generate_anomaly_data() if is_anomaly else self.generate_normal_data()
        
        return {
            'id': f"msg_{int(time.time() * 1000)}",
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'source': 'synthetic_generator',
            'metadata': {
                'is_anomaly': is_anomaly,
                'generator': 'synthetic'
            }
        } 