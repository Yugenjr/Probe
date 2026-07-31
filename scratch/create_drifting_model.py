import os
import random
import time
import requests
import json

from driftguard import DriftGuard

# Configuration
API_KEY = "dg-353460f1c15b79329e7b2023e3e7c19a"
MODEL_ID = "credit-risk-v1"
API_URL = "http://localhost:8000"
WEBHOOK_URL = "http://localhost:8006/api/v1/webhooks"

print("1. Initializing DriftGuard SDK...")
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

# Connect via API to update webhook URL
print("3. Updating Webhook URL via API...")
try:
    response = requests.put(
        f"{API_URL}/models/{MODEL_ID}/webhook",
        json={"webhook_url": WEBHOOK_URL},
        headers={"X-API-Key": API_KEY}
    )
    if response.status_code == 200:
        print(f"✅ Webhook configured to: {WEBHOOK_URL}")
    else:
        print(f"Failed to configure webhook: {response.text}")
except Exception as e:
    print(f"API error: {e}")

print("4. Sending normal telemetry (Healthy state)...")
for i in range(30):
    X = [[random.uniform(30000, 120000), random.uniform(600, 850), random.uniform(0.1, 0.4), random.uniform(5000, 50000), random.uniform(25, 65)] for _ in range(5)]
    wrapped_model.predict(X)
    time.sleep(0.1)
    
print("Normal predictions sent. Sleeping 3 seconds...")
time.sleep(3)

print("5. Sending drifted telemetry (SLA Breach)...")
# Send drifted data to trigger the SLA threshold (which defaults to something like 0.15)
# We need to simulate severe drift. We'll pass extreme out-of-distribution values.
for i in range(20):
    # Age is suddenly negative, credit scores are in the millions, debt ratio is massive
    X = [[random.uniform(-100, -10), random.uniform(100000, 200000), random.uniform(10, 50), random.uniform(-5000, 0), random.uniform(-50, 0)] for _ in range(5)]
    wrapped_model.predict(X)
    time.sleep(0.1)

print("Drift predictions sent! Check the dashboard and the driftguard-probe logs.")
