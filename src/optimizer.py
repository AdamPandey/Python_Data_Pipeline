import logging
import pandas as pd
import numpy as np
logger = logging.getLogger("DataPipelineEngine")

class MemoryOptimizationEngine:
    @staticmethod
    def optimize_dataframe_layout(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimizes internal column storage types, converting objects to categories
        and downcasting numerical types safely without type-matching mismatches.
        """
        start_mem = df.memory_usage(deep=True).sum() / (1024 ** 2)
        
        for col in df.columns:
            # Explicitly check if the column is purely numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                c_min = df[col].min()
                c_max = df[col].max()
                
                if pd.api.types.is_integer_dtype(df[col]):
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                else:
                    # Safely compress floating point boundaries
                    if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
            else:
                # Column is non-numeric (strings, objects, mixed dictionary data)
                num_unique_values = len(df[col].unique())
                num_total_values = len(df[col])
                # Compress repeating structural values into memory-saving categories
                if num_unique_values / num_total_values < 0.5:
                    df[col] = df[col].astype('category')

        end_mem = df.memory_usage(deep=True).sum() / (1024 ** 2)
        logger.info(f"Optimized layout footprint from {start_mem:.2f}MB to {end_mem:.2f}MB.")
        return df