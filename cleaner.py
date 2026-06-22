import pandas as pd
import numpy as np

def fill_missing(df: pd.DataFrame, column: str, strategy: str, custom_value=None) -> pd.DataFrame:
    """
    Fills missing values in a dataframe column based on a specified strategy.
    """
    df_copy = df.copy()
    if column not in df_copy.columns:
        return df_copy
    
    if strategy == "Mean":
        # Convert to numeric if possible before mean
        val = pd.to_numeric(df_copy[column], errors='coerce').mean()
        df_copy[column] = df_copy[column].fillna(val)
    elif strategy == "Median":
        val = pd.to_numeric(df_copy[column], errors='coerce').median()
        df_copy[column] = df_copy[column].fillna(val)
    elif strategy == "Mode":
        mode_val = df_copy[column].mode()
        if not mode_val.empty:
            df_copy[column] = df_copy[column].fillna(mode_val[0])
    elif strategy == "Constant Value":
        if custom_value is not None:
            # Try to cast custom value to column type
            try:
                col_type = df_copy[column].dtype
                if np.issubdtype(col_type, np.number):
                    # Check if integer or float
                    if np.issubdtype(col_type, np.integer):
                        typed_val = int(custom_value)
                    else:
                        typed_val = float(custom_value)
                else:
                    typed_val = str(custom_value)
                df_copy[column] = df_copy[column].fillna(typed_val)
            except ValueError:
                # Fallback to string if casting fails
                df_copy[column] = df_copy[column].fillna(str(custom_value))
    elif strategy == "Forward Fill":
        df_copy[column] = df_copy[column].ffill()
    elif strategy == "Backward Fill":
        df_copy[column] = df_copy[column].bfill()
        
    return df_copy

def drop_missing(df: pd.DataFrame, target: str, subset_cols=None) -> pd.DataFrame:
    """
    Drops rows or columns containing missing values.
    target: "Rows with ANY missing values", "Rows with ALL missing values", "Columns with ANY missing values"
    """
    df_copy = df.copy()
    if target == "Rows with ANY missing values":
        df_copy = df_copy.dropna(how='any', subset=subset_cols)
    elif target == "Rows with ALL missing values":
        df_copy = df_copy.dropna(how='all', subset=subset_cols)
    elif target == "Columns with ANY missing values":
        df_copy = df_copy.dropna(axis=1, how='any')
    return df_copy

def drop_duplicates(df: pd.DataFrame, subset_cols=None, keep="first") -> pd.DataFrame:
    """
    Removes duplicate rows.
    """
    df_copy = df.copy()
    return df_copy.drop_duplicates(subset=subset_cols, keep=keep)

def drop_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Drops list of columns.
    """
    df_copy = df.copy()
    existing_cols = [c for c in columns if c in df_copy.columns]
    return df_copy.drop(columns=existing_cols)

def convert_type(df: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
    """
    Converts a column's data type.
    """
    df_copy = df.copy()
    if column not in df_copy.columns:
        return df_copy
    
    try:
        if target_type == "Integer":
            df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce').astype('Int64')
        elif target_type == "Float":
            df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce').astype(float)
        elif target_type == "String/Text":
            df_copy[column] = df_copy[column].astype(str)
        elif target_type == "Datetime":
            df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
        elif target_type == "Categorical":
            df_copy[column] = df_copy[column].astype('category')
        elif target_type == "Boolean":
            # Map string common representations
            def parse_bool(val):
                if pd.isna(val):
                    return np.nan
                s = str(val).strip().lower()
                if s in ('true', '1', '1.0', 'yes', 't', 'y'):
                    return True
                if s in ('false', '0', '0.0', 'no', 'f', 'n'):
                    return False
                return np.nan
            df_copy[column] = df_copy[column].apply(parse_bool).astype('boolean')
    except Exception as e:
        raise ValueError(f"Failed to convert column '{column}' to {target_type}: {str(e)}")
        
    return df_copy

def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> pd.DataFrame:
    """
    Renames a column in the DataFrame.
    """
    df_copy = df.copy()
    if old_name in df_copy.columns and new_name:
        df_copy = df_copy.rename(columns={old_name: new_name})
    return df_copy

def filter_rows(df: pd.DataFrame, column: str, condition: str, value: str) -> pd.DataFrame:
    """
    Filters rows based on a simple comparison condition.
    """
    df_copy = df.copy()
    if column not in df_copy.columns:
        return df_copy
    
    col_data = df_copy[column]
    
    # Try to convert value to matching type
    try:
        if np.issubdtype(col_data.dtype, np.number):
            typed_val = float(value)
            col_compare = pd.to_numeric(col_data, errors='coerce')
        elif isinstance(col_data.dtype, pd.DatetimeTZDtype) or np.issubdtype(col_data.dtype, np.datetime64):
            typed_val = pd.to_datetime(value)
            col_compare = pd.to_datetime(col_data, errors='coerce')
        else:
            typed_val = str(value)
            col_compare = col_data.astype(str)
    except Exception:
        # Fall back to string comparison
        typed_val = str(value)
        col_compare = col_data.astype(str)

    if condition == "Equals":
        return df_copy[col_compare == typed_val]
    elif condition == "Not Equals":
        return df_copy[col_compare != typed_val]
    elif condition == "Greater Than":
        return df_copy[col_compare > typed_val]
    elif condition == "Less Than":
        return df_copy[col_compare < typed_val]
    elif condition == "Greater Than or Equal":
        return df_copy[col_compare >= typed_val]
    elif condition == "Less Than or Equal":
        return df_copy[col_compare <= typed_val]
    elif condition == "Contains":
        return df_copy[col_data.astype(str).str.contains(str(value), case=False, na=False)]
    elif condition == "Does Not Contain":
        return df_copy[~col_data.astype(str).str.contains(str(value), case=False, na=False)]
    
    return df_copy
