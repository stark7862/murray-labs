import streamlit as st
import glob
import os
import ast

# Configure the Streamlit page (MUST be called first)
st.set_page_config(
    page_title="Labs - mikemurray.net",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS Theme
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0F172A; /* Slate 900 background */
        color: #F1F5F9;
    }
    
    /* Central Dashboard Header */
    .header-container {
        padding: 2rem 2.5rem;
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        margin-bottom: 2.5rem;
        backdrop-filter: blur(12px);
    }
    
    .labs-tag {
        font-family: 'Inter', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #A78BFA;
        letter-spacing: 0.15em;
        margin-bottom: 0.25rem;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FFFFFF 0%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Card panel styling for project directories */
    .project-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.75rem;
        height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .project-card:hover {
        transform: translateY(-5px);
        border-color: rgba(139, 92, 246, 0.35);
        box-shadow: 0 12px 30px rgba(139, 92, 246, 0.15);
    }
    
    .project-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
        /* Line clamp for titles */
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .project-desc {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.5;
        margin-bottom: 1rem;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .project-status {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #090D1A;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to dynamically discover files in the pages/ folder
def get_pages_meta():
    pages_dir = "pages"
    meta = []
    if not os.path.exists(pages_dir):
        return meta
        
    # Get all .py files in pages/ and sort them
    files = sorted(glob.glob(os.path.join(pages_dir, "*.py")))
    for file in files:
        filename = os.path.basename(file)
        
        # Clean title: e.g. "1_data_profiler.py" -> "Data Profiler"
        title = filename.replace(".py", "")
        if "_" in title:
            parts = title.split("_", 1)
            if parts[0].isdigit():
                title = parts[1]
        title = title.replace("_", " ").title()
        
        # Extract module-level docstring using AST parsing
        description = "No description provided."
        try:
            with open(file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                docstring = ast.get_docstring(tree)
                if docstring:
                    description = docstring.strip()
        except Exception:
            pass
            
        meta.append({
            "file_path": file,
            "title": title,
            "description": description,
            "key": filename.replace(".py", "")
        })
    return meta

# Header Section
st.markdown("""
<div class="header-container">
    <div class="labs-tag">MIKEMURRAY.NET / LABS</div>
    <h1 class="header-title">Developer Laboratories</h1>
    <p class="header-subtitle">A sandbox of high-performance utilities, web automation interfaces, and experimental local scripts.</p>
</div>
""", unsafe_allow_html=True)

# Discover pages
pages_meta = get_pages_meta()

if not pages_meta:
    st.warning("⚠️ No sub-apps found. Drop python files inside the `pages/` directory to automatically register new projects.")
else:
    st.markdown("### 🧪 Active Projects")
    st.caption("Select a project below to launch its workspace. The list is automatically synchronized with the `pages/` directory.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render cards in a 3-column grid
    cols_per_row = 3
    for i in range(0, len(pages_meta), cols_per_row):
        chunk = pages_meta[i:i+cols_per_row]
        cols = st.columns(cols_per_row)
        
        for idx, page in enumerate(chunk):
            with cols[idx]:
                # Automatically calculate status based on description tags
                desc_lower = page['description'].lower()
                is_prototype = "mock" in desc_lower or "coming soon" in desc_lower or "prototype" in desc_lower
                status = "🟡 Prototyping" if is_prototype else "🟢 Active"
                status_color = "#F59E0B" if is_prototype else "#10B981"
                
                # Render beautiful card
                st.markdown(f"""
                <div class="project-card">
                    <div>
                        <div class="project-title">{page['title']}</div>
                        <div class="project-status" style="color: {status_color};">{status}</div>
                        <p class="project-desc">{page['description']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Streamlit button to transition page
                if st.button(f"🚀 Open {page['title']}", key=f"btn_{page['key']}", use_container_width=True):
                    st.switch_page(page['file_path'])

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 0.8rem; font-family: monospace;'>"
    "© 2026 mikemurray.net - labs. All rights reserved. Running Streamlit Engine."
    "</div>", 
    unsafe_allow_html=True
)
