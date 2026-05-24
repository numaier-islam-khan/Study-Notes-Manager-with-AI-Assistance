"""
utils.py - Utility/helper functions for the Study Notes Manager
Provides: PDF export, TXT export, text formatting helpers.
"""

import os
import textwrap
from datetime import datetime


# ── Text Helpers ─────────────────────────────────────────────────────────────

def truncate_text(text: str, max_chars: int = 200) -> str:
    """Shorten text to max_chars, appending '…' if truncated."""
    if not text:
        return ""
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "…"


def count_words(text: str) -> int:
    """Return word count of a string."""
    if not text:
        return 0
    return len(text.split())


def format_date(date_str: str) -> str:
    """Convert '2024-01-15 10:30:00' → 'Jan 15, 2024 10:30 AM'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y  %I:%M %p")
    except Exception:
        return date_str


# ── Export Functions ──────────────────────────────────────────────────────────

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


def export_note_txt(note: dict) -> str:
    """
    Save a note as a .txt file in the exports/ folder.
    Returns the file path.
    """
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in note["title"])
    filename   = f"{safe_title}_{note['id']}.txt"
    filepath   = os.path.join(EXPORTS_DIR, filename)

    lines = [
        f"TITLE:     {note['title']}",
        f"CREATED:   {format_date(note['created_at'])}",
        f"UPDATED:   {format_date(note['updated_at'])}",
        f"KEYWORDS:  {note.get('keywords', 'N/A')}",
        "",
        "── SUMMARY ──────────────────────────────",
        note.get("summary", "No summary available."),
        "",
        "── CONTENT ──────────────────────────────",
        note["content"],
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


def export_note_pdf(note: dict) -> str:
    """
    Export note as PDF using fpdf2 if available,
    otherwise falls back to a simple text file with .pdf.txt extension.
    Returns the file path.
    """
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in note["title"])
    filename   = f"{safe_title}_{note['id']}.pdf"
    filepath   = os.path.join(EXPORTS_DIR, filename)

    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, note["title"], ln=True)

        # Meta
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Created: {format_date(note['created_at'])}", ln=True)
        pdf.cell(0, 8, f"Keywords: {note.get('keywords','N/A')}", ln=True)
        pdf.ln(4)

        # Summary
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, note.get("summary", "No summary."))
        pdf.ln(3)

        # Content
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Content", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, note["content"])

        pdf.output(filepath)
        return filepath

    except ImportError:
        # fpdf not installed: save as txt instead
        fallback = filepath + ".txt"
        export_note_txt(note)
        return export_note_txt(note)


def export_quiz_txt(note_title: str, quiz: dict) -> str:
    """
    Save generated quiz as a .txt file.
    Returns file path.
    """
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in note_title)
    filepath = os.path.join(EXPORTS_DIR, f"Quiz_{safe}.txt")

    lines = [f"QUIZ FOR: {note_title}", "=" * 50, ""]

    # MCQ
    if quiz.get("mcq"):
        lines.append("SECTION A – Multiple Choice Questions")
        lines.append("-" * 40)
        for i, q in enumerate(quiz["mcq"], 1):
            lines.append(f"Q{i}. {q['question']}")
            for j, opt in enumerate(q["options"], 1):
                lines.append(f"    {j}. {opt}")
            lines.append(f"    ✓ Answer: {q['answer']}")
            lines.append("")

    # T/F
    if quiz.get("true_false"):
        lines.append("SECTION B – True / False")
        lines.append("-" * 40)
        for i, q in enumerate(quiz["true_false"], 1):
            lines.append(f"Q{i}. {q['question']}")
            lines.append(f"    ✓ Answer: {q['answer']}")
            lines.append("")

    # Short
    if quiz.get("short"):
        lines.append("SECTION C – Short Answer Questions")
        lines.append("-" * 40)
        for i, q in enumerate(quiz["short"], 1):
            lines.append(f"Q{i}. {q['question']}")
            lines.append(f"    Hint: {q['hint']}")
            lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath