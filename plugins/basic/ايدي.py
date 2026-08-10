import html
import os

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from Tepthon import zq_lo
from Tepthon.Config import Config
from Tepthon.core.managers import edit_or_reply


PLUGIN_CATEGORY = "الادوات"


async def get_target_user(event):
    """الحصول على المستخدم من الرد أو المعرف أو الآيدي أو الحساب الحالي."""

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
    """إحضار معلومات المستخدم وصورته."""

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
    first_name = html.escape(
        first_name.replace("\u2060", "")
    )

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
        if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
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

    caption = (
        "✛━━━━━━━━━━━━━✛\n"
        f"<b>•❃╎الاسـم    ⇠ </b> {first_name}\n"
        f"<b>•❃╎المعـرف  ⇠ </b> {username}\n"
        f"<b>•❃╎الايـدي   ⇠ </b> <code>{user_id}</code>\n"
        f"<b>•❃╎الرتبـــه  ⇠ </b> {rank}\n"
        f"<b>•❃╎الصـور   ⇠ </b> {photos_count}\n"
        f'<b>•❃╎الحساب ⇠ </b> <a href="tg://user?id={user_id}">{first_name}</a>\n'
        f"<b>•❃╎البايـو    ⇠ </b> {html.escape(user_bio)}\n"
        "✛━━━━━━━━━━━━━✛"
    )

    return photo, caption


@zq_lo.rep_cmd(
    pattern=r"ايدي(?:\s+(.+))?$",
    command=("ايدي", PLUGIN_CATEGORY),
    info={
        "header": "عرض معلومات المستخدم",
        "الاستـخـدام": "{tr}ايدي بالرد أو {tr}ايدي + معرف/ايدي",
    },
)
async def user_id_command(event):
    """عرض معلومات الشخص بشكل مرتب."""

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

        reply_to = event.reply_to_msg_id or None

        if photo and os.path.exists(photo):
            await event.client.send_file(
                event.chat_id,
                photo,
                caption=caption,
                parse_mode="html",
                force_document=False,
                reply_to=reply_to,
            )

            try:
                os.remove(photo)
            except Exception:
                pass

            await loading.delete()

        else:
            await loading.edit(
                caption,
                parse_mode="html",
            )

    except Exception as error:
        await edit_or_reply(
            loading,
            f"**- حدث خطأ أثناء إحضار المعلومات:**\n<code>{html.escape(str(error))}</code>",
            parse_mode="html",
        )
