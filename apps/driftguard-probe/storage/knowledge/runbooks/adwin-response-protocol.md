# ADWIN Drift Response Protocol

## Purpose
Standardized response protocol for ADWIN drift alarm events across all production models.

## Alarm Severity Mapping
| ADWIN Score | Severity | Response SLA | Owner |
|-------------|----------|-------------|-------|
| 0.10–0.15   | LOW      | 24 hours    | Model owner |
| 0.15–0.20   | MEDIUM   | 8 hours     | Model owner |
| 0.20–0.30   | HIGH     | 4 hours     | ML on-call |
| > 0.30      | CRITICAL | 1 hour      | ML on-call + Manager |

## Step 1: Triage (0–15 minutes)
1. Open the Probe investigation session linked in the alert
2. Review the timeline: which agents completed? What evidence was collected?
3. Check accuracy metrics dashboard for the last 24 hours
4. Determine: covariate drift only, or concept drift?

```bash
# Quick triage commands
curl http://localhost:8002/api/v1/investigations/{session_id}/evidence
curl http://localhost:8002/api/v1/investigations/{session_id}/hypotheses
```

## Step 2: Classify the Drift
**Covariate drift only** (P(X) changed, P(Y|X) stable):
- Accuracy metrics are stable or degraded < 2%
- Action: Monitor. Schedule retrain for next sprint. No rollback.

**Concept drift** (P(Y|X) changed):
- Accuracy metrics dropped > 3%
- Action: Immediate retrain preparation. Rollback assessment.

**Data pipeline failure** (not model drift):
- Multiple unrelated features drift simultaneously
- ADWIN fires on features with historically zero drift (e.g., `user_id`, `timestamp`)
- Action: Escalate to Data Engineering. No model action.

## Step 3: Escalation Decision
```
ADWIN score > 0.20 AND accuracy drop > 3%?
  ├─ YES → Go to Rollback Runbook
  └─ NO
       ├─ Multiple unrelated features? → Data pipeline issue. Escalate Data Eng.
       └─ Single feature? → Fix upstream. Monitor for 2 hours.
```

## Step 4: Communication Template
Post to #mlops-incident-response:

```
[DRIFT INCIDENT] Model: {model_id} | ADWIN: {score} | Severity: {HIGH/CRITICAL}
Investigation: http://localhost:3000/investigations/{session_id}
Status: [INVESTIGATING | ROLLING BACK | RETRAINING]
ETA to resolution: {time}
Assigned to: {name}
```

## Step 5: Resolution and Post-Mortem
- Once resolved, update the Probe investigation status
- Write a 5-line post-mortem: What happened? Why? What changed? What's the fix? How to prevent?
- Add findings to the DriftGuard knowledge base for future reference

## Related
- [Retrain Decision Tree](retrain-decision-tree.md)
- [Rollback Production Model](rollback-production-model.md)
