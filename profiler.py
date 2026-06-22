import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_overall_metrics(df: pd.DataFrame) -> dict:
    """
    Returns a dictionary of overall dataset statistics.
    """
    total_cells = df.size
    total_missing = df.isna().sum().sum()
    pct_missing = (total_missing / total_cells * 100) if total_cells > 0 else 0
    
    # Estimate memory usage
    try:
        memory_usage_bytes = df.memory_usage(deep=True).sum()
        if memory_usage_bytes < 1024:
            memory_str = f"{memory_usage_bytes} B"
        elif memory_usage_bytes < 1024 * 1024:
            memory_str = f"{memory_usage_bytes / 1024:.2f} KB"
        else:
            memory_str = f"{memory_usage_bytes / (1024 * 1024):.2f} MB"
    except Exception:
        memory_str = "Unknown"
        
    num_duplicates = df.duplicated().sum()
    
    return {
        "num_rows": df.shape[0],
        "num_cols": df.shape[1],
        "total_cells": total_cells,
        "total_missing": total_missing,
        "pct_missing": round(pct_missing, 2),
        "num_duplicates": num_duplicates,
        "memory_usage": memory_str
    }

def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a summary DataFrame containing metrics for each column.
    """
    summary_data = []
    
    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        non_null_count = series.count()
        null_count = series.isna().sum()
        pct_null = (null_count / len(df) * 100) if len(df) > 0 else 0
        num_unique = series.nunique()
        
        # Determine sample/top values
        if num_unique > 0:
            top_val = series.value_counts().index[0]
            top_freq = series.value_counts().values[0]
            top_info = f"{top_val} ({top_freq}x)"
        else:
            top_info = "N/A"
            
        summary_data.append({
            "Column Name": col,
            "Data Type": dtype,
            "Filled Rows": non_null_count,
            "Missing Rows": null_count,
            "Missing %": round(pct_null, 2),
            "Unique Values": num_unique,
            "Most Frequent Value": top_info
        })
        
    return pd.DataFrame(summary_data)

def plot_missing_values(df: pd.DataFrame) -> go.Figure:
    """
    Generates a bar chart showing the percentage of missing values per column.
    """
    null_counts = df.isna().sum()
    pct_null = (null_counts / len(df) * 100) if len(df) > 0 else pd.Series(0, index=df.columns)
    
    missing_df = pd.DataFrame({
        "Column": df.columns,
        "Missing %": pct_null.values,
        "Missing Count": null_counts.values
    }).sort_values(by="Missing %", ascending=True)
    
    # Filter to only show columns with missing values if they exist, or show all if empty
    # For visualization, it's nice to see all columns if there are few, or only missing ones if many.
    fig = px.bar(
        missing_df,
        y="Column",
        x="Missing %",
        orientation="h",
        text="Missing Count",
        labels={"Missing %": "Missing (%)", "Column": "Column Name"},
        title="Missing Values by Column (%)",
        color="Missing %",
        color_continuous_scale="Purples"
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E6ED", family="Inter, sans-serif"),
        title_font=dict(size=16, color="#FFFFFF"),
        xaxis=dict(showgrid=True, gridcolor="#2D3139", range=[0, 100]),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False,
        height=max(300, len(df.columns) * 25)
    )
    
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(width=0))
    )
    
    return fig

def plot_column_distribution(df: pd.DataFrame, col: str) -> go.Figure:
    """
    Plots the distribution of a single column depending on its data type.
    """
    series = df[col].dropna()
    if len(series) == 0:
        # Return empty placeholder figure
        fig = go.Figure()
        fig.add_annotation(text="No data to plot", showarrow=False, font=dict(size=16))
        return fig
        
    # Check if numeric
    if np.issubdtype(series.dtype, np.number):
        # Numeric distribution: Histogram + Box Plot
        fig = px.histogram(
            df,
            x=col,
            marginal="box",
            title=f"Distribution of {col}",
            color_discrete_sequence=["#8B5CF6"] # Violet
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E6ED", family="Inter, sans-serif"),
            title_font=dict(size=16, color="#FFFFFF"),
            xaxis=dict(showgrid=True, gridcolor="#2D3139"),
            yaxis=dict(showgrid=True, gridcolor="#2D3139"),
            bargap=0.05
        )
    elif isinstance(series.dtype, pd.DatetimeTZDtype) or np.issubdtype(series.dtype, np.datetime64):
        # Datetime timeline count
        # Resample or just count by date
        dates = pd.to_datetime(series).dt.date.value_counts().sort_index().reset_index()
        dates.columns = ["Date", "Count"]
        
        fig = px.line(
            dates,
            x="Date",
            y="Count",
            title=f"Occurrences Over Time for {col}",
            color_discrete_sequence=["#10B981"] # Emerald/Teal
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E6ED", family="Inter, sans-serif"),
            title_font=dict(size=16, color="#FFFFFF"),
            xaxis=dict(showgrid=True, gridcolor="#2D3139"),
            yaxis=dict(showgrid=True, gridcolor="#2D3139")
        )
    else:
        # Categorical / String distribution: Bar chart of top 15 categories
        value_counts = series.astype(str).value_counts().head(15).reset_index()
        value_counts.columns = ["Value", "Frequency"]
        
        fig = px.bar(
            value_counts,
            y="Value",
            x="Frequency",
            orientation="h",
            title=f"Top 15 Most Common Values in {col}",
            color="Frequency",
            color_continuous_scale="Viridis",
            labels={"Value": col, "Frequency": "Count"}
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E6ED", family="Inter, sans-serif"),
            title_font=dict(size=16, color="#FFFFFF"),
            xaxis=dict(showgrid=True, gridcolor="#2D3139"),
            yaxis=dict(showgrid=False),
            coloraxis_showscale=False
        )
        fig.update_traces(marker=dict(line=dict(width=0)))
        
    return fig

def plot_correlation_matrix(df: pd.DataFrame) -> go.Figure:
    """
    Plots a Pearson correlation matrix for numeric columns in the DataFrame.
    """
    # Select numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.shape[1] < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 2 numeric columns for correlation matrix", 
            showarrow=False, 
            font=dict(size=14, color="#A0AEC0")
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E6ED", family="Inter, sans-serif")
        )
        return fig
        
    corr = numeric_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Correlation"),
        hovertemplate="Col 1: %{x}<br>Col 2: %{y}<br>Correlation: %{z:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Numeric Column Correlation Matrix",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E6ED", family="Inter, sans-serif"),
        title_font=dict(size=16, color="#FFFFFF"),
        xaxis=dict(gridcolor="#2D3139"),
        yaxis=dict(gridcolor="#2D3139"),
        width=600,
        height=550
    )
    
    return fig

def create_sample_data() -> pd.DataFrame:
    """
    Creates a messy DataFrame for testing and demonstration.
    """
    data = {
        "ID": [101, 102, 103, 104, 105, 105, 107, 108, 109, 110],
        "Name": ["  Alice Smith ", "Bob Jones", "Charlie Brown", "Diana Prince", "Evan Wright", "Evan Wright", "Fiona Gallagher", None, "Hannah Abbott", "Ian Malcolm"],
        "Age": [25.0, 30.0, np.nan, 28.0, 35.0, 35.0, -5.0, 42.0, np.nan, 250.0],
        "Email": ["alice@example.com", "bob@example.com", "charlie@example", "diana@example.com", "evan@example.com", "evan@example.com", "fiona@example.com", "ghost@example.com", np.nan, "ian@example.com"],
        "Joined Date": ["2023-01-15", "02/20/2023", "2023-03-10", None, "2022-11-05", "2022-11-05", "March 12, 2023", "2023-05-01", "2023-06-18", "invalid_date"],
        "Salary": ["$85,000", "$92,000", np.nan, "$78,500", "$105,000", "$105,000", "$62,000", "$80,000", "$95,000", "$120,000"],
        "Department": ["Engineering", "sales", "Marketing", "HR", "Engineering", "Engineering", "Support", "Marketing", None, "Engineering"],
        "Active": ["Yes", "No", "yes", "Y", "True", "True", "No", "N", "False", None]
    }
    return pd.DataFrame(data)

