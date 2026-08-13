import os
import asyncio
import threading

from dotenv import load_dotenv
from flask import Flask, jsonify

from .database import init_db
from .manager import BotManager
from .workers import WorkerManager

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

manager = BotManager()
workers = WorkerManager()

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "botmsna-factory"
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


async def startup():
    await init_db()

    print("================================")
    print(" Bot Factory")
    print(" Database: OK")
    print(" Manager: OK")
    print(" Workers: OK")
    print("================================")

    if not BOT_TOKEN:
        print("WARNING: BOT_TOKEN is not configured.")

    if not ADMIN_ID:
        print("WARNING: ADMIN_ID is not configured.")

    print("Factory is ready.")


def run_web():
    port = int(os.getenv("PORT", "10000"))

    app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )


async def main():
    await startup()

    web_thread = threading.Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()

    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Factory stopped.")
