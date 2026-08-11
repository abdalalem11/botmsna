"""
❃ `{i}فحص`
    لـ عرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ `{i}فحص انلاين`
    لعرض حالة السورس بشكل Inline

❃ `{i}ا`
    لعرض معلومات الحساب وصورته

❃ ملاحظة:
    صورة الفحص يمكن تغييرها من خلال ALIVE_PIC
"""

import time
from platform import python_version
from random import choice

from Tepthon.config import version
from telethon.errors import BotMethodInvalidError, ChatSendMediaForbiddenError
from telethon.extensions import html, markdown
from telethon.version import __version__

from .. import *


# أزرار الفحص
buttons = [
    [
        Button.url("مجموعة المساعدة", "https://t.me/SSSTlFd"),
        Button.url("قناة السورس", "https://t.me/SSSTlFd"),
    ]
]


# نص الفحص العادي
alive_1 = (
    "**سورس النسرالاسود يعمل بنجاح ✅**\n\n"
    "❃ **مالك الحساب** - `{}`\n"
    "❃ **إصدار تيبثون** - `{}`\n"
    "❃ **مدة التشغيل** - `{}`\n"
    "❃ **إصدار البايثون** - `{}`\n"
    "❃ **إصدار التليثون** - `{}`\n\n"
    "@SSSTlFd"
)


# نص الفحص Inline
in_alive = (
    "{}\n\n"
    "❃ <b>إصدار النسرالاسود -></b> <code>{}</code>\n"
    "❃ <b>إصدار البايثون -></b> <code>{}</code>\n"
    "❃ <b>مدة التشغيل -></b> <code>{}</code>\n\n"
    "<b>قناة السورس @SSSTlFd</b>"
)


# فيديو الفحص
ALIVE_VIDEO = "https://files.catbox.moe/aghgg7.mp4"


# صورة بديلة إذا احتجتها
ALIVE_PIC = "https://i.ibb.co/gLZ8ZQVT/Gsz.jpg"


# رسالة callback
alive_txt = """
**سورس النسرالاسود يعمـل بنجـاح .. ✅**

❃ إصدار تيبثون - {}
❃ إصدار التليثون - {}
"""


# أمر callback للفحص
@callback("alive")
async def alive(event):
    text = alive_txt.format(version, __version__)
    await event.answer(text, alert=True)


# =========================================================
# أمر الفحص
# =========================================================

@Tepthon_cmd(pattern="فحص( (.*)|$)")
async def alive_func(e):

    match = (e.pattern_match.group(1) or "").strip()
    inline = False

    # فحص انلاين
    if match in ["انلاين", "إنلاين"]:

        try:
            res = await e.client.inline_query(
                tgbot.me.username,
                "alive"
            )

            return await res[0].click(e.chat_id)

        except BotMethodInvalidError:
            inline = False

        except BaseException as er:
            LOGS.exception(er)
            inline = False

    # اسم صاحب الحساب
    OWNER_NAME = jmubot.me.first_name or "المالك"

    # مدة التشغيل
    uptime = time_formatter(
        (time.time() - start_time) * 1000
    )

    # ==========================================
    # الفحص العادي
    # ==========================================

    if not inline:

        parse = markdown

        als = alive_1.format(
            OWNER_NAME,
            version,
            uptime,
            python_version(),
            __version__,
        )

        emoji = jmdB.get_key("ALIVE_EMOJI")

        if emoji:
            als = als.replace("❃", emoji)

        try:
            # إرسال الفيديو مباشرة
            await e.reply(
                als,
                file=ALIVE_VIDEO,
                parse_mode=parse,
                link_preview=False,
                buttons=None,
            )

            return await e.try_delete()

        except ChatSendMediaForbiddenError:
            pass

        except BaseException as er:
            LOGS.exception(er)

            # إذا فشل الفيديو، جرب الصورة
            try:

                await e.reply(
                    als,
                    file=ALIVE_PIC,
                    parse_mode=parse,
                    link_preview=False,
                    buttons=None,
                )

                return await e.try_delete()

            except BaseException as er:
                LOGS.exception(er)

    # ==========================================
    # إذا لم ينجح إرسال الوسائط
    # ==========================================

    await e.eor(
        als,
        parse_mode=parse,
        link_preview=False,
        buttons=buttons if inline else None,
    )


# =========================================================
# فحص Inline
# =========================================================

@in_pattern("alive", owner=True)
async def inline_alive(e):

    uptime = time_formatter(
        (time.time() - start_time) * 1000
    )

    als = in_alive.format(
        version,
        python_version(),
        uptime,
    )

    emoji = jmdB.get_key("ALIVE_EMOJI")

    if emoji:
        als = als.replace("❃", emoji)

    builder = e.builder

    try:

        # عرض الفيديو في Inline
        results = [
            await builder.video(
                ALIVE_VIDEO,
                text=als,
                parse_mode="html",
                buttons=buttons,
                mime_type="video/mp4",
            )
        ]

        return await e.answer(results)

    except BaseException as er:

        LOGS.exception(er)

        # محاولة الصورة كبديل
        try:

            results = [
                await builder.photo(
                    ALIVE_PIC,
                    text=als,
                    parse_mode="html",
                    buttons=buttons,
                )
            ]

            return await e.answer(results)

        except BaseException as er:

            LOGS.exception(er)

    # آخر حل: رسالة نصية
    result = [
        await builder.article(
            "Alive",
            text=als,
            parse_mode="html",
            link_preview=False,
            buttons=buttons,
        )
    ]

    await e.answer(result)


# =========================================================
# أمر معلومات الحساب
# الأمر: .ا
# =========================================================

@Tepthon_cmd(pattern="ا$")
async def account_info(event):

    try:

        # جلب الحساب الحالي
        me = await event.client.get_me()

        # الاسم
        first_name = me.first_name or ""

        last_name = me.last_name or ""

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        if not full_name:
            full_name = "لا يوجد"

        # الآيدي
        user_id = me.id

        # اليوزر
        if me.username:
            username = f"@{me.username}"
        else:
            username = "لا يوجد"

        # رتبة صاحب السورس
        rank = "مبرمج السورس"

        # البطاقة
        caption = (
            "╭─〔 معلومات الحساب 〕─╮\n\n"
            f"👤 الاسم : {full_name}\n"
            f"🆔 الايدي : {user_id}\n"
            f"🔗 اليوزر : {username}\n"
            f"👑 الرتبة : {rank}\n\n"
            "╰────────────────╯"
        )

        # ==========================================
        # جلب صورة الحساب الحالية مباشرة
        # ==========================================

        profile_photo = await event.client.download_profile_photo(
            me,
            file=bytes,
        )

        # ==========================================
        # إذا يوجد صورة
        # ==========================================

        if profile_photo:

            await event.client.send_file(
                event.chat_id,
                profile_photo,
                caption=caption,
                parse_mode="html",
            )

        # ==========================================
        # إذا لا توجد صورة
        # ==========================================

        else:

            await event.reply(
                caption,
                parse_mode="html",
            )

        # حذف أمر .ا
        try:
            await event.delete()
        except BaseException:
            pass

    except BaseException as er:

        LOGS.exception(er)

        await event.eor(
            f"<b>حدث خطأ أثناء جلب معلومات الحساب:</b>\n"
            f"<code>{er}</code>",
            parse_mode="html",
        )
