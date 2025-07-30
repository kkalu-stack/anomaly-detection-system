"""
FastAPI Web Service for Anomaly Detection System
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import structlog

from .anomaly_detector import AnomalyDetector, AnomalyResult

logger = structlog.get_logger()

# Pydantic models
class DetectionRequest(BaseModel):
    data: Dict[str, float]
    model_name: Optional[str] = "ensemble"

class DetectionResponse(BaseModel):
    id: str
    timestamp: datetime
    is_anomaly: bool
    confidence: float
    score: float
    model_used: str
    features: Dict[str, float]
    message: str

# Global variables
anomaly_detector: Optional[AnomalyDetector] = None

# Create FastAPI app
app = FastAPI(
    title="Real-Time Anomaly Detection API",
    description="API for real-time anomaly detection",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Real-Time Anomaly Detection API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": anomaly_detector.is_trained if anomaly_detector else False
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_anomaly(request: DetectionRequest):
    if not anomaly_detector or not anomaly_detector.is_trained:
        raise HTTPException(status_code=503, detail="Models not trained")
    
    try:
        result = anomaly_detector.detect_anomaly(
            data_point=request.data,
            model_name=request.model_name
        )
        
        response = DetectionResponse(
            id=result.timestamp.strftime("%Y%m%d_%H%M%S_%f"),
            timestamp=result.timestamp,
            is_anomaly=result.is_anomaly,
            confidence=result.confidence,
            score=result.score,
            model_used=result.model_used,
            features=result.features,
            message=f"Anomaly detected with {result.confidence:.2f} confidence" if result.is_anomaly else "No anomaly detected"
        )
        
        return response
        
    except Exception as e:
        logger.error("Error in anomaly detection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_models(data: List[Dict[str, float]]):
    global anomaly_detector
    
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        
        if not anomaly_detector:
            anomaly_detector = AnomalyDetector()
        
        metrics = anomaly_detector.train(df)
        
        return {
            "message": "Models trained successfully",
            "data_points": len(data),
            "features": len(data[0]) if data else 0
        }
        
    except Exception as e:
        logger.error("Error in model training", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
async def get_model_status():
    if not anomaly_detector:
        raise HTTPException(status_code=503, detail="Anomaly detector not initialized")
    
    return {
        "is_trained": anomaly_detector.is_trained,
        "available_models": list(anomaly_detector.models.keys()) if anomaly_detector.is_trained else []
    } 