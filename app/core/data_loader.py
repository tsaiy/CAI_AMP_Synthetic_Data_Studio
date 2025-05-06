import pandas as pd
import numpy as np
import json
import os
import warnings
from pathlib import Path
from typing import Optional, Union

class DataLoader:
    """Load arbitrary tabular data into a DataFrame with robust error handling."""
    
    @staticmethod
    def load(path: str, sample_rows: int = 100000) -> pd.DataFrame:
        """
        Load data from various file formats into a pandas DataFrame.
        
        Args:
            path: Path to the data file
            sample_rows: Maximum number of rows to load for large files
            
        Returns:
            pandas DataFrame with the loaded data
        """
        # Validate the path exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        # Get file extension
        ext = Path(path).suffix.lower()
        
        try:
            if ext == ".csv":
                # Try different encoding and delimiter options
                try:
                    df = pd.read_csv(path, encoding='utf-8')
                except:
                    try:
                        df = pd.read_csv(path, encoding='latin1')
                    except:
                        try:
                            # Try with different delimiters
                            df = pd.read_csv(path, sep=None, engine='python')
                        except:
                            # Last resort - try reading with very permissive settings
                            df = pd.read_csv(path, sep=None, engine='python', 
                                             encoding='latin1', on_bad_lines='skip')
            elif ext == ".tsv":
                df = pd.read_csv(path, sep='\t')
            elif ext == ".json":
                # Try multiple JSON formats
                try:
                    # Try JSONL format first
                    df = pd.read_json(path, lines=True)
                except ValueError:
                    try:
                        # Then try normal JSON
                        df = pd.read_json(path)
                    except:
                        # Try loading as raw JSON and converting
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            df = pd.DataFrame(data)
                        elif isinstance(data, dict):
                            # If it's a dict, try to extract a list or convert the dict itself
                            for k, v in data.items():
                                if isinstance(v, list) and len(v) > 0:
                                    df = pd.DataFrame(v)
                                    break
                            else:
                                df = pd.DataFrame([data])
                        else:
                            raise ValueError(f"Unsupported JSON structure in {path}")
            elif ext in (".xls", ".xlsx"):
                try:
                    # Try with openpyxl first
                    df = pd.read_excel(path, engine="openpyxl")
                except:
                    # Fall back to xlrd for older Excel files
                    df = pd.read_excel(path)
            elif ext == ".xlsb":
                df = pd.read_excel(path, engine="pyxlsb")
            elif ext == ".parquet":
                df = pd.read_parquet(path)
            elif ext == ".feather":
                df = pd.read_feather(path)
            elif ext == ".pickle" or ext == ".pkl":
                df = pd.read_pickle(path)
            elif ext == ".sas7bdat":
                df = pd.read_sas(path)
            elif ext == ".dta":
                df = pd.read_stata(path)
            elif ext == ".h5" or ext == ".hdf5":
                df = pd.read_hdf(path)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
                
            # Clean up the DataFrame
            # Replace infinite values with NaN
            df = df.replace([np.inf, -np.inf], np.nan)
            
            # Handle duplicate column names
            if df.columns.duplicated().any():
                df.columns = [f"{col}_{i}" if i > 0 else col 
                              for i, col in enumerate(df.columns)]
                              
            # Keep memory/latency bounded
            if len(df) > sample_rows:
                df = df.sample(sample_rows, random_state=42)
                
            # Process column types
            df = DataLoader.infer_dtypes(df)
                
            return df.reset_index(drop=True)
            
        except Exception as e:
            print(f"Error loading data from {path}: {str(e)}")
            # Return an empty DataFrame with a message column
            return pd.DataFrame({"error_message": [f"Failed to load data: {str(e)}"]})
        
    @staticmethod
    def parse_datetime(series):
        """
        Parse datetime with appropriate format while suppressing warnings.
        """
        # Skip if already datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return series
            
        # Suppress warnings and use dateutil parser
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return pd.to_datetime(series, errors='coerce')

    @staticmethod
    def infer_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Attempt to infer correct data types for all columns."""
        for col in df.columns:
            # Skip columns that are already numeric or datetime
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
                
            # Try to convert to numeric
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if numeric_series.notna().sum() > 0.8 * df[col].count():  # Over 80% valid numbers
                df[col] = numeric_series
                continue
                
            # Try to convert to datetime - with warnings suppressed
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    datetime_series = pd.to_datetime(df[col], errors='coerce')
                if datetime_series.notna().sum() > 0.8 * df[col].count():  # Over 80% valid dates
                    df[col] = datetime_series
                    continue
            except:
                pass
                
        return df