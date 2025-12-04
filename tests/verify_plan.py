import asyncio
import uuid
import os
import shutil
from src.components.builder import build_graph

async def main():
    # Clean up local_store and checkpoints.db for fresh run
    if os.path.exists("local_store"):
        shutil.rmtree("local_store")
    if os.path.exists("checkpoints.db"):
        os.remove("checkpoints.db")
        
    print("Building graph...")
    graph = build_graph()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "dataset_uri": "uk_health_insurance.db",
        "table_name": "claims",
        "retry_count": 0,
        "audit_log": ["Started run for claims"]
    }
    
    print(f"Starting run with thread_id: {thread_id}")
    await graph.ainvoke(initial_state, config=config)
    
    # Check status
    snapshot = await graph.aget_state(config)
    print(f"Status after initial run: {snapshot.next}")
    print(f"Audit Log: {snapshot.values.get('audit_log')}")
    
    if "hitl_node" in snapshot.next:
        print("Hit HITL node. Approving...")
        graph.update_state(
            config, 
            {"human_approval": True, "audit_log": ["Human Approved: True"]},
            as_node="guard_node"
        )
        print("Resuming...")
        await graph.ainvoke(None, config=config)
        
        snapshot = await graph.aget_state(config)
        print(f"Status after resume: {snapshot.next}")
        print(f"Audit Log: {snapshot.values.get('audit_log')}")
    else:
        print("Did not hit HITL node.")

if __name__ == "__main__":
    asyncio.run(main())
