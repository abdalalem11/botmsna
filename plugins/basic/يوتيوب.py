"""
◙ `{i}تنزيل` <اسم المقطع>

مثال:
.تنزيل سورة الكهف

طريقة العمل:
1. يرسل البحث إلى @lN_3_Obot
2. ينتظر الصوت الذي يرسله البوت
3. يعيد إرسال الصوت للمستخدم مباشرة
4. يضيف حقوق SSSTlFd
"""

import asyncio

from .. import Tepthon_cmd, LOGS


# =========================================================
# البوت الذي تتم منه عملية البحث
# =========================================================

SEARCH_BOT = "@lN_3_Obot"


# =========================================================
# أمر التنزيل
#
# مثال:
# .تنزيل سورة الكهف
# =========================================================

@Tepthon_cmd(pattern=r"تنزيل(?:\s+(.+))?$")
async def download_audio(event):

    query = (
        event.pattern_match.group(1)
        or ""
    ).strip()

    # =====================================================
    # التحقق من اسم البحث
    # =====================================================

    if not query:

        return await event.eor(
            "⎆ اكتب اسم المقطع بعد الأمر\n\n"
            "مثال:\n"
            ".تنزيل سورة الكهف"
        )

    # =====================================================
    # رسالة الانتظار
    # =====================================================

    status = await event.eor(
        f"⎆ جاري البحث عن:\n"
        f"「 {query} 」\n\n"
        "⏳ انتظر قليلًا..."
    )

    try:

        # =================================================
        # فتح محادثة البوت
        # =================================================

        bot = await event.client.get_entity(
            SEARCH_BOT
        )

        # =================================================
        # إرسال البحث
        # =================================================

        sent = await event.client.send_message(
            bot,
            f"بحث {query}"
        )

        # =================================================
        # انتظار الصوت
        # =================================================

        audio_message = None

        for _ in range(30):

            await asyncio.sleep(1)

            messages = await event.client.get_messages(
                bot,
                limit=10
            )

            for message in messages:

                # تجاهل رسالة البحث نفسها
                if (
                    message.id
                    == sent.id
                ):
                    continue

                # =================================================
                # التأكد أن الرسالة تحتوي على ملف صوتي
                # =================================================

                if (
                    message.audio
                    or
                    (
                        message.document
                        and message.file
                        and message.file.mime_type
                        and message.file.mime_type.startswith(
                            "audio/"
                        )
                    )
                ):

                    audio_message = message
                    break

            if audio_message:
                break

        # =================================================
        # لم يصل الصوت
        # =================================================

        if not audio_message:

            return await status.eor(
                "❌ لم يصل الصوت من البوت.\n\n"
                "تأكد أن @lN_3_Obot يرسل الصوت مباشرة "
                "بعد أمر البحث."
            )

        # =================================================
        # إرسال الصوت للمستخدم
        # =================================================

        await event.client.send_file(
            event.chat_id,
            audio_message.media,
            caption=(
                "🎵 <b>تم العثور على المقطع</b>\n\n"
                "© <b>SSSTlFd</b>"
            ),
            parse_mode="html",
            voice_note=False,
            supports_streaming=True,
        )

        # =================================================
        # حذف رسالة الانتظار
        # =================================================

        try:
            await status.delete()
        except BaseException:
            pass

        # =================================================
        # حذف رسالة البحث من الخاص
        # =================================================

        try:
            await event.client.delete_messages(
                bot,
                sent.id
            )
        except BaseException:
            pass

    except Exception as er:

        LOGS.exception(er)

        try:

            await status.eor(
                "❌ حدث خطأ أثناء الاتصال ببوت البحث.\n\n"
                f"<code>{er}</code>",
                parse_mode="html"
            )

        except BaseException:
            pass
