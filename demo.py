"""
Simple demonstration of the workflow
"""
import asyncio
import uuid
from src.components.builder import build_graph

async def demo():
    print("\n" + "🚀 " * 20)
    print("AI DATA QUALITY AGENT - LIVE DEMONSTRATION")
    print("🚀 " * 20 + "\n")
    
    # Build the graph
    print("📊 Building LangGraph workflow...")
    graph = build_graph()
    print("✅ Graph built!\n")
    
    # Create a run
    thread_id = str(uuid.uuid4())[:8]  # Short ID for demo
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"🎯 Starting workflow (Thread: {thread_id})")
    print(f"   Database: uk_health_insurance.db")
    print(f"   Table: addresses\n")
    
    initial_state = {
        "dataset_uri": "uk_health_insurance.db",
        "table_name": "addresses",
        "retry_count": 0,
        "audit_log": [f"🎬 Started workflow for addresses table"]
    }
    
    print("⚡ Executing workflow...\n")
    
    # Run the workflow
    await graph.ainvoke(initial_state, config=config)
    
    # Get final state
    snapshot = await graph.aget_state(config)
    state = snapshot.values
    
    print("=" * 60)
    print("📋 WORKFLOW RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 Final Status: {snapshot.next if snapshot.next else 'COMPLETED'}")
    print(f"📊 Policy Decision: {state.get('policy_decision', 'N/A')}")
    
    print(f"\n📝 Audit Trail:")
    for i, log in enumerate(state.get('audit_log', []), 1):
        print(f"   {i}. {log}")
    
    candidate_rule = state.get('candidate_rule')
    if candidate_rule:
        print(f"\n🔍 Generated Rule:")
        print(f"   Template: {candidate_rule.get('template_id')}")
        print(f"   Target Column: {candidate_rule.get('target_column')}")
        print(f"   SQL: {candidate_rule.get('generated_sql')}")
    
    validation = state.get('validation_report')
    if validation:
        print(f"\n✅ Validation Results:")
        print(f"   Passed: {validation.get('passed')}")
        print(f"   Rows Flagged: {validation.get('rows_flagged', 0)}")
    
    print("\n" + "=" * 60)
    if not snapshot.next:
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
    elif "hitl_node" in snapshot.next:
        print("⏸️  WAITING FOR HUMAN APPROVAL")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demo())
