"""
❃ `{i}فحص`
    لـ عرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ `{i}فحص انلاين`
    لعرض حالة السورس بشكل Inline

❃ `{i}ا`
    لعرض معلومات الحساب وصورته الحالية
"""

import os
import tempfile
import time
from platform import python_version

from Tepthon.config import version
from telethon.errors import BotMethodInvalidError
from telethon.extensions import markdown
from telethon.version import __version__

from .. import *


# =========================================================
# أزرار الفحص
# =========================================================

buttons = [
    [
        Button.url(
            "مجموعة المساعدة",
            "https://t.me/SSSTlFd"
        ),
        Button.url(
            "قناة السورس",
            "https://t.me/SSSTlFd"
        ),
    ]
]


# =========================================================
# نص الفحص العادي
# =========================================================

alive_1 = (
    "**سورس النسرالاسود يعمل بنجاح ✅**\n\n"
    "❃ **مالك الحساب** - `{}`\n"
    "❃ **إصدار تيبثون** - `{}`\n"
    "❃ **مدة التشغيل** - `{}`\n"
    "❃ **إصدار البايثون** - `{}`\n"
    "❃ **إصدار التليثون** - `{}`\n\n"
    "@SSSTlFd"
)


# =========================================================
# نص الفحص Inline
# =========================================================

in_alive = (
    "سورس النسرالاسود يعمل بنجاح ✅\n\n"
    "❃ <b>إصدار النسرالاسود -></b> <code>{}</code>\n"
    "❃ <b>إصدار البايثون -></b> <code>{}</code>\n"
    "❃ <b>مدة التشغيل -></b> <code>{}</code>\n\n"
    "<b>قناة السورس @SSSTlFd</b>"
)


# =========================================================
# فيديو الفحص
# =========================================================

ALIVE_VIDEO = "https://files.catbox.moe/aghgg7.mp4"


# =========================================================
# صورة الفحص الاحتياطية
# =========================================================

ALIVE_PIC = "https://i.ibb.co/gLZ8ZQVT/Gsz.jpg"


# =========================================================
# رسالة Callback
# =========================================================

alive_txt = """
**سورس النسرالاسود يعمـل بنجـاح .. ✅**

❃ إصدار تيبثون - {}
❃ إصدار التليثون - {}
"""


# =========================================================
# Callback الفحص
# =========================================================

@callback("alive")
async def alive(event):

    text = alive_txt.format(
        version,
        __version__,
    )

    await event.answer(
        text,
        alert=True,
    )


# =========================================================
# أمر الفحص
#
# .فحص
# .فحص انلاين
# =========================================================

@Tepthon_cmd(pattern="فحص( (.*)|$)")
async def alive_func(e):

    match = (
        e.pattern_match.group(1) or ""
    ).strip()

    # =====================================================
    # فحص Inline
    # =====================================================

    if match in ["انلاين", "إنلاين"]:

        try:

            res = await e.client.inline_query(
                tgbot.me.username,
                "alive",
            )

            if res:
                return await res[0].click(
                    e.chat_id
                )

        except BotMethodInvalidError:
            pass

        except BaseException as er:
            LOGS.exception(er)

    # =====================================================
    # اسم الحساب
    # =====================================================

    try:

        me = await e.client.get_me()

        owner_name = (
            me.first_name
            or "المالك"
        )

    except BaseException:

        owner_name = "المالك"

    # =====================================================
    # مدة التشغيل
    # =====================================================

    uptime = time_formatter(
        (time.time() - start_time) * 1000
    )

    # =====================================================
    # نص الفحص
    # =====================================================

    als = alive_1.format(
        owner_name,
        version,
        uptime,
        python_version(),
        __version__,
    )

    # =====================================================
    # الإيموجي
    # =====================================================

    emoji = jmdB.get_key(
        "ALIVE_EMOJI"
    )

    if emoji:

        als = als.replace(
            "❃",
            emoji,
        )

    # =====================================================
    # إرسال الفيديو
    # =====================================================

    try:

        await e.reply(
            als,
            file=ALIVE_VIDEO,
            parse_mode=markdown,
            link_preview=False,
            buttons=None,
        )

        try:
            await e.delete()
        except BaseException:
            pass

        return

    except BaseException as er:

        LOGS.exception(er)

    # =====================================================
    # إرسال الصورة الاحتياطية
    # =====================================================

    try:

        await e.reply(
            als,
            file=ALIVE_PIC,
            parse_mode=markdown,
            link_preview=False,
            buttons=None,
        )

        try:
            await e.delete()
        except BaseException:
            pass

        return

    except BaseException as er:

        LOGS.exception(er)

    # =====================================================
    # آخر حل: نص
    # =====================================================

    try:

        await e.eor(
            als,
            parse_mode=markdown,
            link_preview=False,
        )

    except BaseException as er:

        LOGS.exception(er)


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

    emoji = jmdB.get_key(
        "ALIVE_EMOJI"
    )

    if emoji:

        als = als.replace(
            "❃",
            emoji,
        )

    builder = e.builder

    # =====================================================
    # الفيديو
    # =====================================================

    try:

        results = [
            await builder.video(
                ALIVE_VIDEO,
                text=als,
                parse_mode="html",
                buttons=buttons,
                mime_type="video/mp4",
            )
        ]

        return await e.answer(
            results
        )

    except BaseException as er:

        LOGS.exception(er)

    # =====================================================
    # الصورة
    # =====================================================

    try:

        results = [
            await builder.photo(
                ALIVE_PIC,
                text=als,
                parse_mode="html",
                buttons=buttons,
            )
        ]

        return await e.answer(
            results
        )

    except BaseException as er:

        LOGS.exception(er)

    # =====================================================
    # النص
    # =====================================================

    try:

        result = [
            await builder.article(
                "Alive",
                text=als,
                parse_mode="html",
                link_preview=False,
                buttons=buttons,
            )
        ]

        return await e.answer(
            result
        )

    except BaseException as er:

        LOGS.exception(er)


# =========================================================
# أمر معلومات الحساب
#
# .ا
# =========================================================

@Tepthon_cmd(pattern="ا$")
async def account_info(event):

    temp_photo = None

    try:

        # =================================================
        # جلب الحساب الحالي
        # =================================================

        me = await event.client.get_me()

        # =================================================
        # الاسم
        # =================================================

        first_name = me.first_name or ""
        last_name = me.last_name or ""

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        if not full_name:
            full_name = "لا يوجد"

        # =================================================
        # اليوزر
        # =================================================

        if me.username:

            username = f"@{me.username}"

        else:

            username = "لا يوجد"

        # =================================================
        # الآيدي
        # =================================================

        user_id = me.id

        # =================================================
        # البايو
        # =================================================

        try:

            from telethon.tl.functions.users import (
                GetFullUserRequest
            )

            full_user = await event.client(
                GetFullUserRequest(me)
            )

            bio = (
                full_user.full_user.about
                or "لا يوجد"
            )

        except BaseException:

            bio = "لا يوجد"

        # =================================================
        # اللقب
        # =================================================

        nickname = (
            me.last_name
            if me.last_name
            else "لا يوجد"
        )

        # =================================================
        # الرتبة
        # =================================================

        rank = "مبرمج السورس"

        # =================================================
        # بيانات وهمية
        # =================================================

        messages_count = "1,284"

        edits_count = "137"

        points = "9,650"

        photos_count = "86"

        interaction = "92%"

        contacts_count = "214"

        comments_count = "73"

        # =================================================
        # قالب الآيدي
        #
        # كل السطر Bold بالكامل
        # =================================================

        caption = (
            "<b>▹ #الاسم - "
            f"{full_name} .</b>\n"

            "<b>▹ #اليوزر - "
            f"{username} .</b>\n"

            "<b>▹ #الرسائل - "
            f"{messages_count} .</b>\n"

            "<b>▹ #الايدي - "
            f"{user_id} .</b>\n"

            "<b>▹ #الرتبه - "
            f"{rank} .</b>\n"

            "<b>▹ #التعديل - "
            f"{edits_count} .</b>\n"

            "<b>▹ #النقاط - "
            f"{points} .</b>\n"

            "<b>▹ #الصور - "
            f"{photos_count} .</b>\n"

            "<b>▹ #التفاعل - "
            f"{interaction} .</b>\n"

            "<b>▹ #البايو - "
            f"{bio} .</b>\n"

            "<b>▹ #اللقب - "
            f"{nickname} .</b>\n"

            "<b>▹ #الجهات - "
            f"{contacts_count} .</b>\n"

            "<b>▹ #التعليقات - "
            f"{comments_count} .</b>"
        )

        # =================================================
        # إنشاء ملف مؤقت للصورة
        # =================================================

        temp = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False,
        )

        temp_photo = temp.name
        temp.close()

        # =================================================
        # تحميل صورة الحساب الحالية
        # =================================================

        downloaded = (
            await event.client.download_profile_photo(
                me,
                file=temp_photo,
            )
        )

        # =================================================
        # إرسال الصورة مباشرة
        # =================================================

        if downloaded:

            await event.client.send_file(
                event.chat_id,
                temp_photo,
                caption=caption,
                parse_mode="html",
                force_document=False,
                supports_streaming=False,
            )

        # =================================================
        # إذا لا توجد صورة
        # =================================================

        else:

            await event.reply(
                caption,
                parse_mode="html",
            )

        # =================================================
        # حذف رسالة .ا
        # =================================================

        try:

            await event.delete()

        except BaseException:

            pass

    except BaseException as er:

        LOGS.exception(er)

        try:

            await event.eor(
                "<b>حدث خطأ أثناء جلب معلومات الحساب:</b>\n"
                f"<code>{er}</code>",
                parse_mode="html",
            )

        except BaseException:

            pass

    finally:

        # =================================================
        # حذف الصورة المؤقتة
        # =================================================

        if temp_photo:

            try:

                if os.path.exists(temp_photo):

                    os.remove(temp_photo)

            except BaseException:

                pass
