
import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.components.state import GlobalState, AgentState
from src.components.nodes.ingest_node import ingest_data
from src.components.nodes.drift_node import detect_drift
from src.components.nodes.rulegen_node import generate_rules
from src.components.nodes.guard_node import guard_node
from src.components.nodes.planner_node import planner_node
from src.components.nodes.agent_node import agent_node
from src.components.nodes.validator_node import evaluator_node

# --- Fixtures ---

@pytest.fixture
def global_state():
    return GlobalState(
        dataset="",
        partition="",
        profile_id="",
        profile_artifact={},
        drift_event=None,
        candidate_rule=None,
        validation_report=None,
        explanation_markdown=None,
        policy_decision=None,
        signed_approval=None,
        deployment_id=None,
        audit_log=[]
    )

@pytest.fixture
def agent_state():
    return AgentState(
        messages=[HumanMessage(content="Test request")],
        sender="user"
    )

# --- Tests for GlobalState Nodes ---

def test_ingest_node(global_state):
    result = ingest_data(global_state)
    assert "dataset" in result
    assert result["dataset"]["source"] == "sample_data.csv"
    assert result["dataset"]["metadata"]["format"] == "csv"

def test_drift_node(global_state):
    result = detect_drift(global_state)
    assert "drift_event" in result
    assert result["drift_event"]["detected"] is False
    assert "metrics" in result["drift_event"]

def test_rulegen_node(global_state):
    result = generate_rules(global_state)
    assert "candidate_rule" in result
    assert result["candidate_rule"]["rule_id"] == "rule_001"

# --- Tests for AgentState Nodes ---

def test_guard_node(agent_state):
    result = guard_node(agent_state)
    assert "safety_metadata" in result
    assert result["safety_metadata"]["safe"] is True

@patch("src.components.nodes.planner_node.get_llm")
def test_planner_node(mock_get_llm, agent_state):
    # Mock LLM response
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="1. Step 1\n2. Step 2")
    mock_get_llm.return_value = mock_llm
    
    result = planner_node(agent_state)
    
    assert "plan" in result
    assert len(result["plan"]) == 2
    assert result["plan"][0] == "1. Step 1"
    assert result["plan"][1] == "2. Step 2"

@patch("src.components.nodes.agent_node.get_llm")
def test_agent_node(mock_get_llm, agent_state):
    # Mock LLM response
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Agent response")
    mock_get_llm.return_value = mock_llm
    
    # Add a plan to state to test plan inclusion
    agent_state["plan"] = ["Step 1", "Step 2"]
    
    result = agent_node(agent_state)
    
    assert "messages" in result
    assert len(result["messages"]) == 2
    assert isinstance(result["messages"][-1], AIMessage)
    assert result["messages"][-1].content == "Agent response"

@patch("src.components.nodes.validator_node.get_llm")
def test_validator_node(mock_get_llm, agent_state):
    # Mock LLM response
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Critique: Good")
    mock_get_llm.return_value = mock_llm
    
    # Add a previous response to messages
    agent_state["messages"].append(AIMessage(content="Previous response"))
    
    result = evaluator_node(agent_state)
    
    assert "critique" in result
    assert result["critique"] == "Critique: Good"
