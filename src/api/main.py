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
