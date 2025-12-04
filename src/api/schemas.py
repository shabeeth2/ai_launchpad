from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class RunRequest(BaseModel):
    dataset_uri: str = "uk_health_insurance.db"
    table_name: str = "claims"

class RunResponse(BaseModel):
    thread_id: str
    status: str

class StateResponse(BaseModel):
    thread_id: str
    status: str
    policy_decision: Optional[str]
    candidate_rule: Optional[Dict[str, Any]]
    audit_log: List[str]

class ApprovalRequest(BaseModel):
    approved: bool
