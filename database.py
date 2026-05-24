"""
database.py - Handles all SQLite database operations
This module manages the notes database: create, read, update, delete.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn


def initialize_database():
    """
    Create the notes table if it doesn't exist.
    Called once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            content     TEXT NOT NULL,
            summary     TEXT,
            keywords    TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            is_favorite INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def add_note(title, content, summary="", keywords=""):
    """
    Insert a new note into the database.
    Returns the new note's ID.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (title, content, summary, keywords, created_at, updated_at, is_favorite)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (title, content, summary, keywords, now, now))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_notes():
    """Fetch all notes ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_note_by_id(note_id):
    """Fetch a single note by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_note(note_id, title, content, summary="", keywords=""):
    """Update an existing note's title and content."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notes
        SET title=?, content=?, summary=?, keywords=?, updated_at=?
        WHERE id=?
    """, (title, content, summary, keywords, now, note_id))
    conn.commit()
    conn.close()


def delete_note(note_id):
    """Delete a note by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


def toggle_favorite(note_id):
    """Toggle the is_favorite flag for a note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notes SET is_favorite = CASE WHEN is_favorite=1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (note_id,))
    conn.commit()
    conn.close()


def search_notes(query):
    """
    Search notes by title or content keyword.
    Returns matching notes.
    """
    conn = get_connection()
    cursor = conn.cursor()
    like_query = f"%{query}%"
    cursor.execute("""
        SELECT * FROM notes
        WHERE title LIKE ? OR content LIKE ? OR keywords LIKE ?
        ORDER BY created_at DESC
    """, (like_query, like_query, like_query))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """
    Return aggregate statistics for the dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM notes")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as favs FROM notes WHERE is_favorite=1")
    favorites = cursor.fetchone()["favs"]

    cursor.execute("SELECT SUM(LENGTH(content) - LENGTH(REPLACE(content,' ','')) + 1) as words FROM notes")
    row = cursor.fetchone()
    total_words = row["words"] if row["words"] else 0

    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT 5")
    recent = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total": total,
        "favorites": favorites,
        "total_words": total_words,
        "recent": recent
    }