"""
Enhanced Demo for Anomaly Detection System
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import random
import time
from datetime import datetime, timedelta
import json

app = FastAPI(
    title="Real-Time Anomaly Detection System",
    description="A revolutionary real-time anomaly detection platform",
    version="1.0.0"
)

# Simulated data with more realistic patterns
anomaly_data = {
    "total_events": 0,
    "anomalies_detected": 0,
    "processing_rate": 0,
    "accuracy": 95.2,
    "latency_ms": 45,
    "uptime_hours": 0,
    "active_models": 3,
    "data_sources": 4
}

@app.get("/")
async def root():
    return {"message": "Real-Time Anomaly Detection System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats")
async def get_stats():
    # Simulate real-time data with more realistic patterns
    anomaly_data["total_events"] += random.randint(50, 200)
    anomaly_data["anomalies_detected"] += random.randint(0, 5)
    anomaly_data["processing_rate"] = random.randint(800, 1500)
    anomaly_data["latency_ms"] = random.randint(25, 120)
    anomaly_data["uptime_hours"] += 0.1
    
    return {
        "metrics": anomaly_data,
        "timestamp": datetime.now().isoformat(),
        "system_status": "operational"
    }

@app.get("/api/anomalies")
async def get_recent_anomalies():
    # Generate more realistic anomalies
    anomaly_types = [
        {"type": "FRAUD", "description": "Suspicious transaction pattern detected", "severity": "high"},
        {"type": "QUALITY", "description": "Manufacturing defect identified", "severity": "medium"},
        {"type": "SECURITY", "description": "Unauthorized access attempt", "severity": "high"},
        {"type": "PERFORMANCE", "description": "System performance degradation", "severity": "low"},
        {"type": "NETWORK", "description": "Unusual network traffic pattern", "severity": "medium"}
    ]
    
    industries = ["financial", "manufacturing", "healthcare", "telecom", "retail", "energy"]
    
    anomalies = []
    for i in range(random.randint(2, 6)):
        anomaly_type = random.choice(anomaly_types)
        anomalies.append({
            "id": f"anomaly_{random.randint(10000, 99999)}",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "severity": anomaly_type["severity"],
            "type": anomaly_type["type"],
            "confidence": round(random.uniform(0.75, 0.98), 2),
            "description": f"{anomaly_type['description']} in {random.choice(industries)} data",
            "source": random.choice(["API Gateway", "Database", "Message Queue", "External Service"]),
            "location": random.choice(["US-East", "US-West", "EU-Central", "Asia-Pacific"])
        })
    
    return {"anomalies": anomalies, "count": len(anomalies)}

@app.get("/api/performance")
async def get_performance_data():
    # Generate performance metrics for charts
    hours = 24
    performance_data = []
    
    for i in range(hours):
        timestamp = datetime.now() - timedelta(hours=hours-i-1)
        performance_data.append({
            "timestamp": timestamp.isoformat(),
            "events_per_second": random.randint(800, 1500),
            "latency_ms": random.randint(25, 120),
            "anomalies": random.randint(0, 8),
            "accuracy": round(random.uniform(94.0, 97.0), 1)
        })
    
    return {"performance": performance_data}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Anomaly Detection Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                color: #333;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 20px 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header h1 {
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .header p {
                color: #7f8c8d;
                font-size: 1.1rem;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #27ae60;
                border-radius: 50%;
                margin-left: 10px;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .controls {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .filters-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 30px;
            }
            
            .filters-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                align-items: end;
            }
            
            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .filter-group label {
                font-weight: 600;
                color: #2c3e50;
                font-size: 0.9rem;
            }
            
            .filter-select {
                padding: 10px 12px;
                border: 2px solid #e0e6ed;
                border-radius: 8px;
                background: white;
                color: #2c3e50;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .filter-select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
                margin-top: 20px;
            }
            
            .btn {
                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 15px;
            }
            
            .stat-icon {
                width: 50px;
                height: 50px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                color: white;
            }
            
            .stat-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #7f8c8d;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .stat-trend {
                font-size: 0.8rem;
                margin-top: 5px;
            }
            
            .trend-up { color: #27ae60; }
            .trend-down { color: #e74c3c; }
            
            .charts-section {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 25px;
                margin-bottom: 30px;
            }
            
            .chart-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                height: 400px;
                display: flex;
                flex-direction: column;
            }
            
            .chart-card canvas {
                flex: 1;
                max-height: 300px;
            }
            
            .chart-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 20px;
            }
            
            .anomalies-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .anomalies-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .anomalies-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .anomaly-item {
                border-left: 4px solid #e74c3c;
                padding: 15px;
                margin: 15px 0;
                background: rgba(231, 76, 60, 0.05);
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .anomaly-item:hover {
                background: rgba(231, 76, 60, 0.1);
                transform: translateX(5px);
            }
            
            .anomaly-item.high { border-left-color: #e74c3c; }
            .anomaly-item.medium { border-left-color: #f39c12; }
            .anomaly-item.low { border-left-color: #f1c40f; }
            
            .anomaly-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .anomaly-type {
                font-weight: bold;
                color: #2c3e50;
            }
            
            .anomaly-severity {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .severity-high { background: #d32f2f; color: white; }
            .severity-medium { background: #f57c00; color: white; }
            .severity-low { background: #388e3c; color: white; }
            
            .anomaly-details {
                color: #7f8c8d;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .anomaly-meta {
                display: flex;
                gap: 15px;
                margin-top: 8px;
                font-size: 0.8rem;
                color: #95a5a6;
            }
            
            /* Mobile-first responsive design */
            @media (max-width: 1200px) {
                .charts-section {
                    grid-template-columns: 1fr;
                }
                
                .chart-card {
                    height: auto;
                    min-height: 350px;
                }
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 15px;
                }
                
                .header {
                    padding: 15px 20px;
                    margin-bottom: 20px;
                }
                
                .header h1 {
                    font-size: 1.8rem;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .header p {
                    font-size: 1rem;
                }
                
                .controls {
                    flex-direction: column;
                    gap: 10px;
                }
                
                .btn {
                    padding: 10px 20px;
                    font-size: 0.9rem;
                }
                
                .filters-section {
                    padding: 20px;
                }
                
                .filters-grid {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                
                .filter-select {
                    padding: 12px;
                    font-size: 1rem;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                    gap: 20px;
                }
                
                .stat-card {
                    padding: 20px;
                }
                
                .stat-value {
                    font-size: 2rem;
                }
                
                .chart-card {
                    padding: 20px;
                    height: auto;
                    min-height: 300px;
                }
                
                .chart-title {
                    font-size: 1.1rem;
                }
                
                .anomalies-section {
                    padding: 20px;
                }
                
                .anomalies-title {
                    font-size: 1.1rem;
                }
                
                .anomaly-item {
                    padding: 12px;
                    margin: 10px 0;
                }
                
                .anomaly-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
                
                .anomaly-meta {
                    flex-direction: column;
                    gap: 5px;
                }
            }
            
            @media (max-width: 480px) {
                .container {
                    padding: 10px;
                }
                
                .header {
                    padding: 15px;
                }
                
                .header h1 {
                    font-size: 1.5rem;
                }
                
                .header p {
                    font-size: 0.9rem;
                }
                
                .filters-section {
                    padding: 15px;
                }
                
                .filter-select {
                    padding: 10px;
                }
                
                .stat-card {
                    padding: 15px;
                }
                
                .stat-value {
                    font-size: 1.8rem;
                }
                
                .chart-card {
                    padding: 15px;
                    min-height: 250px;
                }
                
                .anomalies-section {
                    padding: 15px;
                }
                
                .anomaly-item {
                    padding: 10px;
                }
                
                .anomaly-details {
                    font-size: 0.85rem;
                }
                
                .anomaly-meta {
                    font-size: 0.75rem;
                }
            }
            
            /* iPhone-specific optimizations */
            @media (max-width: 375px) {
                .header h1 {
                    font-size: 1.3rem;
                }
                
                .stat-value {
                    font-size: 1.6rem;
                }
                
                .btn {
                    padding: 8px 16px;
                    font-size: 0.85rem;
                }
                
                .filter-select {
                    padding: 8px;
                    font-size: 0.9rem;
                }
            }
            
            /* Landscape orientation for mobile */
            @media (max-width: 768px) and (orientation: landscape) {
                .header h1 {
                    font-size: 1.6rem;
                }
                
                .stats-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .charts-section {
                    grid-template-columns: 1fr 1fr;
                }
            }
            
            /* Touch-friendly improvements */
            @media (hover: none) and (pointer: coarse) {
                .btn {
                    min-height: 44px;
                }
                
                .filter-select {
                    min-height: 44px;
                }
                
                .anomaly-item {
                    min-height: 60px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>
                    Real-Time Anomaly Detection Dashboard
                    <span class="status-indicator"></span>
                </h1>
                <p>Live monitoring of enterprise anomaly detection system across multiple industries</p>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="location.reload()">Refresh Dashboard</button>
                <button class="btn" onclick="window.open('/docs', '_blank')">API Documentation</button>
                <button class="btn" onclick="window.open('/health', '_blank')">Health Check</button>
            </div>
            
            <div class="filters-section">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Dashboard Filters</h3>
                <div class="filters-grid">
                    <div class="filter-group">
                        <label for="timeRange">Time Range:</label>
                        <select id="timeRange" class="filter-select" onchange="applyFilters()">
                            <option value="1h">Last Hour</option>
                            <option value="24h" selected>Last 24 Hours</option>
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="anomalyType">Anomaly Type:</label>
                        <select id="anomalyType" class="filter-select" onchange="applyFilters()">
                            <option value="all" selected>All Types</option>
                            <option value="FRAUD">Fraud</option>
                            <option value="QUALITY">Quality</option>
                            <option value="SECURITY">Security</option>
                            <option value="PERFORMANCE">Performance</option>
                            <option value="NETWORK">Network</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="severity">Severity:</label>
                        <select id="severity" class="filter-select" onchange="applyFilters()">
                            <option value="all" selected>All Severities</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="industry">Industry:</label>
                        <select id="industry" class="filter-select" onchange="applyFilters()">
                            <option value="all" selected>All Industries</option>
                            <option value="financial">Financial</option>
                            <option value="manufacturing">Manufacturing</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="energy">Energy</option>
                            <option value="telecom">Telecom</option>
                            <option value="retail">Retail</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="location">Location:</label>
                        <select id="location" class="filter-select" onchange="applyFilters()">
                            <option value="all" selected>All Locations</option>
                            <option value="US-East">US-East</option>
                            <option value="US-West">US-West</option>
                            <option value="EU-Central">EU-Central</option>
                            <option value="Asia-Pacific">Asia-Pacific</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <button class="btn btn-secondary" onclick="clearFilters()">Clear Filters</button>
                    </div>
                </div>
            </div>
            
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="total-events">0</div>
                            <div class="stat-label">Total Events Processed</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-up">↑ +12.5% from last hour</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="anomalies">0</div>
                            <div class="stat-label">Anomalies Detected</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-up">↑ +3 new in last 5 min</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="processing-rate">0</div>
                            <div class="stat-label">Events/Second</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-up">↑ +8.2% from baseline</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="accuracy">95.2%</div>
                            <div class="stat-label">Detection Accuracy</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-up">↑ +0.3% improvement</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="latency">45ms</div>
                            <div class="stat-label">Average Latency</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-down">↓ -12ms improvement</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <div>
                            <div class="stat-value" id="uptime">0h</div>
                            <div class="stat-label">System Uptime</div>
                        </div>
                    </div>
                    <div class="stat-trend trend-up">↑ 99.9% availability</div>
                </div>
            </div>
            
            <div class="charts-section">
                <div class="chart-card">
                    <div class="chart-title">Performance Metrics (24h)</div>
                    <canvas id="performanceChart" width="400" height="200"></canvas>
                </div>
                
                <div class="chart-card">
                    <div class="chart-title">Anomaly Distribution by Type</div>
                    <canvas id="anomalyChart" width="400" height="200"></canvas>
                </div>
            </div>
            
            <div class="anomalies-section">
                <div class="anomalies-header">
                    <div class="anomalies-title">Recent Anomalies</div>
                    <div style="color: #7f8c8d; font-size: 0.9rem;">Auto-refresh every 5s</div>
                </div>
                <div id="anomalies-list">
                    <p style="color: #7f8c8d; text-align: center; padding: 20px;">Loading recent anomalies...</p>
                </div>
            </div>
        </div>
        
        <script>
            let performanceChart, anomalyChart;
            let currentAnomalies = [];
            let activeFilters = {
                timeRange: '24h',
                anomalyType: 'all',
                severity: 'all',
                industry: 'all',
                location: 'all'
            };
            
            async function loadData() {
                try {
                    // Load stats
                    const statsResponse = await fetch('/api/stats');
                    const stats = await statsResponse.json();
                    
                    document.getElementById('total-events').textContent = stats.metrics.total_events.toLocaleString();
                    document.getElementById('anomalies').textContent = stats.metrics.anomalies_detected;
                    document.getElementById('processing-rate').textContent = stats.metrics.processing_rate.toLocaleString();
                    document.getElementById('accuracy').textContent = stats.metrics.accuracy + '%';
                    document.getElementById('latency').textContent = stats.metrics.latency_ms + 'ms';
                    document.getElementById('uptime').textContent = Math.floor(stats.metrics.uptime_hours) + 'h';
                    
                    // Load anomalies
                    const anomaliesResponse = await fetch('/api/anomalies');
                    const anomalies = await anomaliesResponse.json();
                    
                    // Store current anomalies for filtering
                    currentAnomalies = anomalies.anomalies;
                    
                    // Apply current filters to new data
                    applyFiltersToData();
                    
                    // Load performance data for charts
                    const performanceResponse = await fetch('/api/performance');
                    const performance = await performanceResponse.json();
                    
                    updateCharts(performance.performance, anomalies.anomalies);
                    
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            function updateCharts(performanceData, anomaliesData) {
                const ctx1 = document.getElementById('performanceChart').getContext('2d');
                const ctx2 = document.getElementById('anomalyChart').getContext('2d');
                
                // Performance Chart
                if (performanceChart) performanceChart.destroy();
                performanceChart = new Chart(ctx1, {
                    type: 'line',
                    data: {
                        labels: performanceData.map(d => new Date(d.timestamp).toLocaleTimeString()),
                        datasets: [{
                            label: 'Events/Second',
                            data: performanceData.map(d => d.events_per_second),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Latency (ms)',
                            data: performanceData.map(d => d.latency_ms),
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {
                            mode: 'index',
                            intersect: false,
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    boxWidth: 12,
                                    padding: 10,
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: {
                                    drawOnChartArea: false,
                                },
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            x: {
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            }
                        },
                    }
                });
                
                // Anomaly Distribution Chart
                const anomalyTypes = {};
                anomaliesData.forEach(a => {
                    anomalyTypes[a.type] = (anomalyTypes[a.type] || 0) + 1;
                });
                
                if (anomalyChart) anomalyChart.destroy();
                anomalyChart = new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(anomalyTypes),
                        datasets: [{
                            label: 'Anomaly Count',
                            data: Object.values(anomalyTypes),
                            backgroundColor: '#2196F3',
                            borderColor: '#1976D2',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(0,0,0,0.1)'
                                },
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    font: {
                                        size: window.innerWidth < 768 ? 10 : 12
                                    }
                                }
                            }
                        }
                    }
                });
            }
            
            // Filter functions
            
            function applyFilters() {
                // Store current filter values
                activeFilters.timeRange = document.getElementById('timeRange').value;
                activeFilters.anomalyType = document.getElementById('anomalyType').value;
                activeFilters.severity = document.getElementById('severity').value;
                activeFilters.industry = document.getElementById('industry').value;
                activeFilters.location = document.getElementById('location').value;
                
                console.log('Filters changed:', activeFilters);
                console.log('Current anomalies count:', currentAnomalies.length);
                
                // Apply filters to current data
                applyFiltersToData();
            }
            
            function applyFiltersToData() {
                let filteredAnomalies = currentAnomalies;
                
                console.log('Applying filters to', currentAnomalies.length, 'anomalies');
                console.log('Active filters:', activeFilters);
                
                if (activeFilters.anomalyType !== 'all') {
                    filteredAnomalies = filteredAnomalies.filter(a => a.type === activeFilters.anomalyType);
                    console.log('After type filter:', filteredAnomalies.length, 'anomalies');
                }
                
                if (activeFilters.severity !== 'all') {
                    filteredAnomalies = filteredAnomalies.filter(a => a.severity === activeFilters.severity);
                    console.log('After severity filter:', filteredAnomalies.length, 'anomalies');
                }
                
                if (activeFilters.location !== 'all') {
                    filteredAnomalies = filteredAnomalies.filter(a => a.location === activeFilters.location);
                    console.log('After location filter:', filteredAnomalies.length, 'anomalies');
                }
                
                // Update the display with filtered results
                displayAnomalies(filteredAnomalies);
                
                // Show filter status
                const activeFilterList = Object.values(activeFilters).filter(f => f !== 'all').join(', ');
                if (activeFilterList) {
                    console.log('Applied filters:', activeFilterList);
                }
            }
            
            function clearFilters() {
                document.getElementById('timeRange').value = '24h';
                document.getElementById('anomalyType').value = 'all';
                document.getElementById('severity').value = 'all';
                document.getElementById('industry').value = 'all';
                document.getElementById('location').value = 'all';
                
                // Reset active filters
                activeFilters = {
                    timeRange: '24h',
                    anomalyType: 'all',
                    severity: 'all',
                    industry: 'all',
                    location: 'all'
                };
                
                // Show all anomalies
                displayAnomalies(currentAnomalies);
                console.log('Filters cleared');
            }
            
            function displayAnomalies(anomalies) {
                const anomaliesHtml = anomalies.map(anomaly => `
                    <div class="anomaly-item ${anomaly.severity}">
                        <div class="anomaly-header">
                            <div class="anomaly-type">${anomaly.type}</div>
                            <div class="anomaly-severity severity-${anomaly.severity}">${anomaly.severity}</div>
                        </div>
                        <div class="anomaly-details">${anomaly.description}</div>
                        <div class="anomaly-meta">
                            <span>Confidence: ${anomaly.confidence}</span>
                            <span>Source: ${anomaly.source}</span>
                            <span>Location: ${anomaly.location}</span>
                            <span>${new Date(anomaly.timestamp).toLocaleTimeString()}</span>
                        </div>
                    </div>
                `).join('');
                
                document.getElementById('anomalies-list').innerHTML = anomaliesHtml || '<p style="color: #7f8c8d; text-align: center; padding: 20px;">No anomalies match the selected filters.</p>';
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
    import os
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Real-Time Anomaly Detection System Demo...")
    print(f"📊 Dashboard available at: http://localhost:{port}/dashboard")
    print(f"🔗 API available at: http://localhost:{port}/docs")
    print(f"💚 Health check at: http://localhost:{port}/health")
    
    uvicorn.run(app, host="0.0.0.0", port=port) 