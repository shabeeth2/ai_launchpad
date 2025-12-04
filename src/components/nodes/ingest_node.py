import duckdb
import json
from pathlib import Path

def ingest_node(state):
    uri = state["dataset_uri"]
    table = state["table_name"]
    
    # DuckDB connects to SQLite file directly
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"CALL sqlite_attach('{uri}')")
    
    # Get Schema & Basic Stats
    stats_df = con.sql(f"DESCRIBE SELECT * FROM {table}").df()
    profile = stats_df.to_dict(orient="records")
    
    # Save heavy profile to disk
    profile_path = f"local_store/profile_{table}.json"
    Path("local_store").mkdir(exist_ok=True)
    with open(profile_path, "w") as f:
        json.dump(profile, f)
        
    return {
        "profile_uri": profile_path,
        "audit_log": ["Ingestion: Profile generated via DuckDB."]
    }