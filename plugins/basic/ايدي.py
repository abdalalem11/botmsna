import html
import os

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from Tepthon import Tepthon_cmd
from Tepthon.Config import Config
from Tepthon.core.managers import edit_or_reply


async def get_target_user(event):
    """الحصول على المستخدم من الرد أو المعرف أو الآيدي."""

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            return await event.client.get_entity(reply.sender_id)

    user_input = event.pattern_match.group(1)

    if not user_input:
        return await event.client.get_me()

    user_input = user_input.strip()

    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityMentionName):
                return await event.client.get_entity(entity.user_id)

    try:
        if user_input.lstrip("-").isdigit():
            user_input = int(user_input)

        return await event.client.get_entity(user_input)

    except Exception:
        return None


async def fetch_info(user, event):
    """إحضار معلومات المستخدم."""

    full_user = await event.client(
        GetFullUserRequest(user.id)
    )

    try:
        photos = await event.client(
            GetUserPhotosRequest(
                user_id=user.id,
                offset=0,
                max_id=0,
                limit=100,
            )
        )
        photos_count = photos.count
    except Exception:
        photos_count = 0

    user_id = user.id

    first_name = user.first_name or "لا يوجد اسم"
    first_name = first_name.replace("\u2060", "")

    username = (
        f"@{user.username}"
        if user.username
        else "لا يوجد معرف"
    )

    user_bio = (
        full_user.full_user.about
        if full_user.full_user.about
        else "لا توجد نبذة"
    )

    me = await event.client.get_me()

    if user_id == me.id:
        rank = "⌁ مالك الحساب 𓀫 ⌁"
    else:
        rank = "⌁ العضو 𓅫 ⌁"

    photo = None

    try:
        os.makedirs(
            Config.TMP_DOWNLOAD_DIRECTORY,
            exist_ok=True,
        )

        photo = await event.client.download_profile_photo(
            user_id,
            Config.TMP_DOWNLOAD_DIRECTORY
            + str(user_id)
            + ".jpg",
            download_big=True,
        )
    except Exception:
        photo = None

    safe_bio = html.escape(user_bio)

    caption = (
        "✛━━━━━━━━━━━━━✛\n"
        f"<b>•❃╎الاسـم    ⇠ </b> {first_name}\n"
        f"<b>•❃╎المعـرف  ⇠ </b> {username}\n"
        f"<b>•❃╎الايـدي   ⇠ </b> <code>{user_id}</code>\n"
        f"<b>•❃╎الرتبـــه  ⇠ </b> {rank}\n"
        f"<b>•❃╎الصـور   ⇠ </b> {photos_count}\n"
        f'<b>•❃╎الحساب ⇠ </b> <a href="tg://user?id={user_id}">{first_name}</a>\n'
        f"<b>•❃╎البايـو    ⇠ </b> {safe_bio}\n"
        "✛━━━━━━━━━━━━━✛"
    )

    return photo, caption


@Tepthon_cmd(
    pattern=r"ايدي(?:\s+(.+))?$"
)
async def user_id_command(event):

    loading = await edit_or_reply(
        event,
        "⇆ جـارِ إحضـار معلومـات المسـتخدم..."
    )

    user = await get_target_user(event)

    if not user:
        return await edit_or_reply(
            loading,
            "**- لـم أستطـع العثـور علـى الشخـص ❌**"
        )

    try:
        photo, caption = await fetch_info(
            user,
            event,
        )

       
