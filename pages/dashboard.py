
"""
pages/dashboard.py - Dashboard page
Shows total notes, favorites, word count stats, and charts.
"""

import streamlit as st
import sys, os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_stats, get_all_notes
from utils    import format_date, count_words


def show():
    # CSS for Bengali font support
    st.markdown("""
        <style>
        * {
            font-family: 'Segoe UI', 'Bangla', 'Noto Sans Bengali', sans-serif;
        }
        .keyword-tag {
            background: #6C63FF;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-right: 8px;
            display: inline-block;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📊 Dashboard</p>', unsafe_allow_html=True)

    stats = get_stats()
    
    # Get all notes for charts
    all_notes = get_all_notes()

    # -- Top Metrics (Bengali) ------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Total Notes", stats["total"])
    with col2:
        st.metric("⭐ Favorites", stats["favorites"])
    with col3:
        st.metric("📖 Total Words", f"{stats['total_words']:,}")
    with col4:
        avg = int(stats["total_words"] / stats["total"]) if stats["total"] else 0
        st.metric("✏️ Avg Words/Note", avg)

    st.markdown("---")

    # -- Charts Section -------------------------------------------------------
    if stats["total"] > 0 and all_notes:
        try:
            # Convert to DataFrame
            df = pd.DataFrame(all_notes)
            
            # Chart 1: Notes over time
            if 'created_at' in df.columns:
                df['date'] = pd.to_datetime(df['created_at']).dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                
                fig1 = px.bar(daily_counts, x='date', y='count',
                             title="📈 Notes Created Over Time",
                             labels={'date': 'Date', 'count': 'Number of Notes'},
                             color='count',
                             color_continuous_scale='Blues')
                fig1.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#A7A9BE",
                    height=350,
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            # Row 2: Two charts side by side
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Chart 2: Word count distribution
                if 'word_count' in df.columns:
                    fig2 = px.histogram(df, x='word_count',
                                       title="📏 Note Length Distribution",
                                       labels={'word_count': 'Word Count', 'count': 'Number of Notes'},
                                       nbins=20,
                                       color_discrete_sequence=['#2E86AB'])
                    fig2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#A7A9BE",
                        height=350,
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            with col_chart2:
                # Chart 3: Favorites vs Regular (Pie Chart)
                if 'is_favorite' in df.columns:
                    fav_count = len(df[df['is_favorite'] == True])
                    normal_count = len(df[df['is_favorite'] == False])
                    
                    fig3 = px.pie(values=[fav_count, normal_count],
                                 names=['⭐ Favorite Notes', '📄 Regular Notes'],
                                 title="⭐ Favorites vs Regular",
                                 color_discrete_sequence=['#FFD700', '#A9A9A9'],
                                 hole=0.3)  # Donut chart style
                    fig3.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#A7A9BE",
                        height=350,
                    )
                    st.plotly_chart(fig3, use_container_width=True)
            
            # Row 3: Top 5 longest notes
            if 'word_count' in df.columns and 'title' in df.columns:
                st.subheader("🏆 Top 5 Longest Notes")
                top_notes = df.nlargest(5, 'word_count')[['title', 'word_count']]
                fig4 = px.bar(top_notes, x='title', y='word_count',
                             title="Top Notes by Word Count",
                             labels={'title': 'Note Title', 'word_count': 'Word Count'},
                             color='word_count',
                             color_continuous_scale='Reds')
                fig4.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#A7A9BE",
                    height=350,
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            # Chart 5: Word count of recent notes (original bar chart)
            st.subheader("📊 Word Count - Recent Notes")
            recent = stats["recent"]
            labels = [n["title"][:20] for n in recent]
            values = [count_words(n["content"]) for n in recent]

            fig5 = go.Figure(
                go.Bar(
                    x=labels, y=values,
                    marker_color=["#6C63FF", "#FF6584", "#43D9AD", "#FFB347", "#A78BFA"][:len(labels)],
                    text=values, textposition="outside"
                )
            )
            fig5.update_layout(
                title="Word Count of Recent Notes",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#A7A9BE",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#2E2E4A"),
                height=350,
            )
            st.plotly_chart(fig5, use_container_width=True)
            
        except ImportError as e:
            st.info("📦 Install plotly for charts: `pip install plotly pandas`")
        except Exception as e:
            st.warning(f"Error loading charts: {e}")
    else:
        st.info("📭 No notes yet. Add your first note to see charts! 🚀")

    st.markdown("---")

    # -- Recent Notes --------------------------------------------------------
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
        st.write("📝 No notes found. Start adding notes!")
