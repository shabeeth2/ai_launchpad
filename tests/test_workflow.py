import asyncio
import uuid
import os
import shutil
import sys
from src.components.builder import build_graph

async def test_full_workflow():
    """Test the complete workflow including HITL"""
    
    # Clean up
    if os.path.exists("local_store"):
        shutil.rmtree("local_store")
        
    print("=" * 60)
    print("TEST 1: Full Workflow with HITL Trigger")
    print("=" * 60)
    
    try:
        graph = build_graph()
        
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        # We need to use a real table from the database
        initial_state = {
            "dataset_uri": "uk_health_insurance.db",
            "table_name": "addresses",  # Use real table
            "retry_count": 0,
            "audit_log": ["Started run for addresses"]
        }
        
        print(f"\n1. Starting run with thread_id: {thread_id}")
        print(f"   Table: {initial_state['table_name']}")
        
        await graph.ainvoke(initial_state, config=config)
        
        # Check status
        snapshot = await graph.aget_state(config)
        print(f"\n2. Status after initial run:")
        print(f"   Next nodes: {snapshot.next}")
        print(f"   Policy decision: {snapshot.values.get('policy_decision')}")
        
        validation_report = snapshot.values.get('validation_report')
        print(f"   Validation report: {validation_report}")
        
        audit_log = snapshot.values.get('audit_log', [])
        print(f"\n3. Audit Log ({len(audit_log)} entries):")
        for i, log in enumerate(audit_log, 1):
            print(f"   {i}. {log}")
        
        if "hitl_node" in snapshot.next:
            print(f"\n4. ✓ Hit HITL node (waiting for human approval)")
            candidate_rule = snapshot.values.get('candidate_rule')
            print(f"   Candidate rule:")
            print(f"     - Template: {candidate_rule.get('template_id')}")
            print(f"     - Column: {candidate_rule.get('target_column')}")
            print(f"     - SQL: {candidate_rule.get('generated_sql')}")
            
            # Simulate human approval
            print(f"\n5. Simulating human approval...")
            graph.update_state(
                config, 
                {"human_approval": True, "audit_log": ["Human Approved: True"]},
                as_node="guard_node"
            )
            
            print(f"\n6. Resuming workflow...")
            await graph.ainvoke(None, config=config)
            
            snapshot = await graph.aget_state(config)
            print(f"\n7. Status after resume:")
            print(f"   Next nodes: {snapshot.next}")
            print(f"   Final audit log:")
            for i, log in enumerate(snapshot.values.get('audit_log', []), 1):
                print(f"   {i}. {log}")
            
            print(f"\n✓ TEST PASSED: Full HITL workflow completed successfully")
            return True
        else:
            print(f"\n4. Did not hit HITL node")
            print(f"   This may happen if no rows were flagged by the validation")
            rows_flagged = validation_report.get('rows_flagged', 0) if validation_report else 0
            print(f"   Rows flagged: {rows_flagged}")
            print(f"   Policy decision: {snapshot.values.get('policy_decision')}")
            
            if snapshot.values.get('policy_decision') == 'approve':
                print(f"\n✓ TEST PASSED: Workflow completed with auto-approval")
                return True
            else:
                print(f"\n⚠ TEST WARNING: Unexpected flow")
                return False
    
    except Exception as e:
        print(f"\n✗ TEST FAILED with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "=" * 60)
    print("LANGGRAPH WORKFLOW VERIFICATION TESTS")
    print("=" * 60)
    
    success = await test_full_workflow()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
