"""
Final verification script to test all components
"""

import sys
import os

def test_imports():
    """Test all imports"""
    print("=" * 60)
    print("Testing Imports...")
    print("=" * 60)
    
    try:
        from src.components.state import AgentState
        print("✅ AgentState imported")
        
        from src.api.schemas import RunRequest, RunResponse
        print("✅ API schemas imported")
        
        from src.components.nodes.ingest_node import ingest_node
        print("✅ ingest_node imported")
        
        from src.components.nodes.drift_node import drift_node
        print("✅ drift_node imported")
        
        from src.components.nodes.rulegen_node import rulegen_node
        print("✅ rulegen_node imported")
        
        from src.components.nodes.validator_node import validator_node
        print("✅ validator_node imported")
        
        from src.components.nodes.guard_node import guard_node
        print("✅ guard_node imported")
        
        from src.components.builder import build_graph
        print("✅ build_graph imported")
        
        from src.api.main import app
        print("✅ FastAPI app imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_build():
    """Test graph builds without errors"""
    print("\n" + "=" * 60)
    print("Testing  Graph Build...")
    print("=" * 60)
    
    try:
        from src.components.builder import build_graph
        graph = build_graph()
        print("✅ Graph built successfully")
        print(f"   Graph type: {type(graph)}")
        return True
    except Exception as e:
        print(f"❌ Graph build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database exists and has tables"""
    print("\n" + "=" * 60)
    print("Testing Database...")
    print("=" * 60)
    
    try:
        import sqlite3
        
        if not os.path.exists("uk_health_insurance.db"):
            print("❌ Database file not found")
            return False
        
        conn = sqlite3.connect('uk_health_insurance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            print(f"✅ Database found with {len(tables)} tables:")
            for table in tables[:5]:
                print(f"   - {table[0]}")
            return True
        else:
            print("❌ No tables found in database")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_duckdb_connection():
    """Test DuckDB can connect to SQLite"""
    print("\n" + "=" * 60)
    print("Testing DuckDB Connection...")
    print("=" * 60)
    
    try:
        import duckdb
        
        con = duckdb.connect()
        con.execute("INSTALL sqlite; LOAD sqlite;")
        con.execute("CALL sqlite_attach('uk_health_insurance.db')")
        
        result = con.sql("SELECT name FROM sqlite_master WHERE type='table'").df()
        print(f"✅ DuckDB connected to SQLite")
        print(f"   Found {len(result)} tables via DuckDB")
        
        return True
    except Exception as e:
        print(f"❌ DuckDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_execution():
    """Test individual node execution"""
    print("\n" + "=" * 60)
    print("Testing Node Execution...")
    print("=" * 60)
    
    try:
        from src.components.nodes.ingest_node import ingest_node
        
        # Clean up local_store
        import shutil
        if os.path.exists("local_store"):
            shutil.rmtree("local_store")
        
        test_state = {
            "dataset_uri": "uk_health_insurance.db",
            "table_name": "addresses",
            "retry_count": 0,
            "audit_log": []
        }
        
        result = ingest_node(test_state)
        
        if "profile_uri" in result:
            print(f"✅ ingest_node executed")
            print(f"   Profile URI: {result['profile_uri']}")
            
            # Check if file was created
            if os.path.exists(result['profile_uri']):
                print(f"   ✅ Profile file created")
                return True
            else:
                print(f"   ❌ Profile file not created")
                return False
        else:
            print(f"❌ ingest_node did not return profile_uri")
            return False
    except Exception as e:
        print(f"❌ Node execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SYSTEM VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Graph Build", test_graph_build),
        ("Database", test_database),
        ("DuckDB Connection", test_duckdb_connection),
        ("Node Execution", test_node_execution),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe system is ready to use!")
        print("\nNext steps:")
        print("  1. Start the API: uvicorn src.api.main:app --reload")
        print("  2. Test endpoints: POST http://localhost:8000/run")
        print("  3. Check status: GET http://localhost:8000/status/{thread_id}")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease review the failures above.")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
