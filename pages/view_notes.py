"""
pages/view_notes.py - View, Search, Edit, and Delete Notes
Displays notes as expandable cards with inline editing and deletion.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_notes, search_notes, update_note,
                      delete_note, toggle_favorite, get_note_by_id)
from ai_tools import generate_title, summarize_text, extract_keywords
from utils    import format_date, count_words, export_note_txt, export_note_pdf


def show():
    st.markdown('<p class="section-header">📚 View Notes</p>', unsafe_allow_html=True)

    # ── Search Bar ────────────────────────────────────────────
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        query = st.text_input("🔍 Search notes…", placeholder="Enter keyword, title, or phrase…")
    with col_filter:
        view_mode = st.selectbox("View", ["Cards", "Table"])

    # Fetch notes
    notes = search_notes(query) if query.strip() else get_all_notes()

    if not notes:
        st.warning("No notes found. Try a different search or add some notes! 📝")
        return

    st.caption(f"Found **{len(notes)}** note(s)")

    # ── Table View ────────────────────────────────────────────
    if view_mode == "Table":
        import pandas as pd
        df = pd.DataFrame([{
            "ID":       n["id"],
            "Title":    n["title"],
            "Words":    count_words(n["content"]),
            "Keywords": n.get("keywords", ""),
            "Created":  format_date(n["created_at"]),
            "Fav":      "⭐" if n["is_favorite"] else ""
        } for n in notes])
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    # ── Cards View ────────────────────────────────────────────
    for note in notes:
        fav_icon = "⭐" if note["is_favorite"] else "☆"
        label    = f"{fav_icon} {note['title']}  |  {format_date(note['created_at'])}"

        with st.expander(label):
            # Meta row
            wc = count_words(note["content"])
            st.caption(f"🆔 ID: {note['id']}   |   📖 {wc} words   |   🕐 Updated: {format_date(note['updated_at'])}")

            # Tabs: View / Edit / Export
            tab_view, tab_edit, tab_export = st.tabs(["👁️ View", "✏️ Edit", "📤 Export"])

            # ── VIEW TAB ───────────────────────────────────────
            with tab_view:
                if note.get("summary"):
                    st.markdown("**📝 Summary**")
                    st.info(note["summary"])

                if note.get("keywords"):
                    kws  = note["keywords"].split(",")
                    tags = " ".join(f'<span class="keyword-tag">{k.strip()}</span>'
                                    for k in kws if k.strip())
                    st.markdown(f"**🔑 Keywords:** {tags}", unsafe_allow_html=True)

                st.markdown("**📄 Full Content**")
                st.write(note["content"])

                # Action buttons row
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"{'💛 Unfav' if note['is_favorite'] else '⭐ Favorite'}",
                                 key=f"fav_{note['id']}"):
                        toggle_favorite(note["id"])
                        st.rerun()
                with c2:
                    if st.button("🗑️ Delete", key=f"del_btn_{note['id']}"):
                        st.session_state[f"confirm_del_{note['id']}"] = True

                # Confirmation dialog
                if st.session_state.get(f"confirm_del_{note['id']}", False):
                    st.warning("⚠️ Are you sure you want to delete this note?")
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("✅ Yes, Delete", key=f"yes_del_{note['id']}"):
                            delete_note(note["id"])
                            st.session_state.pop(f"confirm_del_{note['id']}", None)
                            st.success("Note deleted.")
                            st.rerun()
                    with cn:
                        if st.button("❌ Cancel", key=f"no_del_{note['id']}"):
                            st.session_state.pop(f"confirm_del_{note['id']}", None)
                            st.rerun()

            # ── EDIT TAB ───────────────────────────────────────
            with tab_edit:
                new_title   = st.text_input("Title",   value=note["title"],   key=f"edit_t_{note['id']}")
                new_content = st.text_area("Content",  value=note["content"], height=200,
                                           key=f"edit_c_{note['id']}")

                col_a, col_b = st.columns(2)
                with col_a:
                    regen_summary  = st.checkbox("Re-generate Summary",  key=f"rgs_{note['id']}")
                with col_b:
                    regen_keywords = st.checkbox("Re-generate Keywords", key=f"rgk_{note['id']}")

                if st.button("💾 Save Changes", key=f"save_{note['id']}"):
                    if not new_content.strip():
                        st.error("Content cannot be empty!")
                    else:
                        with st.spinner("Saving…"):
                            final_title = new_title.strip() if new_title.strip() else generate_title(new_content)
                            summary     = summarize_text(new_content)   if regen_summary  else note.get("summary", "")
                            keywords    = extract_keywords(new_content) if regen_keywords else note.get("keywords", "")
                            update_note(note["id"], final_title, new_content, summary, keywords)
                        st.success("✅ Note updated successfully!")
                        st.rerun()

            # ── EXPORT TAB ─────────────────────────────────────
            with tab_export:
                ce1, ce2 = st.columns(2)
                with ce1:
                    if st.button("📄 Export as TXT", key=f"txt_{note['id']}"):
                        path = export_note_txt(note)
                        with open(path, "r", encoding="utf-8") as f:
                            st.download_button("⬇️ Download TXT", f.read(),
                                               file_name=os.path.basename(path),
                                               mime="text/plain",
                                               key=f"dl_txt_{note['id']}")
                with ce2:
                    if st.button("📕 Export as PDF", key=f"pdf_{note['id']}"):
                        path = export_note_pdf(note)
                        with open(path, "rb") as f:
                            st.download_button("⬇️ Download PDF", f.read(),
                                               file_name=os.path.basename(path),
                                               mime="application/pdf",
                                               key=f"dl_pdf_{note['id']}")
