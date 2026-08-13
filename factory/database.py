import os
import aiosqlite


DB_PATH = os.getenv("FACTORY_DB", "factory.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT NOT NULL DEFAULT 'free',
                expires_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bot_token TEXT NOT NULL,
                bot_username TEXT,
                status TEXT NOT NULL DEFAULT 'stopped',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, plan, expires_at FROM users WHERE user_id = ?",
            (user_id,),
        )
        return await cursor.fetchone()


async def create_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()


async def add_bot(
    user_id: int,
    bot_token: str,
    bot_username: str | None,
    created_at: str,
):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bots
            (user_id, bot_token, bot_username, status, created_at)
            VALUES (?, ?, ?, 'stopped', ?)
            """,
            (user_id, bot_token, bot_username, created_at),
        )
        await db.commit()
        return cursor.lastrowid


async def list_bots(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, bot_username, status, created_at
            FROM bots
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )
        return await cursor.fetchall()


async def delete_bot(user_id: int, bot_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM bots WHERE id = ? AND user_id = ?",
            (bot_id, user_id),
        )
        await db.commit()
