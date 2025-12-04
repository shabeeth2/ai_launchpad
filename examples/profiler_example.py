"""
Example script demonstrating how to use the DataProfiler and drift detection.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add the project root to the Python path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.components.nodes.profiler_node import DataProfiler, profile_data, detect_drift

def generate_sample_data(rows=1000, seed=42):
    """Generate sample data for demonstration."""
    np.random.seed(seed)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=rows)
    dates = pd.date_range(start=start_date, end=end_date, periods=rows)
    
    # Create DataFrame with various data types
    data = {
        'date': dates,
        'customer_id': np.arange(1, rows + 1),
        'age': np.random.normal(35, 10, rows).astype(int).clip(18, 100),
        'income': np.random.lognormal(10, 0.5, rows).astype(int),
        'purchase_amount': np.random.exponential(100, rows).round(2),
        'product_category': np.random.choice(
            ['Electronics', 'Clothing', 'Home', 'Books', 'Other'], 
            size=rows,
            p=[0.3, 0.25, 0.2, 0.15, 0.1]
        ),
        'is_premium': np.random.choice([True, False], size=rows, p=[0.2, 0.8]),
        'satisfaction_score': np.random.randint(1, 6, size=rows),
        'last_purchase_days_ago': np.random.poisson(30, size=rows).clip(1, 90),
        'has_subscription': np.random.choice([True, False], size=rows, p=[0.4, 0.6]),
    }
    
    # Add some null values
    for col in data:
        if col != 'date' and col != 'customer_id':
            mask = np.random.random(rows) < 0.05  # 5% null values
            if mask.any():
                data[col] = np.where(mask, None, data[col])
    
    return pd.DataFrame(data)

def main():
    print("=== Data Profiling and Drift Detection Example ===\n")
    
    # Generate reference data (e.g., last month's data)
    print("Generating reference data (1000 rows)...")
    reference_data = generate_sample_data(rows=1000, seed=42)
    
    # Generate current data (e.g., this month's data with some drift)
    print("Generating current data (1000 rows) with some drift...")
    current_data = generate_sample_data(rows=1000, seed=43)  # Different seed for different data
    
    # 1. Profile the reference data
    print("\n=== Profiling Reference Data ===")
    profiler = DataProfiler()
    ref_profile = profiler.profile_dataframe(reference_data)
    
    print(f"\nReference Data Profile Summary:")
    print(f"- Rows: {ref_profile['row_count']}")
    print(f"- Columns: {ref_profile['column_count']}")
    print(f"- Memory Usage: {ref_profile['memory_usage'] / (1024*1024):.2f} MB")
    
    # Show some column stats
    print("\nColumn Statistics (first 3 columns):")
    for i, (col, stats) in enumerate(ref_profile['column_stats'].items()):
        if i >= 3:
            break
        print(f"\n{col} ({stats['dtype']}):")
        print(f"  - Null: {stats['null_count']} ({stats['null_percentage']*100:.1f}%)")
        print(f"  - Unique: {stats['unique_count']} ({stats['unique_percentage']*100:.1f}%)")
    
    # 2. Profile the current data
    print("\n=== Profiling Current Data ===")
    current_profile = profiler.profile_dataframe(current_data)
    
    # 3. Detect drift between reference and current data
    print("\n=== Detecting Data Drift ===")
    state = {
        'data': current_data,
        'reference_data': reference_data
    }
    
    result = detect_drift(state)
    drift_results = result['drift_results']
    
    # Print drift summary
    print(f"\nDrift Detection Results:")
    print(f"- Overall Drift Score: {drift_results['overall_drift_score']:.3f}")
    print(f"- Drift Detected: {'Yes' if drift_results['drift_detected'] else 'No'}")
    
    # Print drift by column
    print("\nDrift by Column (p-value < 0.05 indicates significant drift):")
    for col, stats in drift_results['columns'].items():
        print(f"- {col}: p-value = {stats['p_value']:.4f} ({'DRIFT' if stats['drift_detected'] else 'No Drift'})")
    
    # Save results to files
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True, parents=True)
    
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            # Convert all keys to strings and recursively process values
            result = {}
            for k, v in obj.items():
                # Convert key to string
                if isinstance(k, (pd.Timestamp, datetime)):
                    k_str = k.isoformat()
                else:
                    k_str = str(k)
                # Recursively process value
                if isinstance(v, (dict, list, tuple, set, pd.Timestamp, datetime, np.integer, np.floating, np.ndarray)) or hasattr(v, 'to_dict'):
                    result[k_str] = json_serial(v)
                else:
                    result[k_str] = v
            return result
        elif isinstance(obj, (list, tuple, set)):
            return [json_serial(item) for item in obj]
        return str(obj)  # Convert any remaining types to string as a fallback
    
    # Save reference profile
    ref_profile_path = output_dir / 'reference_profile.json'
    with open(ref_profile_path, 'w') as f:
        json.dump(ref_profile, f, indent=2, default=json_serial)
    
    # Save current profile
    current_profile_path = output_dir / 'current_profile.json'
    with open(current_profile_path, 'w') as f:
        json.dump(current_profile, f, indent=2, default=json_serial)
    
    # Save drift results
    drift_results_path = output_dir / 'drift_results.json'
    with open(drift_results_path, 'w') as f:
        json.dump(drift_results, f, indent=2, default=json_serial)
    
    print(f"\nResults saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
