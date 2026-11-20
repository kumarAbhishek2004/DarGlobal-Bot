import os
import json
import sqlite3
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "conversations.db"

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema for threads and messages."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_updated ON threads(updated_at DESC)")
        conn.commit()
    logger.info(f"Conversations database initialized at {DB_PATH}")

def create_thread(thread_id: Optional[str] = None, title: Optional[str] = "New Conversation") -> Dict[str, Any]:
    tid = thread_id or f"thread_{uuid.uuid4().hex[:12]}"
    clean_title = (title or "New Conversation").strip()
    if len(clean_title) > 60:
        clean_title = clean_title[:57] + "..."

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO threads (id, title, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (tid, clean_title))
        conn.commit()

    return {"id": tid, "title": clean_title}

def get_all_threads() -> List[Dict[str, Any]]:
    """Returns all conversation threads sorted by most recently active."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at
            FROM threads
            ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_thread_by_id(thread_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a thread and all of its messages."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at, updated_at FROM threads WHERE id = ?", (thread_id,))
        thread_row = cursor.fetchone()
        if not thread_row:
            return None

        cursor.execute("""
            SELECT role, content, sources, model, created_at
            FROM messages
            WHERE thread_id = ?
            ORDER BY id ASC
        """, (thread_id,))
        message_rows = cursor.fetchall()

        messages = []
        for r in message_rows:
            sources = []
            if r["sources"]:
                try:
                    sources = json.loads(r["sources"])
                except Exception:
                    sources = []
            messages.append({
                "role": r["role"],
                "content": r["content"],
                "sources": sources,
                "model": r["model"] or "concierge",
                "created_at": r["created_at"]
            })

        thread_dict = dict(thread_row)
        thread_dict["messages"] = messages
        return thread_dict

def save_message_to_thread(
    thread_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    model: Optional[str] = None
):
    """Appends a message to a thread and bumps its updated_at timestamp."""
    sources_json = json.dumps(sources) if sources else None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (thread_id, role, content, sources, model)
            VALUES (?, ?, ?, ?, ?)
        """, (thread_id, role, content, sources_json, model))

        cursor.execute("""
            UPDATE threads
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (thread_id,))
        conn.commit()

def update_thread_title_from_query(thread_id: str, query: str):
    """Auto-generates a clean thread title from the initial user query."""
    clean = query.strip()
    if clean.lower().startswith(("tell me about ", "what is ", "what are ", "how do i ")):
        clean = clean[clean.find(" ") + 1:].strip()
    if len(clean) > 45:
        clean = clean[:42] + "..."
    if not clean:
        clean = "Property Inquiry"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE threads
            SET title = ?
            WHERE id = ? AND (title = 'New Conversation' OR title = 'New Chat')
        """, (clean, thread_id))
        conn.commit()

def delete_thread_by_id(thread_id: str) -> bool:
    """Deletes a thread and all associated messages."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        conn.commit()
        return cursor.rowcount > 0
