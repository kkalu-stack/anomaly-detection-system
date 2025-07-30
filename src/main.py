"""
Main Application Entry Point

Real-Time Anomaly Detection System
"""

import os
import sys
import asyncio
import structlog
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent))

from anomaly_detector import AnomalyDetector
from api import app, anomaly_detector

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def create_sample_data():
    """Create sample data for training"""
    import pandas as pd
    import numpy as np
    
    # Generate normal data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Normal data
    normal_data = np.random.randn(n_samples, n_features)
    
    # Add some anomalies (5% of data)
    n_anomalies = int(n_samples * 0.05)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    
    for idx in anomaly_indices:
        # Add large deviations to create anomalies
        normal_data[idx] += np.random.choice([-3, 3], n_features)
    
    # Create DataFrame
    feature_names = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(normal_data, columns=feature_names)
    
    return df

def train_models():
    """Train the anomaly detection models"""
    logger.info("Training anomaly detection models")
    
    try:
        # Create sample data
        training_data = create_sample_data()
        
        # Initialize and train detector
        detector = AnomalyDetector()
        metrics = detector.train(training_data)
        
        # Save models
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        detector.save_models(str(models_dir))
        
        logger.info("Models trained and saved successfully", metrics=metrics)
        return detector
        
    except Exception as e:
        logger.error("Error training models", error=str(e))
        raise

def main():
    """Main application entry point"""
    logger.info("Starting Real-Time Anomaly Detection System")
    
    try:
        # Train models
        detector = train_models()
        
        # Set global detector for API
        import api
        api.anomaly_detector = detector
        
        # Start API server
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        
        logger.info("Starting API server", host=host, port=port)
        
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 