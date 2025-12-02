from langchain_core.messages import SystemMessage, HumanMessage
from src.llm.client import get_llm
from src.components.state import AgentState

def planner_node(state: AgentState) -> AgentState:
    """
    Decomposes the user request into a list of subtasks.
    """
    print("--- PLANNER NODE ---")
    llm = get_llm()
    
    messages = state["messages"]
    # Extract the latest user request
    user_request = messages[-1].content if messages else "No request"
    
    prompt = f"""
    You are a Planner Agent.
    Break down the following user request into a step-by-step plan.
    Return ONLY the plan as a numbered list.
    
    Request: {user_request}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Naive parsing of the plan
    plan_text = response.content
    plan_steps = [line.strip() for line in plan_text.split('\n') if line.strip()]
    
    return {"plan": plan_steps}
