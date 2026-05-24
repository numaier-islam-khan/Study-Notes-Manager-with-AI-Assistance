"""
pages/add_notes.py - Add Notes page
Users can write a title + content; AI auto-fills title/summary/keywords.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database  import add_note
from ai_tools  import generate_title, summarize_text, extract_keywords


def show():
    st.markdown('<p class="section-header">➕ Add New Note</p>', unsafe_allow_html=True)

    st.info("💡 Leave the title blank and AI will generate one automatically!")

    # ── Form ─────────────────────────────────────────────────
    with st.form("add_note_form", clear_on_submit=True):
        title   = st.text_input("📌 Note Title", placeholder="Leave blank for AI-generated title…")
        content = st.text_area("📄 Note Content", height=250,
                               placeholder="Write your study notes here…")

        col1, col2 = st.columns(2)
        with col1:
            auto_summary  = st.checkbox("🤖 Auto-generate Summary",  value=True)
        with col2:
            auto_keywords = st.checkbox("🔑 Auto-extract Keywords", value=True)

        submitted = st.form_submit_button("💾 Save Note", use_container_width=True)

    if submitted:
        # Validation
        if not content.strip():
            st.error("❌ Note content cannot be empty.")
            return

        # Word count guard
        if len(content.split()) < 3:
            st.warning("⚠️ Please write at least a few words.")
            return

        # AI processing
        with st.spinner("🤖 Running AI analysis…"):
            final_title   = title.strip() if title.strip() else generate_title(content)
            summary       = summarize_text(content)   if auto_summary  else ""
            keywords      = extract_keywords(content) if auto_keywords else ""

        # Save to DB
        note_id = add_note(final_title, content, summary, keywords)

        st.success(f"✅ Note saved successfully! (ID: {note_id})")
        st.balloons()

        # Preview
        with st.expander("👀 Preview your saved note"):
            st.markdown(f"**Title:** {final_title}")
            if summary:
                st.markdown(f"**Summary:** {summary}")
            if keywords:
                kws  = keywords.split(",")
                tags = " ".join(f'<span class="keyword-tag">{k.strip()}</span>'
                                for k in kws if k.strip())
                st.markdown(f"**Keywords:** {tags}", unsafe_allow_html=True)
            st.markdown(f"**Content:**\n\n{content}")
