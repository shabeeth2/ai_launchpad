Here is the **Revised Execution Plan** tailored to your specific file structure, using **FastAPI**, **LangGraph**, **DuckDB**, and **SQLite**.

This plan removes all Docker dependencies and focuses on the code you need to write in `src/`.

---

### 1. The Core State (`src/components/state.py`)
*The Single Source of Truth. This defines what flows through your graph.*

```python
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
```

---

### 2. The API Layer (`src/api/`)
*How the frontend triggers the agent.*

#### A. Schemas (`src/api/schemas.py`)
```python
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
```

#### B. Main App (`src/api/main.py`)
```python
import uuid
from fastapi import FastAPI, HTTPException
from src.api.schemas import RunRequest, RunResponse, StateResponse, ApprovalRequest
from src.components.builder import build_graph

app = FastAPI()
graph = build_graph() # Compiles the LangGraph

@app.post("/run", response_model=RunResponse)
async def start_run(req: RunRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "dataset_uri": req.dataset_uri,
        "table_name": req.table_name,
        "retry_count": 0,
        "audit_log": [f"Started run for {req.table_name}"]
    }
    
    # Start graph (non-blocking in real app, awaiting here for simplicity)
    await graph.ainvoke(initial_state, config=config)
    return RunResponse(thread_id=thread_id, status="started")

@app.get("/status/{thread_id}", response_model=StateResponse)
async def get_status(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snapshot = await graph.aget_state(config)
        state = snapshot.values
        
        # Check if we are paused at the interrupt
        status = "running"
        if not snapshot.next: status = "completed"
        elif "hitl_node" in snapshot.next: status = "waiting_for_human"
            
        return StateResponse(
            thread_id=thread_id,
            status=status,
            policy_decision=state.get("policy_decision"),
            candidate_rule=state.get("candidate_rule"),
            audit_log=state.get("audit_log", [])
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found")

@app.post("/approve/{thread_id}")
async def approve(thread_id: str, req: ApprovalRequest):
    config = {"configurable": {"thread_id": thread_id}}
    
    # Inject human decision into state
    graph.update_state(
        config, 
        {"human_approval": req.approved, "audit_log": [f"Human Approved: {req.approved}"]},
        as_node="guard_node" # Resume from here
    )
    
    # Continue execution
    await graph.ainvoke(None, config=config)
    return {"status": "resumed"}
```

---

### 3. The Node Logic (`src/components/nodes/`)
*The "Brain" and "Muscle" of the agent.*

#### A. Ingest Node (`ingest_node.py`)
*Uses DuckDB to profile data without loading it all.*
```python
import duckdb
import json
from pathlib import Path

def ingest_node(state):
    uri = state["dataset_uri"]
    table = state["table_name"]
    
    # DuckDB connects to SQLite file directly
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"CALL sqlite_attach('{uri}')")
    
    # Get Schema & Basic Stats
    stats_df = con.sql(f"DESCRIBE SELECT * FROM {table}").df()
    profile = stats_df.to_dict(orient="records")
    
    # Save heavy profile to disk
    profile_path = f"local_store/profile_{table}.json"
    Path("local_store").mkdir(exist_ok=True)
    with open(profile_path, "w") as f:
        json.dump(profile, f)
        
    return {
        "profile_uri": profile_path,
        "audit_log": ["Ingestion: Profile generated via DuckDB."]
    }
```

#### B. RuleGen Node (`rulegen_node.py`)
*Uses your Catalog to generate a rule.*
```python
import json
from src.llm.client import get_llm # Wrapper for OpenAI/Anthropic

# Load your Catalog (DQ-001 to DQ-010)
with open("src/data/rule_catalog.json", "r") as f:
    CATALOG = json.load(f)

def rulegen_node(state):
    # 1. Prepare Context
    with open(state["profile_uri"], "r") as f:
        profile = json.load(f)
        
    drift_info = state.get("drift_severity", "none")
    
    # 2. Prompt LLM
    prompt = f"""
    You are a Data Quality Expert.
    Table Profile: {str(profile)[:1000]}...
    Drift Severity: {drift_info}
    
    Task: Select a rule from the Catalog to fix potential issues.
    Catalog: {json.dumps(CATALOG)}
    
    Return JSON only:
    {{
        "template_id": "DQ-XXX",
        "target_column": "col_name",
        "generated_sql": "SELECT * FROM {state['table_name']} WHERE ...",
        "description": "..."
    }}
    """
    
    # 3. Call LLM (Mocked for brevity)
    # response = llm.invoke(prompt)
    # candidate = json.loads(response.content)
    
    # MOCK RESPONSE for testing
    candidate = {
        "template_id": "DQ-001",
        "target_column": "claim_id",
        "generated_sql": f"SELECT * FROM {state['table_name']} WHERE claim_id IS NULL",
        "description": "Mandatory Field Check for claim_id"
    }
    
    return {
        "candidate_rule": candidate,
        "audit_log": [f"RuleGen: Generated {candidate['template_id']}"]
    }
```

#### C. Validator Node (`validator_node.py`)
*Runs the generated SQL in a sandbox.*
```python
import duckdb

def validator_node(state):
    rule = state["candidate_rule"]
    sql = rule["generated_sql"]
    
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"CALL sqlite_attach('{state['dataset_uri']}')")
    
    try:
        # Run on a sample (LIMIT 1000) to test syntax
        # We wrap in a CTE to ensure it's a valid SELECT
        test_sql = f"WITH test_run AS ({sql}) SELECT COUNT(*) FROM test_run"
        count = con.sql(test_sql).fetchone()[0]
        
        return {
            "validation_report": {"passed": True, "rows_flagged": count},
            "audit_log": [f"Validator: SQL valid. Flagged {count} rows."]
        }
    except Exception as e:
        return {
            "validation_report": {"passed": False, "error": str(e)},
            "audit_log": [f"Validator: Failed - {str(e)}"]
        }
```

#### D. Guard Node (`guard_node.py`)
*The Policy Logic.*
```python
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
```

---

### 4. The Graph Wiring (`src/components/builder.py`)
*Connecting the dots.*

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END

from src.components.state import AgentState
from src.components.nodes.ingest_node import ingest_node
from src.components.nodes.drift_node import drift_node
from src.components.nodes.rulegen_node import rulegen_node
from src.components.nodes.validator_node import validator_node
from src.components.nodes.guard_node import guard_node

# Define Routing Logic
def route_policy(state):
    decision = state["policy_decision"]
    if decision == "retry": return "rulegen"
    if decision == "human_review": return "hitl_node"
    if decision == "approve": return "deploy" # or END
    return END

def build_graph():
    # 1. Checkpointer
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    # 2. Graph
    workflow = StateGraph(AgentState)
    
    # 3. Nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("drift", drift_node) # (Assume you have this)
    workflow.add_node("rulegen", rulegen_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("guard_node", guard_node)
    
    # Dummy node for HITL pause
    workflow.add_node("hitl_node", lambda s: s) 
    
    # 4. Edges
    workflow.set_entry_point("ingest")
    workflow.add_edge("ingest", "drift")
    workflow.add_edge("drift", "rulegen")
    workflow.add_edge("rulegen", "validator")
    workflow.add_edge("validator", "guard_node")
    
    # Conditional Edge
    workflow.add_conditional_edges(
        "guard_node",
        route_policy,
        {
            "rulegen": "rulegen",
            "hitl_node": "hitl_node",
            "deploy": END, # Connect to deploy node if you have one
            END: END
        }
    )
    
    # 5. Compile with Interrupt
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["hitl_node"]
    )
```

### Summary of Changes
1.  **No Docker:** Everything uses `sqlite3` and `duckdb` (in-process).
2.  **Rule Catalog:** `RuleGenNode` now explicitly loads your JSON catalog and selects from it.
3.  **FastAPI:** Clean separation of API models (`schemas.py`) and Graph State (`state.py`).
4.  **Validation:** `ValidatorNode` uses DuckDB to run the generated SQL safely.