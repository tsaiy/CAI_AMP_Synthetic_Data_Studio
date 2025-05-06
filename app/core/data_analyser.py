import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Any, Union, Optional, Tuple
import math

class DataAnalyser:
    """Utility class for analyzing datasets and providing statistical insights."""
    
    @classmethod
    def analyse(cls, df: pd.DataFrame, correlation_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Analyze a DataFrame and extract useful statistics and insights.
        
        Args:
            df: Input DataFrame to analyze
            correlation_threshold: Threshold for identifying strong correlations
            
        Returns:
            Dictionary containing analysis results
        """
        print("Analyzing data...")
        
        # Initialize results structure
        results = {"columns": [],
            "grp_columns": {},
            "statistical_analysis": {},
            "cross_row_relationship": {},
            "cross_column_relationship": {}
        }
        
        # Categorize columns
        results["grp_columns"] = cls.categorize_columns(df)
        results["columns"]= df.columns.tolist()
        
        # Analyze each type of column
        stats = {}
        if results["grp_columns"]["numeric"]:
            stats["numeric"] = cls.analyze_numeric_columns(df, results["grp_columns"]["numeric"])
        
        if results["grp_columns"]["categorical"]:
            stats["categorical"] = cls.analyze_categorical_columns(df, results["grp_columns"]["categorical"])
        
        if results["grp_columns"]["datetime"]:
            stats["datetime"] = cls.analyze_datetime_columns(df, results["grp_columns"]["datetime"])
        
        results["statistical_analysis"] = stats
        
        # Analyze cross-row relationships
        results["cross_row_relationship"] = cls.analyze_cross_row_relationships(df)
        
        # Analyze cross-column relationships
        if results["grp_columns"]["numeric"] and len(results["grp_columns"]["numeric"]) > 1:
            results["cross_column_relationship"] = cls.analyze_cross_column_relationships(
                df, results["grp_columns"]["numeric"], correlation_threshold
            )
        
        return results
    
    @classmethod
    def categorize_columns(cls, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Categorize DataFrame columns by their data types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary mapping column types to lists of column names
        """
        result = {
            "numeric": [],
            "categorical": [],
            "datetime": [],
            "text": [],
            "other": []
        }
        
        for col in df.columns:
            column = df[col]
            
            # Check if already datetime type - most reliable method
            if pd.api.types.is_datetime64_any_dtype(column):
                result["datetime"].append(col)
            
            # Check numeric types
            elif pd.api.types.is_numeric_dtype(column) and not pd.api.types.is_bool_dtype(column):
                result["numeric"].append(col)
            
            # Check categorical and boolean
            elif pd.api.types.is_categorical_dtype(column) or pd.api.types.is_bool_dtype(column):
                result["categorical"].append(col)
                
            # Check for text columns
            elif pd.api.types.is_string_dtype(column) or pd.api.types.is_object_dtype(column):
                # Check if more than 50% of non-null values are likely categorical (few unique values)
                non_null_count = column.count()
                if non_null_count > 0:
                    unique_ratio = column.nunique() / non_null_count
                    if unique_ratio < 0.2:  # If less than 20% of values are unique, consider categorical
                        result["categorical"].append(col)
                    else:
                        result["text"].append(col)
                else:
                    result["text"].append(col)
                    
            # Everything else
            else:
                result["other"].append(col)
        
        # Verify all columns are categorized
        categorized = []
        for category, cols in result.items():
            categorized.extend(cols)
        
        missing = set(df.columns) - set(categorized)
        if missing:
            print(f"Found uncategorized columns: {missing}")
            result["other"].extend(list(missing))
        
        return result
    
    @classmethod
    def analyze_numeric_columns(cls, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze numeric columns to extract statistical information.
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            
        Returns:
            Dictionary mapping column names to their statistics
        """
        result = {}
        
        for col in numeric_columns:
            # Skip columns with all NaN values
            if df[col].isna().all():
                continue
                
            stats = {}
            
            # Basic statistics
            stats["count"] = int(df[col].count())
            stats["mean"] = float(df[col].mean())
            stats["median"] = float(df[col].median())
            stats["std"] = float(df[col].std())
            stats["min"] = float(df[col].min())
            stats["max"] = float(df[col].max())
            
            # Calculate percentiles
            for p in [25, 75, 90, 95, 99]:
                stats[f"p{p}"] = float(df[col].quantile(p/100))
            
            # Null value statistics
            null_count = int(df[col].isna().sum())
            stats["null_count"] = null_count
            stats["null_percentage"] = float((null_count / len(df)) * 100)
            
            result[col] = stats
        
        return result
    
    @classmethod
    def analyze_categorical_columns(cls, df: pd.DataFrame, categorical_columns: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze categorical columns to extract distribution information.
        
        Args:
            df: Input DataFrame
            categorical_columns: List of categorical column names
            
        Returns:
            Dictionary mapping column names to their statistics
        """
        result = {}
        
        for col in categorical_columns:
            # Skip columns with all NaN values
            if df[col].isna().all():
                continue
                
            stats = {}
            
            # Basic statistics
            stats["count"] = int(df[col].count())
            stats["unique_count"] = int(df[col].nunique())
            
            # Value distribution (top 10 most common values)
            value_counts = df[col].value_counts().head(10).to_dict()
            # Convert any non-string keys to strings for JSON compatibility
            top_values = {}
            for k, v in value_counts.items():
                key = str(k) if not isinstance(k, str) else k
                top_values[key] = int(v)
            
            stats["top_values"] = top_values
            
            # Calculate entropy to measure randomness
            counts = df[col].value_counts()
            probs = counts / counts.sum()
            entropy = -np.sum(probs * np.log2(probs))
            stats["entropy"] = float(entropy)
            
            # Null value statistics
            null_count = int(df[col].isna().sum())
            stats["null_count"] = null_count
            stats["null_percentage"] = float((null_count / len(df)) * 100)
            
            result[col] = stats
        
        return result
    
    @classmethod
    def analyze_datetime_columns(cls, df: pd.DataFrame, datetime_columns: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze datetime columns to extract temporal patterns.
        
        Args:
            df: Input DataFrame
            datetime_columns: List of datetime column names
            
        Returns:
            Dictionary mapping column names to their statistics
        """
        result = {}
        
        for col in datetime_columns:
            # Skip columns with all NaN values
            if df[col].isna().all():
                continue
                
            stats = {}
            
            # Basic statistics
            stats["count"] = int(df[col].count())
            stats["min"] = str(df[col].min())
            stats["max"] = str(df[col].max())
            
            # Calculate temporal span
            min_date = df[col].min()
            max_date = df[col].max()
            if pd.notna(min_date) and pd.notna(max_date):
                span_days = (max_date - min_date).total_seconds() / (60 * 60 * 24)
                stats["span_days"] = float(span_days)
            
            # Extract date parts distribution
            date_parts = {}
            
            # Year distribution
            if df[col].dt.year.nunique() > 1:
                year_counts = df[col].dt.year.value_counts().to_dict()
                date_parts["year"] = {str(k): int(v) for k, v in year_counts.items()}
            
            # Month distribution
            month_counts = df[col].dt.month.value_counts().to_dict()
            date_parts["month"] = {str(k): int(v) for k, v in month_counts.items()}
            
            # Day of week distribution
            dow_counts = df[col].dt.dayofweek.value_counts().to_dict()
            date_parts["day_of_week"] = {str(k): int(v) for k, v in dow_counts.items()}
            
            # Hour distribution (if time component exists)
            if (df[col].dt.hour != 0).any():
                hour_counts = df[col].dt.hour.value_counts().to_dict()
                date_parts["hour"] = {str(k): int(v) for k, v in hour_counts.items()}
            
            stats["date_parts"] = date_parts
            
            # Null value statistics
            null_count = int(df[col].isna().sum())
            stats["null_count"] = null_count
            stats["null_percentage"] = float((null_count / len(df)) * 100)
            
            result[col] = stats
        
        return result
    
    @classmethod
    def analyze_cross_row_relationships(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze relationships across rows, such as duplicates and null patterns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing cross-row relationship information
        """
        result = {}
        
        # Analyze duplicates
        duplicates = df.duplicated()
        duplicate_count = int(duplicates.sum())
        duplicate_percentage = float((duplicate_count / len(df)) * 100)
        
        result["duplicates"] = {
            "count": duplicate_count,
            "percentage": duplicate_percentage
        }
        
        # Analyze rows with null values
        rows_with_null = df.isna().any(axis=1)
        null_rows_count = int(rows_with_null.sum())
        null_rows_percentage = float((null_rows_count / len(df)) * 100)
        
        result["null_rows"] = {
            "count": null_rows_count,
            "percentage": null_rows_percentage
        }
        
        return result
    
    @classmethod
    def analyze_cross_column_relationships(
        cls, df: pd.DataFrame, numeric_columns: List[str], correlation_threshold: float
    ) -> Dict[str, Any]:
        """
        Analyze relationships between columns, such as correlations.
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numeric column names
            correlation_threshold: Threshold for identifying strong correlations
            
        Returns:
            Dictionary containing cross-column relationship information
        """
        result = {}
        
        # Calculate correlations between numeric columns
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            corr_matrix = df[numeric_columns].corr()
        
        # Extract strong correlations (ignore self-correlations)
        strong_correlations = {}
        for i in range(len(numeric_columns)):
            for j in range(i+1, len(numeric_columns)):
                col1 = numeric_columns[i]
                col2 = numeric_columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                # Skip NaN correlations
                if pd.isna(corr_value):
                    continue
                
                # Store absolute correlation values above threshold
                if abs(corr_value) >= correlation_threshold:
                    pair_name = f"{col1} - {col2}"
                    strong_correlations[pair_name] = float(corr_value)
        
        if strong_correlations:
            result["correlations"] = strong_correlations
        
        return result