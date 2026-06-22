"""
Validate structure, minify, or format JSON payloads with clean indentation.
"""

import streamlit as st
import json

# Back button to return to dashboard
col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Return to Labs Dashboard", use_container_width=True):
        st.switch_page("homepage.py")

st.markdown("""
<div style="padding: 1rem 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(99, 102, 241, 0.02) 100%); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; margin-top: 1rem; margin-bottom: 1.5rem;">
    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #FFFFFF;">⚡ JSON Validator & Formatter</h2>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #94A3B8;">Validate structure, minify, or format JSON payloads with clean indentation.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Raw JSON Input")
    indent_size = st.slider("Indentation Spaces:", min_value=1, max_value=8, value=4, key="page_json_indent")
    
    default_json = '{"project": "Labs", "creator": "Mike Murray", "active": true, "tools": ["data-cleaner", "sql-builder"], "nested": {"version": 1.0}}'
    raw_input = st.text_area("Paste raw JSON here:", value=default_json, height=350, key="page_json_raw_input")
    
with col2:
    st.subheader("Validated Output")
    
    if raw_input.strip():
        try:
            parsed = json.loads(raw_input)
            formatted = json.dumps(parsed, indent=indent_size)
            
            st.success("✅ Valid JSON format!")
            st.code(formatted, language="json")
            
            st.download_button(
                label="📥 Download Formatted JSON",
                data=formatted,
                file_name="formatted.json",
                mime="application/json",
                use_container_width=True,
                key="page_json_download_btn"
            )
        except json.JSONDecodeError as jde:
            st.error(f"❌ Invalid JSON: {str(jde)}")
            st.info("Check syntax, braces, trailing commas, or quotes (ensure double quotes are used for keys).")
    else:
        st.info("Paste JSON in the input panel to validate and format.")
