def guard_node(state):
    valid = state["validation_report"]["passed"]
    retry = state["retry_count"]
    
    # 1. Self-Correction Loop
    if not valid:
        if retry < 3:
            return {
                "policy_decision": "retry",
                "retry_count": retry + 1,
                "audit_log": ["Guard: Validation failed. Retrying..."]
            }
        else:
            return {"policy_decision": "reject", "audit_log": ["Guard: Max retries reached."]}
            
    # 2. Human Review Logic
    # If rule flags > 0 rows, we might want a human to check
    if state["validation_report"]["rows_flagged"] > 0:
        return {
            "policy_decision": "human_review",
            "audit_log": ["Guard: Anomalies found. Requesting Human Review."]
        }
        
    return {"policy_decision": "approve", "audit_log": ["Guard: Auto-Approved."]}
