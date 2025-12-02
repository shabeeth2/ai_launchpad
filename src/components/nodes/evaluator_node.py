from langchain_core.messages import HumanMessage
from src.llm.client import get_llm
from src.components.state import AgentState

def evaluator_node(state: AgentState) -> AgentState:
    """
    Critiques the agent's output or the plan.
    """
    print("--- EVALUATOR NODE ---")
    llm = get_llm()
    
    messages = state["messages"]
    last_response = messages[-1].content if messages else ""
    
    prompt = f"""
    You are an Evaluator Agent.
    Critique the following response for accuracy, safety, and completeness.
    
    Response: {last_response}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"critique": response.content}
