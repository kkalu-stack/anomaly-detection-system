#!/usr/bin/env python3
"""
Startup Script for Real-Time Anomaly Detection System

This script starts the complete anomaly detection system with all components.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import tensorflow
        import sklearn
        import pandas
        import numpy
        import fastapi
        import uvicorn
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_system():
    """Start the anomaly detection system"""
    print("🚀 Starting Real-Time Anomaly Detection System")
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    print("\n📋 System Components:")
    print("   • Anomaly Detection Engine (TensorFlow, Scikit-learn)")
    print("   • Real-time Stream Processing (Kafka, Redis)")
    print("   • REST API (FastAPI)")
    print("   • Monitoring & Visualization (Prometheus, Grafana)")
    print("   • Data Storage (PostgreSQL, MongoDB)")
    
    print("\n🔄 Starting system...")
    
    try:
        # Start the main application
        print("   Starting anomaly detection API...")
        process = subprocess.Popen([
            sys.executable, "src/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for API to start
        print("   Waiting for API to start...")
        time.sleep(10)
        
        # Test API health
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is running successfully")
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  API health check failed: {e}")
        
        print("\n🌐 System URLs:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • API Health: http://localhost:8000/health")
        print("   • Grafana Dashboard: http://localhost:3000 (admin/admin)")
        print("   • Prometheus: http://localhost:9090")
        
        print("\n📊 Monitoring:")
        print("   • Kafka: localhost:9092")
        print("   • Redis: localhost:6379")
        print("   • PostgreSQL: localhost:5432")
        print("   • MongoDB: localhost:27017")
        
        print("\n🛠️  Testing:")
        print("   • Run tests: python test_system.py")
        print("   • Generate data: python data_generator.py")
        
        print("\n⏹️  Press Ctrl+C to stop the system")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            process.terminate()
            process.wait()
            print("✅ System stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        return False

def main():
    """Main entry point"""
    print("=" * 60)
    print("🔍 Real-Time Anomaly Detection System")
    print("=" * 60)
    
    success = start_system()
    
    if success:
        print("\n🎉 System started successfully!")
    else:
        print("\n❌ Failed to start system")
        sys.exit(1)

if __name__ == "__main__":
    main() 