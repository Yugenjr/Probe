# Retrain Decision Tree — ML Model Retraining Runbook

## Purpose
This runbook guides the on-call ML engineer through the decision to retrain a production model following a drift incident.

## Prerequisites
- Access to model registry (MLflow / SageMaker / Vertex)
- Access to feature store or training data pipeline
- DriftGuard Probe investigation session ID

## Step 1: Confirm Drift is Real
Before triggering a retrain, verify the drift alarm is not a false positive:

```bash
# Check raw feature statistics
GET /api/v1/investigations/{session_id}/evidence

# Confirm ADWIN score > 0.20 on at least 2 features
# Confirm PSI > 0.15 on at least 1 feature
```

If only 1 feature drifted and it's a low-importance feature → **Do not retrain. Fix upstream data.**

## Step 2: Assess Accuracy Impact
```bash
# Compare current accuracy against baseline
GET /api/models/{model_id}/metrics?window=7d

# Thresholds for retrain decision:
# AUC drop > 3%  → Prepare retrain
# AUC drop > 7%  → Emergency retrain (SLA: 4 hours)
# AUC drop > 12% → Rollback immediately + retrain
```

## Step 3: Prepare Training Dataset
```bash
# Select training window: use past 90 days of production data
# Ensure labels are available for the full window
python scripts/prepare_training_data.py \
  --model-id {model_id} \
  --window-days 90 \
  --output-path data/retrain/{model_id}/

# Validate dataset size (minimum: 50,000 samples for churn models)
python scripts/validate_dataset.py --path data/retrain/{model_id}/
```

## Step 4: Trigger Retrain
```bash
# Via DriftGuard callback
curl -X POST http://localhost:8000/retrain/{model_id}/trigger \
  -H "Content-Type: application/json" \
  -d '{"reason": "drift_incident", "investigation_id": "{session_id}"}'
```

## Step 5: Validate New Model
- Run shadow evaluation on last 7 days of production traffic
- Compare new model AUC vs current model AUC
- New model must be ≥ current model accuracy before promotion

## Step 6: Promote and Monitor
- Promote new model version to production
- Monitor ADWIN for 60 minutes post-deploy
- Close Probe investigation session with outcome: `RETRAINED`

## Escalation
- If retrain fails twice: escalate to ML Platform team
- If data pipeline is the root cause: escalate to Data Engineering
- SLA for completion: 8 hours from alarm

## Related
- [ADWIN Response Protocol](adwin-response-protocol.md)
- [Rollback Production Model](rollback-production-model.md)
