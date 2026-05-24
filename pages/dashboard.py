"""
pages/dashboard.py - Dashboard page
Shows total notes, favorites, word count stats, and charts.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_stats
from utils    import format_date, count_words


def show():
    st.markdown('<p class="section-header">📊 Dashboard</p>', unsafe_allow_html=True)

    stats = get_stats()

    # ── Top Metrics ──────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Total Notes",    stats["total"])
    with col2:
        st.metric("⭐ Favorites",      stats["favorites"])
    with col3:
        st.metric("📖 Total Words",    f"{stats['total_words']:,}")
    with col4:
        avg = int(stats["total_words"] / stats["total"]) if stats["total"] else 0
        st.metric("✏️ Avg Words/Note", avg)

    st.markdown("---")

    # ── Chart ────────────────────────────────────────────────
    if stats["total"] > 0:
        try:
            import plotly.graph_objects as go

            recent = stats["recent"]
            labels = [n["title"][:20] for n in recent]
            values = [count_words(n["content"]) for n in recent]

            fig = go.Figure(
                go.Bar(
                    x=labels, y=values,
                    marker_color=["#6C63FF", "#FF6584", "#43D9AD", "#FFB347", "#A78BFA"][:len(labels)],
                    text=values, textposition="outside"
                )
            )
            fig.update_layout(
                title="Word Count – Recent Notes",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#A7A9BE",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2E2E4A"),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("Install plotly for charts: `pip install plotly`")
    else:
        st.info("No notes yet. Add your first note to see stats here! 🚀")

    st.markdown("---")

    # ── Recent Notes ─────────────────────────────────────────
    st.subheader("🕐 Recently Added Notes")

    if stats["recent"]:
        for note in stats["recent"]:
            fav = "⭐ " if note["is_favorite"] else ""
            with st.expander(f"{fav}{note['title']}  —  {format_date(note['created_at'])}"):
                st.write(note["content"][:400] + ("…" if len(note["content"]) > 400 else ""))
                if note.get("keywords"):
                    kws = note["keywords"].split(",")
                    tags = " ".join(f'<span class="keyword-tag">{k.strip()}</span>' for k in kws if k.strip())
                    st.markdown(tags, unsafe_allow_html=True)
    else:
        st.write("No notes found. Start adding notes! 📝")
