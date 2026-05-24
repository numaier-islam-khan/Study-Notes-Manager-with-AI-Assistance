"""
pages/quiz_generator.py - AI Quiz Generator page
Select any note and generate MCQ, True/False, and Short Answer questions.
"""

import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_all_notes
from ai_tools import generate_quiz
from utils    import export_quiz_txt


def show():
    st.markdown('<p class="section-header">🧠 AI Quiz Generator</p>', unsafe_allow_html=True)
    st.info("Select a note and generate a quiz automatically using AI. 🤖")

    notes = get_all_notes()
    if not notes:
        st.warning("No notes available. Add some notes first! 📝")
        return

    # ── Note Selector ─────────────────────────────────────────
    note_titles = {n["title"]: n for n in notes}
    selected_title = st.selectbox("📚 Select a Note", list(note_titles.keys()))
    selected_note  = note_titles[selected_title]

    with st.expander("📄 Preview Note Content"):
        st.write(selected_note["content"][:600] +
                 ("…" if len(selected_note["content"]) > 600 else ""))

    st.markdown("---")

    # ── Generate Button ───────────────────────────────────────
    if st.button("🚀 Generate Quiz", use_container_width=True):
        if len(selected_note["content"].split()) < 30:
            st.error("❌ Note is too short to generate a quiz. Add more content!")
            return

        with st.spinner("🤖 Generating quiz questions…"):
            quiz = generate_quiz(selected_note["content"])

        st.session_state["current_quiz"]       = quiz
        st.session_state["current_quiz_title"] = selected_note["title"]
        st.success("✅ Quiz generated! Scroll down to see your questions.")

    # ── Display Quiz ──────────────────────────────────────────
    if "current_quiz" not in st.session_state:
        return

    quiz  = st.session_state["current_quiz"]
    title = st.session_state["current_quiz_title"]

    st.markdown(f"### 📋 Quiz: {title}")

    # MCQ Section
    mcq_list = quiz.get("mcq", [])
    if mcq_list:
        st.markdown("#### 🔵 Section A – Multiple Choice Questions")
        for i, q in enumerate(mcq_list, 1):
            st.markdown(f'<div class="quiz-card"><b>Q{i}.</b> {q["question"]}</div>',
                        unsafe_allow_html=True)
            user_ans = st.radio("Choose your answer:",
                                q["options"],
                                key=f"mcq_{i}_{title[:10]}",
                                index=None)
            if user_ans:
                if user_ans == q["answer"]:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer: **{q['answer']}**")
            st.markdown("")

    # True/False Section
    tf_list = quiz.get("true_false", [])
    if tf_list:
        st.markdown("#### 🟡 Section B – True / False")
        for i, q in enumerate(tf_list, 1):
            st.markdown(f'<div class="quiz-card"><b>Q{i}.</b> {q["question"]}</div>',
                        unsafe_allow_html=True)
            user_ans = st.radio("True or False?",
                                ["True", "False"],
                                key=f"tf_{i}_{title[:10]}",
                                index=None)
            if user_ans:
                if user_ans == q["answer"]:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer: **{q['answer']}**")
            st.markdown("")

    # Short Answer Section
    sa_list = quiz.get("short", [])
    if sa_list:
        st.markdown("#### 🟢 Section C – Short Answer Questions")
        for i, q in enumerate(sa_list, 1):
            st.markdown(f'<div class="quiz-card"><b>Q{i}.</b> {q["question"]}</div>',
                        unsafe_allow_html=True)
            st.text_area("Your answer:", key=f"sa_{i}_{title[:10]}", height=80)
            with st.expander("💡 Hint"):
                st.write(q["hint"])
            st.markdown("")

    # ── Download Quiz ─────────────────────────────────────────
    st.markdown("---")
    if st.button("📥 Download Quiz as TXT"):
        path = export_quiz_txt(title, quiz)
        with open(path, "r", encoding="utf-8") as f:
            st.download_button("⬇️ Download Quiz",
                               f.read(),
                               file_name=os.path.basename(path),
                               mime="text/plain")
