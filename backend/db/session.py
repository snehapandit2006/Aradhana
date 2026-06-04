import aiosqlite
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

DATABASE_FILE = os.getenv("DATABASE_URL", "./astroagent.db")

async def init_db():
    """
    Initializes the SQLite database schema if tables do not exist.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON;")
        
        # Create sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                birth_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create messages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT CHECK(role IN ('user', 'assistant', 'system', 'tool')),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );
        """)
        await db.commit()

async def get_or_create_session(session_id: str) -> None:
    """
    Ensures a session exists in the sessions table.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,)) as cursor:
            if not await cursor.fetchone():
                await db.execute(
                    "INSERT INTO sessions (session_id, birth_data) VALUES (?, ?)",
                    (session_id, None)
                )
                await db.commit()

async def save_birth_data(session_id: str, birth_data: dict) -> None:
    """
    Saves or updates birth data for a session.
    """
    await get_or_create_session(session_id)
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "UPDATE sessions SET birth_data = ? WHERE session_id = ?",
            (json.dumps(birth_data), session_id)
        )
        await db.commit()

async def get_birth_data(session_id: str) -> Optional[dict]:
    """
    Retrieves birth data for a session, if any exists.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT birth_data FROM sessions WHERE session_id = ?", (session_id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None

async def save_message(session_id: str, role: str, content: str) -> None:
    """
    Appends a new message to the session's chat history.
    """
    await get_or_create_session(session_id)
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        await db.commit()

async def get_history(session_id: str) -> List[Dict[str, str]]:
    """
    Retrieves the chronological list of messages for a session.
    """
    await get_or_create_session(session_id)
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]

async def delete_session(session_id: str) -> None:
    """
    Deletes the session and all its associated messages cascadingly.
    """
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        await db.commit()
