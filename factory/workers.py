import asyncio
from dataclasses import dataclass


@dataclass
class Worker:
    bot_id: int
    task: asyncio.Task


class WorkerManager:
    def __init__(self):
        self.workers: dict[int, Worker] = {}

    async def start(self, bot_id: int):
        if bot_id in self.workers:
            return False

        task = asyncio.create_task(self._run(bot_id))

        self.workers[bot_id] = Worker(
            bot_id=bot_id,
            task=task,
        )

        return True

    async def stop(self, bot_id: int):
        worker = self.workers.pop(bot_id, None)

        if worker is None:
            return False

        worker.task.cancel()

        try:
            await worker.task
        except asyncio.CancelledError:
            pass

        return True

    async def _run(self, bot_id: int):
        try:
            while True:
                await asyncio.sleep(30)

        except asyncio.CancelledError:
            raise

    async def stop_all(self):
        for bot_id in list(self.workers):
            await self.stop(bot_id)
