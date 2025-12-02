from typing import TypedDict, List, Any, Optional, Dict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    context: Optional[str]
    safety_metadata: Optional[Dict[str, Any]]
    plan: Optional[List[str]]
    critique: Optional[str]
    final_answer: Optional[str]
