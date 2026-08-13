import aiosqlite
from pathlib import Path

DB_PATH = Path("factory/bots.db")


async def init_permissions():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                user_id INTEGER PRIMARY KEY,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def request_permission(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO permissions (user_id, status)
            VALUES (?, 'pending')
            ON CONFLICT(user_id)
            DO UPDATE SET status='pending'
        """, (user_id,))
        await db.commit()


async def get_permission(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT status FROM permissions WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else None


async def set_permission(user_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO permissions (user_id, status)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET status=excluded.status
        """, (user_id, status))
        await db.commit()


async def get_pending():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT user_id
            FROM permissions
            WHERE status='pending'
            ORDER BY created_at
        """)
        return await cur.fetchall()
