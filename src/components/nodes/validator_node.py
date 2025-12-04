import duckdb

def validator_node(state):
    rule = state["candidate_rule"]
    sql = rule["generated_sql"]
    
    con = duckdb.connect()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"CALL sqlite_attach('{state['dataset_uri']}')")
    
    try:
        # Run on a sample (LIMIT 1000) to test syntax
        # We wrap in a CTE to ensure it's a valid SELECT
        test_sql = f"WITH test_run AS ({sql}) SELECT COUNT(*) FROM test_run"
        count = con.sql(test_sql).fetchone()[0]
        
        return {
            "validation_report": {"passed": True, "rows_flagged": count},
            "audit_log": [f"Validator: SQL valid. Flagged {count} rows."]
        }
    except Exception as e:
        return {
            "validation_report": {"passed": False, "error": str(e)},
            "audit_log": [f"Validator: Failed - {str(e)}"]
        }
