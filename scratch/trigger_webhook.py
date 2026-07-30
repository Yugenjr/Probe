import requests
import json
import time

webhook_url = "http://localhost:8005/api/v1/webhooks"

payloads = [
    {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "churn-prediction-xgb",
        "model_version": "v1.5",
        "drift_score": 0.55,
        "details": {"feature": "user_engagement_score", "description": "Gradual feature drift over 30 days"}
    },
    {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "recommendation-engine-dnn",
        "model_version": "v3.1",
        "drift_score": 0.61,
        "details": {"feature": "click_through_rate", "description": "Concept drift detected on new product categories"}
    },
    {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "pricing-optimizer-rf",
        "model_version": "v2.2",
        "drift_score": 0.49,
        "details": {"feature": "competitor_price", "description": "Sudden covariate shift"}
    },
    {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "supply-chain-forecaster",
        "model_version": "v1.0",
        "drift_score": 0.82,
        "details": {"feature": "lead_time_days", "description": "Massive target drift detected due to external macro events"}
    },
    {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "anomaly-detector-isoforest",
        "model_version": "v1.1",
        "drift_score": 0.38,
        "details": {"feature": "network_latency", "description": "Slight feature shift in underlying infrastructure"}
    }
]

for p in payloads:
    print(f"Triggering investigation for {p['model_id']}...")
    try:
        r = requests.post(webhook_url, json=p)
        print(r.status_code, r.text)
    except Exception as e:
        print("Error:", e)
    time.sleep(2)
