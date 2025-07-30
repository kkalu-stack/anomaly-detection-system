#!/usr/bin/env python3
"""
Data Generator for Anomaly Detection System

Generates synthetic data for testing the anomaly detection system.
"""

import time
import json
import requests
import random
import numpy as np
from datetime import datetime

def generate_data():
    """Generate synthetic data point"""
    features = {f'feature_{i}': float(np.random.randn()) for i in range(10)}
    return {
        'id': f'msg_{int(time.time() * 1000)}',
        'timestamp': datetime.now().isoformat(),
        'data': features,
        'source': 'synthetic_generator',
        'metadata': {'is_anomaly': random.random() < 0.1}
    }

def main():
    """Main data generation loop"""
    print('Starting data generator...')
    
    while True:
        try:
            data = generate_data()
            response = requests.post('http://localhost:8000/detect', json=data)
            print(f'Generated data: {data["id"]}, Response: {response.status_code}')
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(5)

if __name__ == "__main__":
    main() 