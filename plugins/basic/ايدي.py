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
            try:
                return await event.client.get_entity(reply.sender_id)
            except Exception:
                return None

    user_input = None

    try:
        user_input = event.pattern_match.group(1)
    except Exception:
        user_input = None

    if not user_input:
        return await event.client.get_me()

    user_input = user_input.strip()

    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityMentionName):
                try:
                    return await event.client.get_entity(entity.user_id)
                except Exception:
                    pass

    try:
        if user_input.lstrip("-").isdigit():
            user_input = int(user_input)

        return await event.client.get_entity(user_input)

    except Exception:
        return None


async def fetch_info(user, event):
    """إحضار معلومات المستخدم."""

    try:
        full_user = await event.client(
            GetFullUserRequest(user.id)
        )
    except Exception:
        full_user = None

    try:
        photos = await event.client(
            GetUserPhotosRequest(
                user_id=user.id,
                offset=0,
                max_id=0,
                limit=100,
            )
        )
        photos_count = getattr(photos, "count", 0) or 0
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

    try:
        user_bio = (
            full_user.full_user.about
            if full_user
            and full_user.full_user
            and full_user.full_user.about
            else "لا توجد نبذة"
        )
    except Exception:
        user_bio = "لا توجد نبذة"

    me = await event.client.get_me()

    if user_id == me.id:
        rank = "⌁ مالك الحساب 𓀫 ⌁"
    else:
        rank = "⌁ العضو 𓅫 ⌁"

    photo = None
    photo_path = None

    try:
        download_dir = getattr(
            Config,
            "TMP_DOWNLOAD_DIRECTORY",
            "./temp/",
        )

        os.makedirs(
            download_dir,
            exist_ok=True,
        )

        photo_path = os.path.join(
            download_dir,
            f"{user_id}.jpg",
        )

        photo = await event.client.download_profile_photo(
            user_id,
            photo_path,
            download_big=True,
        )

    except Exception:
        photo = None

    safe_name = html.escape(first_name)
    safe_username = html.escape(username)
    safe_bio = html.escape(user_bio)

    caption = (
        "✛━━━━━━━━━━━━━✛\n"
        f"<b>•❃╎الاسـم    ⇠ </b> {safe_name}\n"
        f"<b>•❃╎المعـرف  ⇠ </b> {safe_username}\n"
        f"<b>•❃╎الايـدي   ⇠ </b> <code>{user_id}</code>\n"
        f"<b>•❃╎الرتبـــه  ⇠ </b> {rank}\n"
        f"<b>•❃╎الصـور   ⇠ </b> {photos_count}\n"
        f'<b>•❃╎الحساب ⇠ </b> '
        f'<a href="tg://user?id={user_id}">{safe_name}</a>\n'
        f"<b>•❃╎البايـو    ⇠ </b> {safe_bio}\n"
        "✛━━━━━━━━━━━━━✛"
    )

    return photo, photo_path, caption


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
        photo, photo_path, caption = await fetch_info(
            user,
            event,
        )

        if photo and os.path.exists(photo):
            await event.client.send_file(
                event.chat_id,
                photo,
                caption=caption,
                parse_mode="html",
            )

            try:
                await loading.delete()
            except Exception:
                pass

            try:
                if photo_path and os.path.exists(photo_path):
                    os.remove(photo_path)
            except Exception:
                pass

            try:
                if event.out:
                    await event.delete()
            except Exception:
                pass

        else:
            await edit_or_reply(
                loading,
                caption,
                parse_mode="html",
                link_preview=False,
            )

    except Exception as error:
        try:
            await edit_or_reply(
                loading,
                f"**- حدث خطأ أثناء جلب معلومات المستخدم ❌**\n\n"
                f"<code>{html.escape(str(error))}</code>",
                parse_mode="html",
            )
        except Exception:
            pass
