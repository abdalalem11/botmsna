import aiosqlite
from pathlib import Path

DB_PATH = Path("factory/bots.db")


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                bot_token TEXT NOT NULL UNIQUE,
                bot_username TEXT,
                status TEXT DEFAULT 'stopped',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


async def add_bot(owner_id, bot_token, bot_username=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bots
            (owner_id, bot_token, bot_username)
            VALUES (?, ?, ?)
            """,
            (owner_id, bot_token, bot_username),
        )

        await db.commit()
        return cursor.lastrowid


async def get_bots(owner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, bot_token, bot_username, status, created_at
            FROM bots
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (owner_id,),
        )

        return await cursor.fetchall()


async def delete_bot(bot_id, owner_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            DELETE FROM bots
            WHERE id = ? AND owner_id = ?
            """,
            (bot_id, owner_id),
        )

        await db.commit()
