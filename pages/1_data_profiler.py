"""
Inspect rows and columns, generate visual diagnostics with interactive Plotly graphs, edit cells directly in the browser spreadsheet, and clean/export datasets.
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
import os

# Add parent directory to sys.path so we can import profiler and cleaner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import profiler
import cleaner

# Initialize Session State for Cleaner
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'original_df' not in st.session_state:
    st.session_state['original_df'] = None
if 'df_history' not in st.session_state:
    st.session_state['df_history'] = []
if 'clean_actions' not in st.session_state:
    st.session_state['clean_actions'] = []
if 'active_file_name' not in st.session_state:
    st.session_state['active_file_name'] = ""

# Back button to return to dashboard
col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Return to Labs Dashboard", use_container_width=True):
        st.switch_page("homepage.py")

# --- SIDEBAR: Brand & Controls ---
with st.sidebar:
    st.markdown('<div class="labs-tag">mikemurray.net / labs</div>', unsafe_allow_html=True)
    st.markdown('## 🔮 Raw Profiler & Cleaner', unsafe_allow_html=True)
    st.markdown('---')
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload dataset (CSV or Excel)", 
        type=["csv", "xlsx", "xls"],
        help="Drag and drop a file or browse. Maximum size 200MB.",
        key="page_file_uploader"
    )
    
    # Read file when uploaded
    if uploaded_file is not None:
        try:
            # Only read if name is different or not yet initialized
            if st.session_state['active_file_name'] != uploaded_file.name:
                if uploaded_file.name.endswith('.csv'):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    raw_df = pd.read_excel(uploaded_file)
                
                st.session_state['df'] = raw_df.copy()
                st.session_state['original_df'] = raw_df.copy()
                st.session_state['df_history'] = []
                st.session_state['clean_actions'] = []
                st.session_state['active_file_name'] = uploaded_file.name
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
            
    # Load Sample Dataset button (only if no dataset loaded or as alternative)
    st.markdown("### 💡 Quick Testing")
    if st.button("🚀 Load Sample Messy Dataset", use_container_width=True, key="page_load_sample_btn"):
        raw_df = profiler.create_sample_data()
        st.session_state['df'] = raw_df.copy()
        st.session_state['original_df'] = raw_df.copy()
        st.session_state['df_history'] = []
        st.session_state['clean_actions'] = []
        st.session_state['active_file_name'] = "sample_messy_data.csv"
        st.rerun()

    # Active State Controls
    if st.session_state['df'] is not None:
        st.markdown('---')
        st.markdown("### 🛠️ Active History")
        
        # Undo button
        has_history = len(st.session_state['df_history']) > 0
        if st.button("↩️ Undo Last Step", disabled=not has_history, use_container_width=True, key="page_undo_btn"):
            st.session_state['df'] = st.session_state['df_history'].pop()
            st.session_state['clean_actions'].pop()
            st.rerun()
            
        # Reset button
        is_modified = not st.session_state['df'].equals(st.session_state['original_df'])
        if st.button("🔄 Reset to Original", disabled=not is_modified, use_container_width=True, key="page_reset_btn"):
            st.session_state['df'] = st.session_state['original_df'].copy()
            st.session_state['df_history'] = []
            st.session_state['clean_actions'] = []
            st.rerun()
            
        # Show audit log
        if st.session_state['clean_actions']:
            with st.expander("📝 Applied Changes Log", expanded=True):
                for idx, action in enumerate(st.session_state['clean_actions']):
                    st.markdown(f'<div class="action-badge">{idx+1}. {action}</div>', unsafe_allow_html=True)

# Sub-App Header
st.markdown("""
<div style="padding: 1rem 1.5rem; background: linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(99, 102, 241, 0.02) 100%); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 12px; margin-top: 1rem; margin-bottom: 1.5rem;">
    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #FFFFFF;">📊 Raw Data Profiler & Cleaner</h2>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #94A3B8;">Diagnostics, interactive editing, and automated processing.</p>
</div>
""", unsafe_allow_html=True)

if st.session_state['df'] is None:
    # --- Landing Page / Empty State ---
    st.markdown("""
    <div class="card-panel" style="text-align: center; padding: 3rem;">
        <h2 style="color: #FFFFFF; font-weight: 600; margin-bottom: 1rem;">No Dataset Loaded</h2>
        <p style="color: #94A3B8; max-width: 600px; margin: 0 auto 2rem; font-size: 1.1rem; line-height: 1.6;">
            To begin, upload a CSV or Excel file via the sidebar on the left, or load the built-in sample messy dataset to explore the tool's features immediately.
        </p>
        <div style="display: flex; justify-content: center; gap: 1.5rem;">
            <div class="metric-card" style="max-width: 250px;">
                <div class="metric-card-title">📊 Instant Metrics</div>
                <div class="metric-card-sub">Generate dataset health grades, check duplicates, and analyze missing data fields.</div>
            </div>
            <div class="metric-card" style="max-width: 250px;">
                <div class="metric-card-title">✏️ Browser Spreadsheet</div>
                <div class="metric-card-sub">Edit cells, add rows, and delete records directly inside a live interactive grid.</div>
            </div>
            <div class="metric-card" style="max-width: 250px;">
                <div class="metric-card-title">🧹 Auto-Clean</div>
                <div class="metric-card-sub">Impute nulls, remove duplicates, change data types, and filter records effortlessly.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Dataset is loaded, let's load helper metrics
    df = st.session_state['df']
    metrics = profiler.get_overall_metrics(df)
    
    # Display overall metrics
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    cols = st.columns(5)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Rows</div>
            <div class="metric-card-value">{metrics['num_rows']:,}</div>
            <div class="metric-card-sub">Total records</div>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Columns</div>
            <div class="metric-card-value">{metrics['num_cols']:,}</div>
            <div class="metric-card-sub">Total variables</div>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Missing Cells</div>
            <div class="metric-card-value">{metrics['total_missing']:,}</div>
            <div class="metric-card-sub">{metrics['pct_missing']}% of total data</div>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Duplicate Rows</div>
            <div class="metric-card-value">{metrics['num_duplicates']:,}</div>
            <div class="metric-card-sub">Identical rows</div>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[4]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Memory Size</div>
            <div class="metric-card-value">{metrics['memory_usage']}</div>
            <div class="metric-card-sub">RAM footprint</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Tabbed Navigation System ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Data Health & Overview",
        "🔍 Column Deep-Dive",
        "✏️ Interactive Spreadsheet",
        "🧹 Smart Cleaning Tools",
        "💾 Export Cleaned Data"
    ])
    
    # --- TAB 1: OVERVIEW & GENERAL DIAGNOSTICS ---
    with tab1:
        st.markdown("### 📊 High-Level Diagnostics")
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("#### Column Metadata & Status")
            col_summary = profiler.get_column_summary(df)
            st.dataframe(
                col_summary,
                use_container_width=True,
                hide_index=True
            )
            
        with col_right:
            st.markdown("#### Null Value Densities")
            if metrics['total_missing'] > 0:
                missing_chart = profiler.plot_missing_values(df)
                st.plotly_chart(missing_chart, use_container_width=True)
            else:
                st.info("🎉 Clean dataset! No missing values detected in any column.")
                
            # Numeric Correlation Matrix
            st.markdown("#### Correlation Matrix")
            corr_chart = profiler.plot_correlation_matrix(df)
            st.plotly_chart(corr_chart, use_container_width=True)
            
    # --- TAB 2: COLUMN DEEP-DIVE ---
    with tab2:
        st.markdown("### 🔍 Column-Specific Diagnostics")
        
        selected_col = st.selectbox("Select column to analyze:", options=df.columns, key="deep_dive_col_select")
        
        if selected_col:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"#### Profile: `{selected_col}`")
                
                col_series = df[selected_col]
                null_cnt = col_series.isna().sum()
                unique_cnt = col_series.nunique()
                
                stats_data = {
                    "Metric": ["Data Type", "Filled Values", "Missing Values", "Missing %", "Unique Values"],
                    "Value": [
                        str(col_series.dtype),
                        f"{col_series.count():,}",
                        f"{null_cnt:,}",
                        f"{(null_cnt / len(df) * 100):.2f}%",
                        f"{unique_cnt:,}"
                    ]
                }
                st.table(pd.DataFrame(stats_data))
                
                # Descriptive Stats
                st.markdown("#### Summary Statistics")
                try:
                    desc = col_series.describe(datetime_is_numeric=True).reset_index()
                    desc.columns = ["Statistic", "Value"]
                    st.dataframe(desc, use_container_width=True, hide_index=True)
                except Exception:
                    desc = col_series.describe().reset_index()
                    desc.columns = ["Statistic", "Value"]
                    st.dataframe(desc, use_container_width=True, hide_index=True)
                    
            with col2:
                # Plot distribution
                dist_chart = profiler.plot_column_distribution(df, selected_col)
                st.plotly_chart(dist_chart, use_container_width=True)
                
    # --- TAB 3: INTERACTIVE BROWSER SPREADSHEET ---
    with tab3:
        st.markdown("### ✏️ Live Interactive Spreadsheet")
        st.caption("Double-click any cell to edit it, or use the bottom grid controls to add/remove rows. All edits update data metrics in real-time.")
        
        # Grid component
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor_grid"
        )
        
        # Compare and update state if edited
        if not edited_df.equals(df):
            st.session_state['df_history'].append(df.copy())
            st.session_state['df'] = edited_df
            st.session_state['clean_actions'].append("Manually edited cells in spreadsheet")
            st.rerun()
            
    # --- TAB 4: SMART CLEANING TOOLS ---
    with tab4:
        st.markdown("### 🧹 Automated Cleaning Tools")
        st.write("Perform bulk operations across columns or rows. All changes are logged and can be undone.")
        
        grid_cols = st.columns(2)
        
        # COLUMN A: NULLS AND DUPLICATES
        with grid_cols[0]:
            # Imputation Expander
            with st.expander("🩹 Fill Missing Values (Imputation)", expanded=True):
                impute_col = st.selectbox("Select column to impute:", options=df.columns, key="impute_col_select")
                impute_strat = st.selectbox(
                    "Select imputation strategy:", 
                    ["Mean", "Median", "Mode", "Constant Value", "Forward Fill", "Backward Fill"],
                    key="impute_strat_select"
                )
                
                custom_val = None
                if impute_strat == "Constant Value":
                    custom_val = st.text_input("Enter constant value:", key="impute_custom_val")
                    
                if st.button("Apply Imputation", key="apply_impute_btn", use_container_width=True):
                    try:
                        new_df = cleaner.fill_missing(df, impute_col, impute_strat, custom_val)
                        st.session_state['df_history'].append(df.copy())
                        st.session_state['df'] = new_df
                        st.session_state['clean_actions'].append(f"Imputed missing in '{impute_col}' via {impute_strat}")
                        st.success(f"Filled missing values in '{impute_col}'!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Imputation failed: {str(ex)}")
                        
            # Remove Duplicates Expander
            with st.expander("👯 Remove Duplicate Rows", expanded=False):
                st.write("Deduplicate dataset rows based on unique column keys.")
                dup_cols = st.multiselect(
                    "Deduplicate by specific columns (leave empty for all columns):", 
                    options=df.columns,
                    key="dup_cols_multiselect"
                )
                keep_strat = st.selectbox("Duplicate instance to keep:", ["first", "last"], key="keep_strat_select")
                
                if st.button("Deduplicate Dataset", key="apply_dedup_btn", use_container_width=True):
                    subset_val = dup_cols if dup_cols else None
                    original_len = len(df)
                    new_df = cleaner.drop_duplicates(df, subset_cols=subset_val, keep=keep_strat)
                    dropped_cnt = original_len - len(new_df)
                    
                    st.session_state['df_history'].append(df.copy())
                    st.session_state['df'] = new_df
                    st.session_state['clean_actions'].append(f"Removed {dropped_cnt} duplicates (kept {keep_strat})")
                    st.success(f"Successfully removed {dropped_cnt} duplicate rows!")
                    st.rerun()
                    
            # Row Filtering Expander
            with st.expander("🔍 Filter Rows by Condition", expanded=False):
                filter_col = st.selectbox("Select column to filter:", options=df.columns, key="filter_col_select")
                filter_cond = st.selectbox(
                    "Select condition:", 
                    ["Equals", "Not Equals", "Greater Than", "Less Than", "Greater Than or Equal", "Less Than or Equal", "Contains", "Does Not Contain"],
                    key="filter_cond_select"
                )
                filter_val = st.text_input("Enter value to compare:", key="filter_val_input")
                
                if st.button("Apply Filter", key="apply_filter_btn", use_container_width=True):
                    try:
                        original_len = len(df)
                        new_df = cleaner.filter_rows(df, filter_col, filter_cond, filter_val)
                        removed_cnt = original_len - len(new_df)
                        
                        st.session_state['df_history'].append(df.copy())
                        st.session_state['df'] = new_df
                        st.session_state['clean_actions'].append(f"Filtered rows: {filter_col} {filter_cond} '{filter_val}' ({removed_cnt} dropped)")
                        st.success(f"Filter applied! Dropped {removed_cnt} rows.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Filtering error: {str(ex)}")

        # COLUMN B: TYPE CASTS AND COLUMN OPERATIONS
        with grid_cols[1]:
            # Type Casting Expander
            with st.expander("🔄 Cast Column Data Types", expanded=True):
                cast_col = st.selectbox("Select column to cast:", options=df.columns, key="cast_col_select")
                target_type = st.selectbox(
                    "Select target type:",
                    ["Integer", "Float", "String/Text", "Datetime", "Categorical", "Boolean"],
                    key="cast_type_select"
                )
                
                if st.button("Cast Data Type", key="apply_cast_btn", use_container_width=True):
                    try:
                        new_df = cleaner.convert_type(df, cast_col, target_type)
                        st.session_state['df_history'].append(df.copy())
                        st.session_state['df'] = new_df
                        st.session_state['clean_actions'].append(f"Casted '{cast_col}' to {target_type}")
                        st.success(f"Successfully casted '{cast_col}' to {target_type}!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Casting failed: {str(ex)}")
                        
            # Column Management Expander
            with st.expander("📋 Column Operations (Rename / Drop)", expanded=False):
                sub_tab1, sub_tab2 = st.tabs(["Rename Column", "Drop Columns"])
                
                with sub_tab1:
                    rename_col_select = st.selectbox("Select column to rename:", options=df.columns, key="rename_col_select")
                    new_col_name = st.text_input("Enter new column name:", key="rename_col_input")
                    if st.button("Rename Column", key="apply_rename_btn", use_container_width=True):
                        if new_col_name.strip():
                            new_df = cleaner.rename_column(df, rename_col_select, new_col_name.strip())
                            st.session_state['df_history'].append(df.copy())
                            st.session_state['df'] = new_df
                            st.session_state['clean_actions'].append(f"Renamed column '{rename_col_select}' to '{new_col_name}'")
                            st.success(f"Renamed column to '{new_col_name}'!")
                            st.rerun()
                        else:
                            st.warning("Please provide a valid new name.")
                            
                with sub_tab2:
                    drop_cols_select = st.multiselect("Select columns to drop:", options=df.columns, key="drop_cols_multiselect")
                    if st.button("Drop Selected Columns", key="apply_drop_btn", use_container_width=True):
                        if drop_cols_select:
                            new_df = cleaner.drop_columns(df, drop_cols_select)
                            st.session_state['df_history'].append(df.copy())
                            st.session_state['df'] = new_df
                            st.session_state['clean_actions'].append(f"Dropped column(s): {', '.join(drop_cols_select)}")
                            st.success(f"Dropped {len(drop_cols_select)} columns!")
                            st.rerun()
                        else:
                            st.warning("Please select at least one column to drop.")
                            
            # Drop Missing Values Expander
            with st.expander("🗑️ Drop Rows/Columns with Missing Values", expanded=False):
                drop_missing_target = st.selectbox(
                    "Drop strategy:",
                    ["Rows with ANY missing values", "Rows with ALL missing values", "Columns with ANY missing values"],
                    key="drop_missing_strategy_select"
                )
                
                # If rows, let them filter by a subset of columns optionally
                subset_drop = None
                if "Rows" in drop_missing_target:
                    subset_drop = st.multiselect(
                        "Restrict check to specific columns (optional, default all):",
                        options=df.columns,
                        key="subset_drop_missing"
                    )
                    
                if st.button("Execute Drop Missing", key="apply_drop_missing_btn", use_container_width=True):
                    original_shape = df.shape
                    new_df = cleaner.drop_missing(df, drop_missing_target, subset_cols=subset_drop if subset_drop else None)
                    
                    st.session_state['df_history'].append(df.copy())
                    st.session_state['df'] = new_df
                    
                    # Log message
                    if "Rows" in drop_missing_target:
                        diff = original_shape[0] - new_df.shape[0]
                        msg = f"Dropped {diff} rows with missing values"
                    else:
                        diff = original_shape[1] - new_df.shape[1]
                        msg = f"Dropped {diff} columns with missing values"
                        
                    st.session_state['clean_actions'].append(msg)
                    st.success(f"Completed! {msg}.")
                    st.rerun()

    # --- TAB 5: DOWNLOAD & EXPORT ---
    with tab5:
        st.markdown("### 💾 Export Cleaned Dataset")
        st.write("Compare the dimensions and download your processed dataset in CSV or Excel format.")
        
        # Compare scorecard
        comp_df = st.session_state['original_df']
        
        st.markdown("#### Comparison Metrics")
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            st.markdown("""
            <div class="card-panel">
                <h4 style="margin: 0 0 1rem 0; color: #94A3B8;">Original Dataset</h4>
                <table style="width:100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); text-align:left;">Rows</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); text-align:left;">Columns</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); text-align:left;">Null Cells</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; text-align:left;">Duplicate Rows</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                </table>
            </div>
            """.format(
                comp_df.shape[0], 
                comp_df.shape[1], 
                comp_df.isna().sum().sum(), 
                comp_df.duplicated().sum()
            ), unsafe_allow_html=True)
            
        with col_comp2:
            st.markdown("""
            <div class="card-panel" style="border-color: rgba(139, 92, 246, 0.3);">
                <h4 style="margin: 0 0 1rem 0; color: #A78BFA;">Current Cleaned Dataset</h4>
                <table style="width:100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); color:#A78BFA; text-align:left;">Rows</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); color:#A78BFA; text-align:left;">Columns</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; border-bottom:1px solid rgba(255,255,255,0.05); color:#A78BFA; text-align:left;">Null Cells</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                    <tr><td style="padding: 8px 0; color:#A78BFA; text-align:left;">Duplicate Rows</td><td style="text-align:right; font-weight:bold;">{:,}</td></tr>
                </table>
            </div>
            """.format(
                df.shape[0], 
                df.shape[1], 
                df.isna().sum().sum(), 
                df.duplicated().sum()
            ), unsafe_allow_html=True)
            
        # Export Actions
        st.markdown("#### Select Export Format")
        export_col1, export_col2 = st.columns(2)
        
        # Generate CSV bytes
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')
        except Exception as e:
            csv_data = None
            st.error(f"Error generating CSV: {e}")
            
        with export_col1:
            st.markdown('<div class="card-panel" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown("##### Comma Separated Values (.csv)")
            st.caption("Standard text-based format for broad compatibility.")
            if csv_data:
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv_data,
                    file_name=f"cleaned_{st.session_state['active_file_name'] or 'dataset.csv'}",
                    mime="text/csv",
                    use_container_width=True,
                    key="page_csv_download_btn"
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Generate Excel bytes
        try:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_data = excel_buffer.getvalue()
        except Exception as e:
            excel_data = None
            st.error(f"Error generating Excel: {e}")
            
        with export_col2:
            st.markdown('<div class="card-panel" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown("##### Microsoft Excel Spreadsheet (.xlsx)")
            st.caption("Binary spreadsheet format supporting sheets and typing.")
            if excel_data:
                st.download_button(
                    label="📥 Download Cleaned Excel",
                    data=excel_data,
                    file_name=f"cleaned_{st.session_state['active_file_name'].split('.')[0] or 'dataset'}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="page_excel_download_btn"
                )
            st.markdown('</div>', unsafe_allow_html=True)
