import os
import asyncio

from dotenv import load_dotenv

from .database import init_db
from .manager import BotManager
from .workers import WorkerManager

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

manager = BotManager()
workers = WorkerManager()


async def startup():
    await init_db()

    print("================================")
    print(" Bot Factory")
    print(" Database: OK")
    print(" Manager: OK")
    print(" Workers: OK")
    print("================================")


async def main():
    await startup()

    if not BOT_TOKEN:
        print("WARNING: BOT_TOKEN is not configured.")

    if not ADMIN_ID:
        print("WARNING: ADMIN_ID is not configured.")

    print("Factory is ready.")

    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Factory stopped.")
