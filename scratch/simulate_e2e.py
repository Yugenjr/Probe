import os
import random
import time
import requests
import sys

from driftguard import DriftGuard

API_KEY = "dg-353460f1c15b79329e7b2023e3e7c19a"
MODEL_ID = "credit-risk-e2e"
API_URL = "http://localhost:8000"
WEBHOOK_URL = "http://localhost:8006/api/v1/webhooks"

print(f"1. Initializing DriftGuard SDK for new model: {MODEL_ID}")
dg = DriftGuard(
    model_id=MODEL_ID,
    api_key=API_KEY,
    api_url=API_URL
)

class MockModel:
    def __init__(self):
        self.features = ['income', 'credit_score', 'debt_ratio', 'loan_amount', 'age']
        self.version = '1.0.0'
        
    def predict(self, X):
        return [random.choice([0, 1]) for _ in X]
        
    def predict_proba(self, X):
        return [[random.random(), random.random()] for _ in X]

print("2. Wrapping model...")
mock_model = MockModel()
wrapped_model = dg.wrap(mock_model)

print("3. Updating Webhook URL via API...")
try:
    response = requests.put(
        f"{API_URL}/models/{MODEL_ID}/webhook",
        json={"webhook_url": WEBHOOK_URL},
        headers={"X-API-Key": API_KEY}
    )
    if response.status_code == 200:
        print(f"Webhook configured to: {WEBHOOK_URL}")
    else:
        print(f"Failed to configure webhook: {response.text}")
except Exception as e:
    print(f"API error: {e}")

print("4. Sending normal telemetry (Healthy state)...")
for i in range(30):
    X = [[random.uniform(30000, 120000), random.uniform(600, 850), random.uniform(0.1, 0.4), random.uniform(5000, 50000), random.uniform(25, 65)] for _ in range(5)]
    wrapped_model.predict(X)
    time.sleep(0.05)
    
print("Normal predictions sent. Sleeping 2 seconds...")
time.sleep(2)

print("5. Sending drifted telemetry (SLA Breach)...")
for i in range(20):
    X = [[random.uniform(-100, -10), random.uniform(100000, 200000), random.uniform(10, 50), random.uniform(-5000, 0), random.uniform(-50, 0)] for _ in range(5)]
    wrapped_model.predict(X)
    time.sleep(0.05)

print("Drift predictions sent! Waiting 5 seconds for backend to trigger retraining event...")
time.sleep(5)

print("6. Simulating external ML pipeline finishing the retraining...")
payload = {
    "validation_passed": True,
    "new_version": "1.0.1",
    "new_accuracy": 0.97,
    "old_accuracy": 0.85,
    "error_message": None
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(f"{API_URL}/retrain/{MODEL_ID}/complete", json=payload, headers=headers)
print(f"Callback Status: {response.status_code}")
print(f"Callback Response: {response.json()}")

print("End-to-End Simulation Complete!")
