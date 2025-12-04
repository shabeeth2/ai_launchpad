from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from scipy import stats
import json

@dataclass
class ColumnStats:
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dtype": self.dtype,
            "null_count": self.null_count,
            "null_percentage": self.null_percentage,
            "unique_count": self.unique_count,
            "unique_percentage": self.unique_percentage,
            "stats": self.stats
        }

class DataProfiler:
    """Comprehensive data profiling for tabular data."""
    
    def __init__(self, reference_data: Optional[pd.DataFrame] = None):
        self.reference_data = reference_data
        
    def _get_numeric_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for numeric columns."""
        def safe_float(value):
            """Safely convert a value to float, handling None and non-numeric types."""
            if value is None or isinstance(value, (dict, list)):
                return value
            try:
                return float(value) if not np.isnan(value) else None
            except (ValueError, TypeError):
                return None
        
        stats = {
            "min": safe_float(series.min()),
            "max": safe_float(series.max()),
            "mean": safe_float(series.mean()),
            "median": safe_float(series.median()),
            "std": safe_float(series.std()),
            "skewness": safe_float(series.skew()),
            "kurtosis": safe_float(series.kurtosis()),
            "zeros": int((series == 0).sum()),
            "negatives": int((series < 0).sum()),
            "outliers": self._detect_outliers(series)  # This returns a dict, which is fine
        }
        return stats
    
    def _get_categorical_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for categorical columns."""
        value_counts = series.value_counts()
        return {
            "top": value_counts.index[0] if len(value_counts) > 0 else None,
            "freq": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "n_unique": len(value_counts),
            "value_counts": value_counts.head(10).to_dict()
        }
    
    def _detect_outliers(self, series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
        """Detect outliers using z-score."""
        if series.dtype.kind in 'fc':
            z_scores = np.abs(stats.zscore(series.dropna()))
            outliers = z_scores > threshold
            return {
                "count": int(outliers.sum()),
                "percentage": float(outliers.mean() * 100) if len(outliers) > 0 else 0.0,
                "indices": np.where(outliers)[0].tolist()
            }
        return {"count": 0, "percentage": 0.0, "indices": []}
    
    def _calculate_data_quality_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate overall data quality metrics."""
        total_cells = df.size
        null_count = df.isnull().sum().sum()
        
        return {
            "completeness": 1 - (null_count / total_cells) if total_cells > 0 else 0,
            "uniqueness": df.nunique().mean() / len(df) if len(df) > 0 else 0,
            "validity": 1.0,  # Placeholder for domain-specific validation
            "consistency": self._calculate_consistency_metrics(df)
        }
    
    def _calculate_consistency_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate consistency metrics including type consistency."""
        if self.reference_data is None:
            return {"type_consistency": 1.0, "value_consistency": 1.0}
            
        # Check if column dtypes match reference
        type_matches = []
        for col in df.columns:
            if col in self.reference_data.columns:
                type_matches.append(df[col].dtype == self.reference_data[col].dtype)
        
        type_consistency = sum(type_matches) / len(type_matches) if type_matches else 1.0
        
        return {
            "type_consistency": type_consistency,
            "value_consistency": 1.0  # Placeholder for more complex consistency checks
        }
    
    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive profile of the dataframe."""
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
            
        profile = {
            "timestamp": datetime.utcnow().isoformat(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_stats": {},
            "data_quality_metrics": self._calculate_data_quality_metrics(df),
            "duplicate_rows": df.duplicated().sum(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "sample_data": df.head(5).to_dict(orient='records')
        }
        
        # Profile each column
        for col in df.columns:
            series = df[col]
            null_count = series.isnull().sum()
            unique_count = series.nunique()
            
            col_stats = ColumnStats(
                name=col,
                dtype=str(series.dtype),
                null_count=int(null_count),
                null_percentage=float(null_count / len(df)) if len(df) > 0 else 0.0,
                unique_count=int(unique_count),
                unique_percentage=float(unique_count / len(df)) if len(df) > 0 else 0.0
            )
            
            # Add type-specific statistics
            if np.issubdtype(series.dtype, np.number):
                col_stats.stats = self._get_numeric_stats(series)
            else:
                col_stats.stats = self._get_categorical_stats(series)
            
            profile["column_stats"][col] = col_stats.to_dict()
        
        return profile

def profile_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Profile the input data and generate data quality metrics.
    
    Args:
        state: Current workflow state containing the dataset
        
    Returns:
        Updated state with profile artifact
    """
    if "data" not in state or not isinstance(state["data"], pd.DataFrame):
        raise ValueError("State must contain a 'data' key with a pandas DataFrame")
    
    profiler = DataProfiler()
    state["profile_artifact"] = profiler.profile_dataframe(state["data"])
    
    return state

def detect_drift(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect drift between current and reference data.
    
    Args:
        state: Current workflow state containing current and reference data
        
    Returns:
        Updated state with drift detection results
    """
    if "data" not in state or not isinstance(state["data"], pd.DataFrame):
        raise ValueError("State must contain a 'data' key with a pandas DataFrame")
    
    if "reference_data" not in state or not isinstance(state["reference_data"], pd.DataFrame):
        raise ValueError("State must contain a 'reference_data' key with a pandas DataFrame")
    
    current_data = state["data"]
    reference_data = state["reference_data"]
    
    # Initialize drift results
    drift_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "columns": {},
        "overall_drift_score": 0.0,
        "drift_detected": False,
        "metrics": {}
    }
    
    # Calculate drift for each column
    drift_scores = []
    
    for col in current_data.columns:
        if col not in reference_data.columns:
            continue
            
        current_series = current_data[col].dropna()
        ref_series = reference_data[col].dropna()
        
        if len(current_series) == 0 or len(ref_series) == 0:
            continue
            
        col_drift = {"drift_detected": False, "p_value": 1.0, "test": None}
        
        # Choose appropriate statistical test based on data type
        if np.issubdtype(current_series.dtype, np.number):
            # For numerical data, use Kolmogorov-Smirnov test
            if len(current_series) > 1 and len(ref_series) > 1:
                _, p_value = stats.ks_2samp(current_series, ref_series)
                col_drift.update({
                    "p_value": float(p_value),
                    "test": "Kolmogorov-Smirnov",
                    "drift_detected": p_value < 0.05
                })
        else:
            # For categorical data, use chi-square test
            if len(current_series) > 1 and len(ref_series) > 1:
                current_counts = current_series.value_counts(normalize=True)
                ref_counts = ref_series.value_counts(normalize=True)
                
                # Align indices and fill missing values with 0
                all_categories = set(current_counts.index) | set(ref_counts.index)
                current_aligned = [current_counts.get(cat, 0) for cat in all_categories]
                ref_aligned = [ref_counts.get(cat, 0) for cat in all_categories]
                
                try:
                    _, p_value = stats.chisquare(current_aligned, ref_aligned)
                    col_drift.update({
                        "p_value": float(p_value),
                        "test": "Chi-square",
                        "drift_detected": p_value < 0.05
                    })
                except:
                    pass
        
        drift_results["columns"][col] = col_drift
        if "p_value" in col_drift:
            drift_scores.append(1 - col_drift["p_value"])
    
    # Calculate overall drift score
    if drift_scores:
        drift_results["overall_drift_score"] = float(np.mean(drift_scores))
        drift_results["drift_detected"] = any(
            col.get("drift_detected", False) 
            for col in drift_results["columns"].values()
        )
    
    state["drift_results"] = drift_results
    return state