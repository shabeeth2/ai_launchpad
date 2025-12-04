import sqlite3
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
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
    # conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    # checkpointer = SqliteSaver(conn)
    checkpointer = MemorySaver()
    
    # 2. Graph
    workflow = StateGraph(AgentState)
    
    # 3. Nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("drift", drift_node)
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
