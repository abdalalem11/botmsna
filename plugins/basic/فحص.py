"""
❃ `{i}فحص`
    لـ عرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ `{i}فحص انلاين`
    لعرض حالة السورس بشكل Inline

❃ `{i}ا`
    لعرض معلومات الحساب وصورته الحالية

❃ ملاحظة:
    صورة الفحص يمكن تغييرها من خلال ALIVE_PIC
"""

import time
from io import BytesIO
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
        Button.url("مجموعة المساعدة", "https://t.me/SSSTlFd"),
        Button.url("قناة السورس", "https://t.me/SSSTlFd"),
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
# Callback للفحص
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
    # جلب اسم صاحب الحساب
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
    # تجهيز نص الفحص
    # =====================================================

    als = alive_1.format(
        owner_name,
        version,
        uptime,
        python_version(),
        __version__,
    )

    # =====================================================
    # الإيموجي المخصص
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
    # إرسال فيديو الفحص
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
    # إذا فشل الفيديو يتم إرسال الصورة
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
    # آخر حل: إرسال النص فقط
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

    # =====================================================
    # مدة التشغيل
    # =====================================================

    uptime = time_formatter(
        (time.time() - start_time) * 1000
    )

    # =====================================================
    # نص Inline
    # =====================================================

    als = in_alive.format(
        version,
        python_version(),
        uptime,
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

    builder = e.builder

    # =====================================================
    # محاولة عرض الفيديو
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
    # محاولة عرض الصورة
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
    # آخر حل: نتيجة نصية
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
#
# يعرض:
# الاسم
# الآيدي
# اليوزر
# الرتبة
# صورة الحساب الحالية
# =========================================================

@Tepthon_cmd(pattern="ا$")
async def account_info(event):

    try:

        # =================================================
        # جلب الحساب الحالي
        # =================================================

        me = await event.client.get_me()

        # =================================================
        # الاسم
        # =================================================

        first_name = (
            me.first_name
            or ""
        )

        last_name = (
            me.last_name
            or ""
        )

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        if not full_name:
            full_name = "لا يوجد"

        # =================================================
        # الآيدي
        # =================================================

        user_id = me.id

        # =================================================
        # اليوزر
        # =================================================

        if me.username:

            username = (
                f"@{me.username}"
            )

        else:

            username = "لا يوجد"

        # =================================================
        # الرتبة
        # =================================================

        rank = "مبرمج السورس"

        # =================================================
        # بطاقة معلومات الحساب
        # =================================================

        caption = (
            "╭─〔 معلومات الحساب 〕─╮\n\n"
            f"👤 الاسم : {full_name}\n"
            f"🆔 الايدي : {user_id}\n"
            f"🔗 اليوزر : {username}\n"
            f"👑 الرتبة : {rank}\n\n"
            "╰────────────────╯"
        )

        # =================================================
        # جلب صورة الحساب الحالية
        # =================================================

        profile_photo = (
            await event.client.download_profile_photo(
                me,
                file=bytes,
            )
        )

        # =================================================
        # إذا الحساب لديه صورة
        # =================================================

        if profile_photo:

            # تحويل البيانات إلى ملف ذاكرة
            image = BytesIO(
                profile_photo
            )

            # مهم:
            # إعطاء الملف امتداد صورة
            image.name = "profile.jpg"

            # =================================================
            # إرسال الصورة كصورة Telegram مباشرة
            # =================================================

            await event.client.send_file(
                event.chat_id,
                image,
                caption=caption,
                force_document=False,
                supports_streaming=False,
            )

        # =================================================
        # إذا الحساب بدون صورة
        # =================================================

        else:

            await event.reply(
                caption
            )

        # =================================================
        # حذف رسالة .ا
        # =================================================

        try:

            await event.delete()

        except BaseException:

            pass

    except BaseException as er:

        # =================================================
        # تسجيل الخطأ في اللوج
        # =================================================

        LOGS.exception(er)

        # =================================================
        # إظهار الخطأ للمستخدم
        # =================================================

        try:

            await event.eor(
                "<b>حدث خطأ أثناء جلب معلومات الحساب:</b>\n"
                f"<code>{er}</code>",
                parse_mode="html",
            )

        except BaseException:

            pass
