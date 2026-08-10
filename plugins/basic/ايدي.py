import os
from datetime import datetime

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_display_name

from Tepthon import Tepthon_cmd
from Tepthon.Config import Config
from Tepthon.core.managers import edit_or_reply


# ==============================
# إعدادات أمر الايدي
# ==============================

PROGRAMMER_ID = 1170411845
PROGRAMMER_USERNAME = "@SSSTlF"

PLUGIN_CATEGORY = "الادوات"


async def get_target_user(event):
    """جلب الشخص من الرد أو المعرف أو الايدي."""

    # إذا كان الأمر بالرد على شخص
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()

        if not reply or not reply.sender_id:
            return None

        try:
            return await event.client.get_entity(reply.sender_id)
        except Exception:
            return None

    # إذا كتب معرف أو ايدي بعد الأمر
    input_str = event.pattern_match.group(1)

    if input_str:
        input_str = input_str.strip()

        if input_str:
            try:
                if input_str.isdigit():
                    return await event.client.get_entity(int(input_str))

                return await event.client.get_entity(input_str)

            except Exception:
                return None

    # إذا لم يكتب شيء: معلومات صاحب الحساب
    try:
        return await event.client.get_me()
    except Exception:
        return None


async def get_user_photo_count(event, user_id):
    """جلب عدد صور البروفايل."""

    try:
        photos = await event.client(
            GetUserPhotosRequest(
                user_id=user_id,
                offset=0,
                max_id=0,
                limit=100,
            )
        )
        return photos.count
    except Exception:
        return "غير معروف"


@Tepthon_cmd(
    pattern="ايدي(?:\\s|$)(.*)",
    command=("ايدي", PLUGIN_CATEGORY),
    info={
        "header": "لعرض معلومات الشخص",
        "الاستعمال": ".ايدي بالرد أو .ايدي + المعرف أو الايدي",
    },
)
async def show_id(event):
    """عرض معلومات الشخص بشكل مرتب."""

    loading = await edit_or_reply(
        event,
        "**⌔︙جاري إحضار معلومات المستخدم ... ⏳**",
    )

    user = await get_target_user(event)

    if not user:
        return await edit_or_reply(
            loading,
            "**⌔︙لم أستطع العثور على المستخدم ❌**",
        )

    user_id = user.id

    # الاسم
    try:
        name = get_display_name(user)
    except Exception:
        name = user.first_name or "لا يوجد اسم"

    name = name.replace("\u2060", "") if name else "لا يوجد اسم"

    # المعرف
    username = f"@{user.username}" if user.username else "لا يوجد معرف"

    # البايو
    try:
        full_user = await event.client(
            GetFullUserRequest(user_id)
        )
        bio = full_user.full_user.about or "لا توجد نبذة"
    except Exception:
        bio = "لا توجد نبذة"

    # عدد الصور
    photo_count = await get_user_photo_count(
        event,
        user_id,
    )

    # الرتبة
    try:
        my_id = (await event.client.get_me()).id
    except Exception:
        my_id = None

    if user_id == PROGRAMMER_ID:
        rank = "⌁ مبرمج السورس 𓄂𓆃 ⌁"
    elif user_id == my_id:
        rank = "⌁ مالك الحساب 𓀫 ⌁"
    else:
        rank = "⌁ العضو 𓅫 ⌁"

    # الرابط
    user_link = f'<a href="tg://user?id={user_id}">{name}</a>'

    # النص النهائي
    caption = (
        "✛━━━━━━━━━━━━━✛\n"
        f"<b>⌔︙الاسـم    ⇠</b> {name}\n"
        f"<b>⌔︙المعـرف  ⇠</b> {username}\n"
        f"<b>⌔︙الايـدي   ⇠</b> <code>{user_id}</code>\n"
        f"<b>⌔︙الرتبـــه  ⇠</b> {rank}\n"
        f"<b>⌔︙الصـور   ⇠</b> {photo_count}\n"
        f"<b>⌔︙الحساب ⇠</b> {user_link}\n"
        f"<b>⌔︙البايـو    ⇠</b> {bio}\n"
        "✛━━━━━━━━━━━━━✛"
    )

    # تحميل صورة البروفايل
    photo = None

    try:
        if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
            os.makedirs(
                Config.TMP_DOWNLOAD_DIRECTORY,
                exist_ok=True,
            )

        photo_path = os.path.join(
            Config.TMP_DOWNLOAD_DIRECTORY,
            f"id_{user_id}_{datetime.now().timestamp()}.jpg",
        )

       
