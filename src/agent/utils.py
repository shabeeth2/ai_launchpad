"""Convenience wrapper to spin up a ReAct agent compatible with LangGraph."""
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver

#  graph = workflow.compile(checkpointer=InMemorySaver())

def create_react_agent_with_tools(
    llm: BaseLanguageModel,
    tools: list[BaseTool],
    system: str = "You are a helpful assistant.",
):
    """Returns a compiled LangGraph agent ready for `.invoke()` or `.stream()`."""
    return create_react_agent(llm, tools, state_modifier=system)