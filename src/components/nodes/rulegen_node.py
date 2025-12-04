import json
from src.llm.client import get_llm # Wrapper for OpenAI/Anthropic

# Load your Catalog (DQ-001 to DQ-010)
try:
    with open("src/data/rule_catalog.json", "r") as f:
        CATALOG = json.load(f)
except FileNotFoundError:
    CATALOG = []

def rulegen_node(state):
    # 1. Prepare Context
    with open(state["profile_uri"], "r") as f:
        profile = json.load(f)
        
    # Extract column names from profile
    column_names = [col.get("column_name") for col in profile if col.get("column_name")]
    
    drift_info = state.get("drift_severity", "none")
    table_name = state['table_name']
    
    # 2. Prompt LLM (or mock intelligent selection)
    # For now, we'll create a simple rule that checks for NULL values in the first column
    
    # MOCK RESPONSE for testing - use actual column from the profile
    if column_names:
        target_column = column_names[0]  # Use first column
        candidate = {
            "template_id": "DQ-001",
            "target_column": target_column,
            "generated_sql": f"SELECT * FROM {table_name} WHERE {target_column} IS NULL",
            "description": f"Mandatory Field Check for {target_column}"
        }
    else:
        # Fallback if no columns found
        candidate = {
            "template_id": "DQ-001",
            "target_column": "unknown",
            "generated_sql": f"SELECT * FROM {table_name} LIMIT 10",
            "description": "Generic data quality check"
        }
    
    return {
        "candidate_rule": candidate,
        "audit_log": [f"RuleGen: Generated {candidate['template_id']} for column {candidate['target_column']}"]
    }
