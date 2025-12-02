from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from src.components.builder import WorkflowBuilder
from langchain_core.messages import HumanMessage

router = APIRouter()

class WorkflowRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    workflow_type: str = "basic" # basic or advanced

class WorkflowResponse(BaseModel):
    result: Dict[str, Any]

@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    try:
        builder = WorkflowBuilder(system_prompt=request.system_prompt)
        
        if request.workflow_type == "advanced":
            graph = builder.build_advanced_graph()
        else:
            graph = builder.build_basic_graph()
            
        initial_state = {
            "messages": [HumanMessage(content=request.prompt)],
            "context": None,
            "safety_metadata": None
        }
        
        # Invoke the graph
        final_state = graph.invoke(initial_state)
        
        # Serialize the output (convert messages to dicts if needed)
        # For simplicity, we just return the raw state dict, 
        # but in production you'd want to serialize messages properly.
        return {"result": final_state}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
