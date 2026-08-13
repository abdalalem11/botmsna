import aiosqlite
from pathlib import Path

DB_PATH = Path("factory/bots.db")


async def init_sessions():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                session TEXT NOT NULL,
                status TEXT DEFAULT 'stopped',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_session(owner_id, name, session):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO sessions (owner_id, name, session)
            VALUES (?, ?, ?)
            """,
            (owner_id, name, session),
        )
        await db.commit()
        return cur.lastrowid


async def get_sessions(owner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, name, status, created_at
            FROM sessions
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (owner_id,),
        )
        return await cur.fetchall()


async def delete_session(session_id, owner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            DELETE FROM sessions
            WHERE id = ? AND owner_id = ?
            """,
            (session_id, owner_id),
        )
        await db.commit()
