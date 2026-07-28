import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InvestigationLoopAgent:
    def __init__(self):
        pass

    async def evaluate_iteration(
        self,
        previous_iterations: List[Dict[str, Any]],
        current_confidence: float,
        should_continue: bool
    ) -> Dict[str, Any]:
        """
        Evaluates the current investigation iteration cycle to decide on termination or continuation.
        """
        iteration_index = len(previous_iterations) + 1
        
        # Calculate confidence change trajectories
        if len(previous_iterations) > 0:
            last_iter = previous_iterations[-1]
            before_conf = last_iter.get("confidence_change", {}).get("after", 0.0)
        else:
            before_conf = 0.0
            
        after_conf = current_confidence

        # Terminating/state logic
        if current_confidence >= 0.85:
            status = "completed"
            reason = f"Investigation successful. Root cause confidence of {int(after_conf * 100)}% achieved target thresholds."
        elif iteration_index >= 3:
            status = "insufficient"
            reason = f"Investigation terminated. Maximum iteration limit of 3 reached with confidence of {int(after_conf * 100)}%."
        elif not should_continue:
            status = "completed"
            reason = "Investigation completed. No remaining evidence gaps identified by gap analyzer."
        else:
            status = "waiting_for_evidence"
            reason = f"Evidence gaps identified during iteration {iteration_index}. Awaiting additional diagnostic file uploads."

        return {
            "iteration": iteration_index,
            "status": status,
            "confidence_change": {
                "before": before_conf,
                "after": after_conf
            },
            "reason": reason
        }
