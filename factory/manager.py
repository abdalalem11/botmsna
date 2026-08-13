from .database import add_bot, get_bots, delete_bot
from .plans import get_plan


class BotManager:
    def __init__(self):
        pass

    async def create_bot(self, owner_id, bot_token, bot_username=None):
        return await add_bot(
            owner_id=owner_id,
            bot_token=bot_token,
            bot_username=bot_username,
        )

    async def list_bots(self, owner_id):
        return await get_bots(owner_id)

    async def remove_bot(self, bot_id, owner_id):
        await delete_bot(bot_id, owner_id)

    def get_plan(self, plan_name):
        return get_plan(plan_name)
