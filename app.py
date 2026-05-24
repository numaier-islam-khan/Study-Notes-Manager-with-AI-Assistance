"""
app.py - Main entry point for the AI-Powered Study Notes Manager
Run with: streamlit run app.py

Navigation is handled via sidebar radio buttons.
Each page is imported from the pages/ folder.
"""

import streamlit as st
import os

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title  = "AI Study Notes Manager",
    page_icon   = "📚",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ── Project-level imports ─────────────────────────────────────────────────────
from database import initialize_database

# Initialize DB on first run
initialize_database()

# ── Load Custom CSS ───────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    # FIX: Added encoding="utf-8" to fix UnicodeDecodeError
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("CSS file not found. Using default styling.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Study Notes")
    st.markdown("*AI-Powered Manager*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "➕ Add Note", "📖 View Notes", "🧠 Quiz Generator"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-info">'
        '🤖 <b>AI Features</b><br>'
        '• Auto title generation<br>'
        '• Smart summarization<br>'
        '• Keyword extraction<br>'
        '• Quiz generation'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.caption("Built with ❤️ using Streamlit + NLTK")

# ── Page Routing ──────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    from pages.dashboard import show
elif page == "➕ Add Note":
    from pages.add_notes import show
elif page == "📖 View Notes":
    from pages.view_notes import show
elif page == "🧠 Quiz Generator":
    from pages.quiz_generator import show

show()