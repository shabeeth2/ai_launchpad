import operator
from typing import TypedDict, Annotated, List, Optional, Dict, Any, Literal

# Helper to append logs instead of overwriting them
def merge_lists(a: List, b: List) -> List:
    return a + b

class AgentState(TypedDict):
    # --- Inputs ---
    dataset_uri: str          # Path to 'uk_health_insurance.db'
    table_name: str           # e.g., 'claims'
    
    # --- Artifacts (Paths to local JSON files) ---
    profile_uri: Optional[str]
    drift_report_uri: Optional[str]
    
    # --- Analysis ---
    drift_detected: bool
    drift_severity: Optional[Literal["low", "medium", "high"]]
    
    # --- Generation (The Rule) ---
    # Matches your Rule Catalog structure + generated SQL
    candidate_rule: Optional[Dict[str, Any]] 
    
    # --- Validation ---
    validation_report: Optional[Dict[str, Any]]
    
    # --- Governance ---
    retry_count: int
    policy_decision: Optional[Literal["approve", "reject", "human_review", "retry"]]
    human_approval: Optional[bool]
    
    # --- Audit ---
    audit_log: Annotated[List[str], merge_lists]
