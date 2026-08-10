from . import zq_lo
from ..core.managers import edit_or_reply


plugin_category = "الاساسي"


@zq_lo.rep_cmd(
    pattern="ايدي$",
    command=("ايدي", plugin_category),
)
async def user_id(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        return await edit_or_reply(
            event,
            f"**⎉╎ايدي الشخص الذي رددت عليه :** `{user_id}`"
        )

    return await edit_or_reply(
        event,
        f"**⎉╎ايديك :** `{event.sender_id}`"
    )
