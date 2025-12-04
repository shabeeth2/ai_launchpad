import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.components.nodes.profiler_node import DataProfiler, profile_data, detect_drift

@pytest.fixture
def sample_data():
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    data = {
        'date': dates,
        'numeric1': np.random.normal(0, 1, 100),
        'numeric2': np.random.randint(1, 100, 100),
        'categorical': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'boolean': np.random.choice([True, False], 100),
        'with_nulls': [None if x % 10 == 0 else x for x in range(100)]
    }
    
    return pd.DataFrame(data)

def test_data_profiler_initialization():
    """Test DataProfiler initialization."""
    profiler = DataProfiler()
    assert profiler.reference_data is None
    
    df = pd.DataFrame({'test': [1, 2, 3]})
    profiler_with_ref = DataProfiler(reference_data=df)
    assert profiler_with_ref.reference_data.equals(df)

def test_profile_dataframe(sample_data):
    """Test profiling a DataFrame."""
    profiler = DataProfiler()
    profile = profiler.profile_dataframe(sample_data)
    
    # Check basic structure
    assert 'timestamp' in profile
    assert 'row_count' in profile
    assert 'column_count' in profile
    assert 'column_stats' in profile
    assert 'data_quality_metrics' in profile
    
    # Check row and column counts
    assert profile['row_count'] == 100
    assert profile['column_count'] == 6
    
    # Check column stats
    assert 'numeric1' in profile['column_stats']
    assert 'categorical' in profile['column_stats']
    
    # Check data quality metrics
    metrics = profile['data_quality_metrics']
    assert 0 <= metrics['completeness'] <= 1
    assert 0 <= metrics['uniqueness'] <= 1
    assert 0 <= metrics['validity'] <= 1

def test_drift_detection():
    """Test drift detection between two datasets."""
    # Create reference data
    np.random.seed(42)
    ref_data = pd.DataFrame({
        'numeric': np.random.normal(0, 1, 1000),
        'categorical': np.random.choice(['A', 'B', 'C'], 1000, p=[0.5, 0.3, 0.2])
    })
    
    # Create current data with some drift
    current_data = pd.DataFrame({
        'numeric': np.random.normal(0.5, 1.2, 1000),  # Different distribution
        'categorical': np.random.choice(['A', 'B', 'C'], 1000, p=[0.3, 0.4, 0.3])  # Different distribution
    })
    
    # Test detect_drift function
    state = {
        'data': current_data,
        'reference_data': ref_data
    }
    
    result = detect_drift(state)
    
    # Check if drift results are in the state
    assert 'drift_results' in result
    assert 'columns' in result['drift_results']
    assert 'overall_drift_score' in result['drift_results']
    assert 'drift_detected' in result['drift_results']
    
    # Check if drift was detected (should be true for our test data)
    assert result['drift_results']['drift_detected'] is True
    
    # Check column-level drift detection
    assert 'numeric' in result['drift_results']['columns']
    assert 'categorical' in result['drift_results']['columns']
    
    # Check that p-values are within valid range
    for col, stats in result['drift_results']['columns'].items():
        assert 0 <= stats['p_value'] <= 1

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_profiler.py"])
