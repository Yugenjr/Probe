import os
import sys
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from driftguard import DriftGuard

API_KEY = "dg-353460f1c15b79329e7b2023e3e7c19a"
MODEL_NAMES = [
    "credit-risk-model-v2",
    "fraud-detection-ensemble",
    "churn-prediction-xgb",
    "recommendation-engine-dnn",
    "pricing-optimizer-rf",
    "supply-chain-forecaster",
    "anomaly-detector-isoforest"
]

def main():
    print("--- Registering 7 Models ---")
    
    # Create simple dataset and model
    X, y = make_classification(n_samples=50, n_features=5, random_state=42)
    base_model = LogisticRegression()
    base_model.fit(X, y)
    
    for model_name in MODEL_NAMES:
        print(f"Initializing {model_name}...")
        dg = DriftGuard(
            model_id=model_name,
            api_key=API_KEY,
            api_url="http://localhost:8000",
            drift_threshold=0.15,
            auto_retrain=False
        )
        
        wrapped_model = dg.wrap(base_model)
        
        # Send 5 predictions
        for _ in range(5):
            sample_input = np.random.normal(0, 1, (1, 5))
            _ = wrapped_model.predict(sample_input)
            
        print(f"Logged metrics for {model_name}.")
        
    print("All models successfully logged!")

if __name__ == "__main__":
    main()
