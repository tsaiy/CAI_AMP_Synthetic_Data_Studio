import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class SummaryFormatter:
    """Build XML‑ish blocks for prompt ingestion with error handling."""

    @staticmethod
    def first_rows_block(df: pd.DataFrame, n: int = 10) -> str:
        """Generate a CSV snippet of the first n rows."""
        try:
            # Handle potential issues with object serialization
            # Replace problematic values with their string representation
            safe_df = df.head(n).copy()
            
            for col in safe_df.columns:
                # Replace problematic values in object columns
                if safe_df[col].dtype == 'object':
                    safe_df[col] = safe_df[col].apply(lambda x: 
                                                  str(x) if x is not None else None)
            
            # Use CSV repr so models instantly see delimiters
            return safe_df.to_csv(index=False)
        except Exception as e:
            return f"Error generating CSV snippet: {str(e)}\n"

    @staticmethod
    def json_block(summary: Dict[str, Any]) -> str:
        """Convert summary dict to a JSON string, handling problematic values."""
        try:
            # Handle non-serializable objects
            def clean_for_json(obj):
                if isinstance(obj, dict):
                    return {k: clean_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_for_json(item) for item in obj]
                elif isinstance(obj, (int, float, str, bool, type(None))):
                    return obj
                elif isinstance(obj, np.number):
                    return float(obj)
                else:
                    return str(obj)
            
            # Clean the summary dict
            clean_summary = clean_for_json(summary)
            
            # Convert to JSON
            return json.dumps(clean_summary, separators=(",", ":"), ensure_ascii=False)
        except Exception as e:
            return f"Error generating JSON summary: {str(e)}"