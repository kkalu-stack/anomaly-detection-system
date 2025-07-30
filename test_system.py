#!/usr/bin/env python3
"""
Test Script for Anomaly Detection System

Tests the complete anomaly detection pipeline.
"""

import requests
import json
import time
import numpy as np
from datetime import datetime

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_model_training():
    """Test model training"""
    try:
        # Generate training data
        training_data = []
        for i in range(100):
            features = {f'feature_{j}': float(np.random.randn()) for j in range(10)}
            training_data.append(features)
        
        response = requests.post("http://localhost:8000/train", json=training_data)
        print(f"✅ Model training: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        return False

def test_anomaly_detection():
    """Test anomaly detection"""
    try:
        # Test normal data
        normal_data = {f'feature_{i}': float(np.random.randn()) for i in range(10)}
        response = requests.post("http://localhost:8000/detect", json={
            "data": normal_data,
            "model_name": "ensemble"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Normal data detection: {result['is_anomaly']}")
        else:
            print(f"❌ Normal data detection failed: {response.status_code}")
            return False
        
        # Test anomaly data
        anomaly_data = {f'feature_{i}': float(np.random.randn() * 5) for i in range(10)}
        response = requests.post("http://localhost:8000/detect", json={
            "data": anomaly_data,
            "model_name": "ensemble"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Anomaly data detection: {result['is_anomaly']}")
        else:
            print(f"❌ Anomaly data detection failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Anomaly detection test failed: {e}")
        return False

def test_batch_detection():
    """Test batch anomaly detection"""
    try:
        # Generate batch data
        batch_data = []
        for i in range(10):
            features = {f'feature_{j}': float(np.random.randn()) for j in range(10)}
            batch_data.append(features)
        
        response = requests.post("http://localhost:8000/detect/batch", json=batch_data)
        
        if response.status_code == 200:
            results = response.json()
            anomalies = sum(1 for r in results if r['is_anomaly'])
            print(f"✅ Batch detection: {len(results)} processed, {anomalies} anomalies")
            return True
        else:
            print(f"❌ Batch detection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch detection test failed: {e}")
        return False

def test_model_status():
    """Test model status endpoint"""
    try:
        response = requests.get("http://localhost:8000/models/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Model status: {status['is_trained']}")
            return status['is_trained']
        else:
            print(f"❌ Model status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model status test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Anomaly Detection System Tests")
    print("=" * 50)
    
    tests = [
        ("API Health", test_api_health),
        ("Model Training", test_model_training),
        ("Model Status", test_model_status),
        ("Anomaly Detection", test_anomaly_detection),
        ("Batch Detection", test_batch_detection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the system.")
    
    return passed == total

if __name__ == "__main__":
    main() 