"""
Explore schemas visually, toggle database dialects, construct SQL query statements dynamically, and view mocked execution results.
"""

import streamlit as st

# Back button to return to dashboard
col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Return to Labs Dashboard", use_container_width=True):
        st.switch_page("homepage.py")

st.markdown("""
<div style="padding: 1rem 1.5rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.02) 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; margin-top: 1rem; margin-bottom: 1.5rem;">
    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #FFFFFF;">🛠️ SQL Query Builder & Runner</h2>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #94A3B8;">Visual schema explorer and SQL query generator (Coming Soon).</p>
</div>
""", unsafe_allow_html=True)

# Interactive Mock Interface
st.markdown("### 🗄️ Visual Query Configurator")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Database Schema")
    dialect = st.selectbox("Dialect:", ["PostgreSQL", "MySQL", "SQLite", "Snowflake"], key="page_sql_dialect")
    
    st.markdown("**Tables**")
    table = st.selectbox("Select Target Table:", ["users", "orders", "products", "transactions"], key="page_sql_table")
    
    st.markdown("**Columns to Select**")
    if table == "users":
        st.checkbox("id (INT)", value=True, key="page_sql_user_id")
        st.checkbox("email (VARCHAR)", value=True, key="page_sql_user_email")
        st.checkbox("created_at (TIMESTAMP)", value=False, key="page_sql_user_created")
        st.checkbox("status (VARCHAR)", value=True, key="page_sql_user_status")
    elif table == "orders":
        st.checkbox("order_id (INT)", value=True, key="page_sql_order_id")
        st.checkbox("user_id (INT)", value=True, key="page_sql_order_uid")
        st.checkbox("amount (DECIMAL)", value=True, key="page_sql_order_amt")
        st.checkbox("order_date (DATE)", value=True, key="page_sql_order_date")
        
    st.markdown("**Filter Conditions**")
    st.text_input("WHERE Clause:", placeholder="status = 'active'", key="page_sql_where")
    
with col2:
    st.subheader("Generated SQL Statement")
    
    # Build mock query
    cols_str = "*"
    if table == "users":
        cols_str = "id, email, status"
    elif table == "orders":
        cols_str = "order_id, user_id, amount, order_date"
        
    mock_sql = f"SELECT {cols_str}\nFROM {table}\nWHERE status = 'active'\nLIMIT 100;"
    st.code(mock_sql, language="sql")
    
    st.info("ℹ️ SQL execution runner is currently a mockup. In the future, this app will connect to database credentials and display results in real-time.")
    
    st.button("⚡ Run Query (Mocked)", disabled=True, key="page_sql_run_btn")
