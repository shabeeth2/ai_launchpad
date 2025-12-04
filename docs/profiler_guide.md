# Data Profiler and Drift Detection Guide

This guide explains how to use the Data Profiler and Drift Detection components in the AI DQ project.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Profiler](#data-profiler)
  - [Basic Usage](#basic-usage)
  - [Profile Structure](#profile-structure)
- [Drift Detection](#drift-detection)
  - [Basic Usage](#basic-usage-1)
  - [Interpreting Results](#interpreting-results)
- [Example](#example)
- [API Reference](#api-reference)
- [Testing](#testing)

## Overview

The Data Profiler and Drift Detection components help you:
- Generate comprehensive data profiles with statistics and quality metrics
- Detect data drift between datasets over time
- Monitor data quality and consistency
- Identify anomalies and changes in data distributions

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

Here's a quick example of how to use both the profiler and drift detection:

```python
import pandas as pd
from src.components.nodes.profiler_node import DataProfiler, detect_drift

# Load or create your datasets
reference_data = pd.read_csv('reference_data.csv')
current_data = pd.read_csv('current_data.csv')

# Create a profiler instance
profiler = DataProfiler()

# Generate a profile for the reference data
profile = profiler.profile_dataframe(reference_data)
print(f"Profile generated with {profile['row_count']} rows and {profile['column_count']} columns")

# Detect drift between reference and current data
state = {
    'data': current_data,
    'reference_data': reference_data
}
result = detect_drift(state)
print(f"Drift detected: {result['drift_results']['drift_detected']}")
```

## Data Profiler

### Basic Usage

```python
from src.components.nodes.profiler_node import DataProfiler

# Initialize the profiler
profiler = DataProfiler()

# Profile a pandas DataFrame
df = pd.DataFrame({
    'numeric': [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
    'categorical': ['A', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'C', 'B']
})

profile = profiler.profile_dataframe(df)
```

### Profile Structure

The profile contains the following information:

- `timestamp`: When the profile was generated
- `row_count`: Number of rows in the dataset
- `column_count`: Number of columns in the dataset
- `column_stats`: Detailed statistics for each column
  - Basic info: name, data type, null count, unique count
  - Type-specific statistics (numeric/categorical)
  - Outlier detection for numeric columns
  - Value distributions for categorical columns
- `data_quality_metrics`: Overall data quality scores
  - Completeness: Ratio of non-null values
  - Uniqueness: Ratio of unique values
  - Validity: Data validity score
  - Consistency: Data consistency metrics
- `duplicate_rows`: Number of duplicate rows
- `memory_usage`: Memory usage of the DataFrame
- `sample_data`: A sample of the data (first 5 rows)

## Drift Detection

### Basic Usage

```python
from src.components.nodes.profiler_node import detect_drift

# Assume we have reference_data and current_data DataFrames
state = {
    'data': current_data,
    'reference_data': reference_data
}

# Detect drift
result = detect_drift(state)
drift_results = result['drift_results']

# Check if drift was detected
if drift_results['drift_detected']:
    print("Warning: Significant drift detected!")
    
# See drift by column
for col, stats in drift_results['columns'].items():
    print(f"{col}: p-value={stats['p_value']:.4f} (drift detected: {stats['drift_detected']})")
```

### Interpreting Results

- `overall_drift_score`: A value between 0 and 1 indicating the overall magnitude of drift
- `drift_detected`: Boolean indicating if significant drift was detected (p < 0.05)
- `columns`: Dictionary with drift statistics for each column
  - `p_value`: Statistical significance of the drift (lower = more significant)
  - `test`: Which statistical test was used
  - `drift_detected`: Whether drift was detected for this column

## Example

See the full example in `examples/profiler_example.py` for a complete demonstration.

## API Reference

### `DataProfiler`

```python
class DataProfiler:
    def __init__(self, reference_data: Optional[pd.DataFrame] = None):
        """
        Initialize the DataProfiler.
        
        Args:
            reference_data: Optional reference DataFrame for consistency checks
        """
        
    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive profile of the input DataFrame.
        
        Args:
            df: Input pandas DataFrame
            
        Returns:
            Dictionary containing the data profile
        """
```

### `detect_drift`

```python
def detect_drift(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect drift between current and reference data.
    
    Args:
        state: Dictionary containing:
            - 'data': Current DataFrame
            - 'reference_data': Reference DataFrame
            
    Returns:
        Updated state with 'drift_results' key containing drift analysis
    """
```

## Testing

Run the test suite with:

```bash
pytest tests/test_profiler.py -v
```

To run with coverage:

```bash
pytest tests/test_profiler.py --cov=src/components/nodes/profiler_node.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
