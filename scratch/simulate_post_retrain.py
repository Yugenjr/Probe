import random
import time
import requests

from driftguard import DriftGuard

API_KEY = "dg-353460f1c15b79329e7b2023e3e7c19a"
MODEL_ID = "credit-risk-e2e"
API_URL = "http://localhost:8000"

print(f"1. Connecting to DriftGuard SDK for model: {MODEL_ID}")
dg = DriftGuard(
    model_id=MODEL_ID,
    api_key=API_KEY,
    api_url=API_URL
)

class MockModelV2:
    def __init__(self):
        self.features = ['income', 'credit_score', 'debt_ratio', 'loan_amount', 'age']
        self.version = '1.0.1'  # The newly promoted version
        
    def predict(self, X):
        return [random.choice([0, 1]) for _ in X]
        
    def predict_proba(self, X):
        return [[random.random(), random.random()] for _ in X]

print("2. Wrapping updated model (v1.0.1)...")
mock_model = MockModelV2()
wrapped_model = dg.wrap(mock_model)

print("3. Sending healthy telemetry to show drift score dropping back to normal...")
for i in range(40):
    # Sending normal baseline data so ADWIN drift score drops
    X = [[random.uniform(30000, 120000), random.uniform(600, 850), random.uniform(0.1, 0.4), random.uniform(5000, 50000), random.uniform(25, 65)] for _ in range(5)]
    wrapped_model.predict(X)
    time.sleep(0.05)

print("Healthy predictions sent! Check the Drift Chart to see the score plummet back down!")
