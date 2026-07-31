import requests

API_KEY = "dg-353460f1c15b79329e7b2023e3e7c19a"
MODEL_ID = "credit-risk-v1"
API_URL = "http://localhost:8000"

payload = {
    "validation_passed": True,
    "new_version": "1.0.1",
    "new_accuracy": 0.965,
    "old_accuracy": 0.88,
    "error_message": None
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(f"{API_URL}/retrain/{MODEL_ID}/complete", json=payload, headers=headers)
print(response.status_code)
print(response.json())
