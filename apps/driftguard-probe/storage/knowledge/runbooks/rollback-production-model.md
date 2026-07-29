# Rollback Production Model — Emergency Response Runbook

## Purpose
Step-by-step guide for rolling back a degraded production model to a previous stable version.

## When to Use This Runbook
- Model drift score > 0.30 AND accuracy drop > 5%
- P0/P1 incident raised by alerting system
- Probe investigation has recommended rollback action

## Do NOT Use This Runbook If
- Drift is confirmed covariate only (accuracy is stable) → Use monitoring runbook instead
- All model versions are drifted → Root cause is data pipeline, not model

## Pre-Rollback Checklist
- [ ] Confirm investigation session ID from Probe dashboard
- [ ] Identify the last known-good model version from model registry
- [ ] Confirm previous version metrics (AUC, F1) from last evaluation run
- [ ] Notify product team of potential prediction disruption

## Step 1: Identify Rollback Target
```bash
# List available versions
GET /api/models/{model_id}/versions

# Response includes: version_id, deployed_at, accuracy_at_deploy, current_drift_score
# Select the most recent version where drift_score < 0.15 at deploy time
```

## Step 2: Shadow Traffic Validation (5 minutes)
```bash
# Deploy previous version in shadow mode (receives traffic but does not serve)
POST /api/deployments/shadow
{
  "model_id": "{model_id}",
  "version_id": "{target_version}",
  "shadow_duration_minutes": 5
}

# Compare shadow predictions vs current model predictions
# Acceptable divergence: < 3% on key segments
```

## Step 3: Execute Rollback
```bash
# Switch 100% traffic to previous version
POST /api/deployments/rollback
{
  "model_id": "{model_id}",
  "target_version_id": "{target_version}",
  "reason": "drift_incident",
  "investigation_id": "{session_id}"
}
```

## Step 4: Post-Rollback Verification
```bash
# Monitor ADWIN score on rolled-back version
# Expected: ADWIN score should fall below 0.15 within 10 minutes

# If ADWIN score remains high:
# → Root cause is data pipeline, not model version
# → Escalate to Data Engineering immediately
```

## Step 5: Open Retrain Ticket
A rollback is not a fix — it is a temporary recovery measure.
- Open a retrain ticket immediately after rollback is confirmed stable
- Reference the Probe investigation session ID in the ticket
- Set priority based on drift severity: HIGH → P2, CRITICAL → P1
- Target retrain completion: within 24 hours (P2) or 4 hours (P1)

## Rollback SLA
| Step | Target Time |
|------|-------------|
| Detect → Decision | ≤ 15 min |
| Decision → Shadow | ≤ 5 min |
| Shadow → Traffic Switch | ≤ 10 min |
| **Total TTR** | **≤ 30 min** |

## Escalation
- Rollback fails: page ML Platform on-call (#mlops-oncall)
- All versions drifted: page Data Engineering on-call
- Business impact confirmed: notify Product and VP Engineering

## Related
- [Retrain Decision Tree](retrain-decision-tree.md)
- [ADWIN Response Protocol](adwin-response-protocol.md)
