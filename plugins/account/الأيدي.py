# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tepthon - ID Plugin
# حقوق @SSSTlF
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from telethon.utils import pack_bot_file_id

from .. import Tepthon_cmd
from ..core.logger import LOGS


plugin_category = "utils"


async def edit_or_reply(event, text, **kwargs):
    """
    تعديل رسالة الأمر إذا كانت صادرة من المستخدم،
    وإلا إرسال رسالة جديدة.
    """
    try:
        if event.out:
            return await event.edit(text, **kwargs)
        return await event.respond(text, **kwargs)
    except Exception:
        return await event.respond(text, **kwargs)


async def edit_delete(event, text, time=5, **kwargs):
    """
    إرسال/تعديل الرسالة ثم حذفها بعد المدة المحددة.
    بدون استخدام managers.
    """
    import asyncio

    try:
        msg = await edit_or_reply(event, text, **kwargs)

        if time:
            await asyncio.sleep(time)

        try:
            await msg.delete()
        except Exception:
            pass

        return msg

    except Exception as e:
        LOGS.exception(e)
        return None


@Tepthon_cmd(
    pattern=r"(get_id|id)(?:\s|$)([\s\S]*)",
    command=("id", plugin_category),
    info={
        "header": "To get id of the group or user.",
        "description": (
            "if given input then shows id of that given "
            "chat/channel/user else if you reply to user "
            "then shows id of the replied user along with "
            "current chat id and if not replied to user or "
            "given input then just show id of the chat where "
            "you used the command"
        ),
        "usage": "{tr}id <reply/username>",
    },
)
async def _(event):
    """
    الحصول على ID المستخدم أو المجموعة أو القناة.
    """

    input_str = event.pattern_match.group(2)

    # --------------------------
    # Username / ID / Entity
    # --------------------------
    if input_str:
        try:
            entity = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(
                event,
                f"`{e}`",
                5,
            )

        try:
            if getattr(entity, "first_name", None):
                return await edit_or_reply(
                    event,
                    f"The id of the user `{input_str}` is `{entity.id}`",
                )
        except Exception:
            pass

        try:
            if getattr(entity, "title", None):
                return await edit_or_reply(
                    event,
                    f"The id of the chat/channel "
                    f"`{entity.title}` is `{entity.id}`",
                )
        except Exception as e:
            LOGS.info(str(e))

        return await edit_or_reply(
            event,
            "`Either give input as username or reply to user`",
        )

    # --------------------------
    # Reply
    # --------------------------
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()

        if reply_message is None:
            return await edit_or_reply(
                event,
                "`Unable to get the replied message.`",
            )

        if reply_message.media:
            try:
                bot_api_file_id = pack_bot_file_id(
                    reply_message.media
                )
            except Exception:
                bot_api_file_id = "Unable to generate file ID"

            return await edit_or_reply(
                event,
                f"**Current Chat ID:** `{event.chat_id}`\n"
                f"**From User ID:** `{reply_message.sender_id}`\n"
                f"**Media File ID:** `{bot_api_file_id}`",
            )

        return await edit_or_reply(
            event,
            f"**Current Chat ID:** `{event.chat_id}`\n"
            f"**From User ID:** `{reply_message.sender_id}`",
        )

    # --------------------------
    # Current chat only
    # --------------------------
    return await edit_or_reply(
        event,
        f"**Current Chat ID:** `{event.chat_id}`",
    )
