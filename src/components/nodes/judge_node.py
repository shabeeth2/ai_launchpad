from langchain_core.messages import HumanMessage
from src.llm.client import get_llm
from src.components.state import AgentState

def judge_node(state: AgentState) -> AgentState:
    """
    Decides if the output is sufficient or if replanning/refining is needed.
    For this boilerplate, it just synthesizes a final answer.
    """
    print("--- JUDGE NODE ---")
    llm = get_llm()
    
    critique = state.get("critique", "")
    messages = state["messages"]
    last_response = messages[-1].content if messages else ""
    
    prompt = f"""
    You are a Judge Agent.
    Based on the original response and the critique, provide the final, polished answer.
    
    Original Response: {last_response}
    Critique: {critique}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {"final_answer": response.content}
