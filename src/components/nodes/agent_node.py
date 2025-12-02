from langchain_core.messages import HumanMessage, SystemMessage
from src.llm.client import get_llm
from src.components.state import AgentState

def agent_node(state: AgentState) -> AgentState:
    """
    Invokes the LLM to generate a response based on messages and context.
    """
    print("--- AGENT NODE ---")
    llm = get_llm()
    
    messages = state["messages"]
    context = state.get("context", "")
    
    # Simple prompt engineering to include context
    # Simple prompt engineering to include context and plan
    system_content = []
    if context:
        system_content.append(f"Context: {context}")
    
    plan = state.get("plan")
    if plan:
        plan_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan)])
        system_content.append(f"Plan:\n{plan_str}")
        
    if system_content:
        system_msg = SystemMessage(content="\n\n".join(system_content))
        # Prepend context if not already present (simplified logic)
        messages = [system_msg] + messages
        
    response = llm.invoke(messages)
    
    # Append response to history? Or just return the latest?
    # LangGraph usually expects updates to the state.
    # If 'messages' is an Annotated list with add_messages, we return the new message.
    # Here we are using a simple TypedDict, so we manually append.
    
    return {"messages": state["messages"] + [response]}
