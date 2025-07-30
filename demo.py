"""
Simple Demo for Anomaly Detection System
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import random
import time
from datetime import datetime
import json

app = FastAPI(
    title="Real-Time Anomaly Detection System",
    description="A revolutionary real-time anomaly detection platform",
    version="1.0.0"
)

# Simulated data
anomaly_data = {
    "total_events": 0,
    "anomalies_detected": 0,
    "processing_rate": 0,
    "accuracy": 95.2,
    "latency_ms": 45
}

@app.get("/")
async def root():
    return {"message": "Real-Time Anomaly Detection System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats")
async def get_stats():
    # Simulate real-time data
    anomaly_data["total_events"] += random.randint(10, 50)
    anomaly_data["anomalies_detected"] += random.randint(0, 3)
    anomaly_data["processing_rate"] = random.randint(800, 1200)
    anomaly_data["latency_ms"] = random.randint(30, 80)
    
    return {
        "metrics": anomaly_data,
        "timestamp": datetime.now().isoformat(),
        "system_status": "operational"
    }

@app.get("/api/anomalies")
async def get_recent_anomalies():
    # Simulate recent anomalies
    anomalies = []
    for i in range(random.randint(1, 5)):
        anomalies.append({
            "id": f"anomaly_{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "severity": random.choice(["low", "medium", "high"]),
            "type": random.choice(["fraud", "quality", "security", "performance"]),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "description": f"Anomaly detected in {random.choice(['financial', 'manufacturing', 'healthcare', 'telecom'])} data"
        })
    
    return {"anomalies": anomalies, "count": len(anomalies)}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Anomaly Detection Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #222; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat-value { font-size: 2em; font-weight: bold; color: #222; }
            .stat-label { color: #666; margin-top: 5px; }
            .anomalies-list { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .anomaly-item { border-left: 4px solid #ff6b35; padding: 10px; margin: 10px 0; background: #f9f9f9; }
            .high { border-left-color: #ff4444; }
            .medium { border-left-color: #ff8800; }
            .low { border-left-color: #ffbb33; }
            .refresh-btn { background: #222; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .refresh-btn:hover { background: #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Real-Time Anomaly Detection Dashboard</h1>
                <p>Live monitoring of anomaly detection system</p>
            </div>
            
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Data</button>
            
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-events">0</div>
                    <div class="stat-label">Total Events Processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="anomalies">0</div>
                    <div class="stat-label">Anomalies Detected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="processing-rate">0</div>
                    <div class="stat-label">Events/Second</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="accuracy">95.2%</div>
                    <div class="stat-label">Detection Accuracy</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="latency">45ms</div>
                    <div class="stat-label">Average Latency</div>
                </div>
            </div>
            
            <div class="anomalies-list">
                <h2>Recent Anomalies</h2>
                <div id="anomalies-list">
                    <p>Loading recent anomalies...</p>
                </div>
            </div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    const statsResponse = await fetch('/api/stats');
                    const stats = await statsResponse.json();
                    
                    document.getElementById('total-events').textContent = stats.metrics.total_events.toLocaleString();
                    document.getElementById('anomalies').textContent = stats.metrics.anomalies_detected;
                    document.getElementById('processing-rate').textContent = stats.metrics.processing_rate.toLocaleString();
                    document.getElementById('accuracy').textContent = stats.metrics.accuracy + '%';
                    document.getElementById('latency').textContent = stats.metrics.latency_ms + 'ms';
                    
                    const anomaliesResponse = await fetch('/api/anomalies');
                    const anomalies = await anomaliesResponse.json();
                    
                    const anomaliesHtml = anomalies.anomalies.map(anomaly => `
                        <div class="anomaly-item ${anomaly.severity}">
                            <strong>${anomaly.type.toUpperCase()}</strong> - ${anomaly.description}
                            <br><small>Confidence: ${anomaly.confidence} | Severity: ${anomaly.severity}</small>
                        </div>
                    `).join('');
                    
                    document.getElementById('anomalies-list').innerHTML = anomaliesHtml || '<p>No recent anomalies detected.</p>';
                    
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            // Load data immediately and every 5 seconds
            loadData();
            setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting Real-Time Anomaly Detection System Demo...")
    print("📊 Dashboard available at: http://localhost:8000/dashboard")
    print("🔗 API available at: http://localhost:8000/docs")
    print("💚 Health check at: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 