from typing import List, Optional, Callable
from langgraph.graph import StateGraph, END
from langchain_core.tools import BaseTool

from src.components.state import AgentState
from src.components.nodes.guard_node import guard_node
from src.components.nodes.memory_node import memory_node
from src.components.nodes.agent_node import agent_node
from src.components.nodes.planner_node import planner_node
from src.components.nodes.evaluator_node import evaluator_node
from src.components.nodes.judge_node import judge_node

class WorkflowBuilder:
    def __init__(self, system_prompt: str = "You are a helpful assistant.", tools: List[BaseTool] = []):
        self.system_prompt = system_prompt
        self.tools = tools
        self.graph_builder = StateGraph(AgentState)

    def build_basic_graph(self):
        """
        Builds the standard Guard -> Memory -> Agent flow.
        """
        self.graph_builder.add_node("guard", guard_node)
        self.graph_builder.add_node("memory", memory_node)
        self.graph_builder.add_node("agent", agent_node)

        self.graph_builder.set_entry_point("guard")
        
        self.graph_builder.add_edge("guard", "memory")
        self.graph_builder.add_edge("memory", "agent")
        self.graph_builder.add_edge("agent", END)

        return self.graph_builder.compile()

    def build_advanced_graph(self):
        """
        Builds a flow with Planner -> Agent -> Evaluator -> Judge.
        """
        self.graph_builder.add_node("planner", planner_node)
        self.graph_builder.add_node("agent", agent_node)
        self.graph_builder.add_node("evaluator", evaluator_node)
        self.graph_builder.add_node("judge", judge_node)

        self.graph_builder.set_entry_point("planner")

        self.graph_builder.add_edge("planner", "agent")
        self.graph_builder.add_edge("agent", "evaluator")
        self.graph_builder.add_edge("evaluator", "judge")
        self.graph_builder.add_edge("judge", END)
        
        return self.graph_builder.compile()
