"""
◙ `{i}تنزيل` <اسم المقطع>
   البحث عن المقطع وتنزيله صوتيًا مباشرة.

مثال:
.تنزيل سورة الكهف
.تنزيل اسم الأغنية

يتم وضع حقوق SSSTlFd مع كل ملف.
"""

import os
import tempfile
from yt_dlp import YoutubeDL

from .. import Tepthon_cmd


# =========================================================
# إعدادات التحميل
# =========================================================

DOWNLOAD_DIR = os.path.join(
    tempfile.gettempdir(),
    "tepthon_downloads"
)

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


# =========================================================
# أمر التنزيل
#
# .تنزيل سورة الكهف
# =========================================================

@Tepthon_cmd(pattern=r"تنزيل(?:\s+(.+))?$")
async def download_audio(event):

    query = (
        event.pattern_match.group(1)
        or ""
    ).strip()

    # =====================================================
    # التأكد من وجود بحث
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

    msg = await event.eor(
        f"⎆ جاري البحث عن:\n"
        f"「 {query} 」\n\n"
        "يرجى الانتظار..."
    )

    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    # =====================================================
    # إعدادات yt-dlp
    # =====================================================

    ytd = {
        "format": "bestaudio/best",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "default_search": "ytsearch",

        "outtmpl": output_template,

        "geo_bypass": True,

        "nocheckcertificate": True,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],

        "postprocessor_args": [
            "-metadata",
            "artist=SSSTlFd",
            "-metadata",
            "album=SSSTlFd",
            "-metadata",
            "comment=SSSTlFd",
        ],
    }

    downloaded_file = None

    try:

        # =================================================
        # البحث في يوتيوب
        # =================================================

        search_query = f"ytsearch1:{query}"

        with YoutubeDL(ytd) as ydl:

            info = await event.client.loop.run_in_executor(
                None,
                lambda: ydl.extract_info(
                    search_query,
                    download=True
                )
            )

        if not info:

            return await msg.eor(
                "⎆ لم يتم العثور على نتيجة."
            )

        # =================================================
        # الحصول على نتيجة البحث
        # =================================================

        if "entries" in info:

            entries = info.get("entries")

            if not entries:

                return await msg.eor(
                    "⎆ لم يتم العثور على المقطع."
                )

            video = entries[0]

        else:

            video = info

        # =================================================
        # معلومات المقطع
        # =================================================

        title = (
            video.get("title")
            or query
        )

        video_id = video.get(
            "id"
        )

        # =================================================
        # البحث عن الملف الناتج
        # =================================================

        possible_files = []

        if video_id:

            for ext in [
                "mp3",
                "m4a",
                "webm",
                "opus",
            ]:

                path = os.path.join(
                    DOWNLOAD_DIR,
                    f"{video_id}.{ext}"
                )

                if os.path.exists(path):

                    possible_files.append(
                        path
                    )

        # =================================================
        # اختيار الملف
        # =================================================

        if possible_files:

            downloaded_file = (
                possible_files[0]
            )

        else:

            # البحث عن آخر ملف تم إنشاؤه
            files = [
                os.path.join(
                    DOWNLOAD_DIR,
                    f
                )
                for f in os.listdir(
                    DOWNLOAD_DIR
                )
            ]

            files = [
                f
                for f in files
                if os.path.isfile(f)
            ]

            if files:

                downloaded_file = max(
                    files,
                    key=os.path.getmtime
                )

        # =================================================
        # التأكد من الملف
        # =================================================

        if not downloaded_file:

            return await msg.eor(
                "⎆ تعذر العثور على الملف بعد التحميل."
            )

        # =================================================
        # اسم الملف وحقوق السورس
        # =================================================

        safe_title = (
            title
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .strip()
        )

        filename = (
            f"{safe_title} - SSSTlFd.mp3"
        )

        # =================================================
        # إرسال الصوت مباشرة
        # =================================================

        await msg.eor(
            "⎆ تم العثور على المقطع ✅\n"
            "⎆ جاري إرساله..."
        )

        await event.client.send_file(
            event.chat_id,
            downloaded_file,
            caption=(
                f"🎵 <b>{title}</b>\n\n"
                f"© <b>SSSTlFd</b>"
            ),
            parse_mode="html",
            voice_note=False,
            supports_streaming=True,
            attributes=[],
        )

        # =================================================
        # حذف رسالة الانتظار
        # =================================================

        try:

            await msg.delete()

        except BaseException:

            pass

    except Exception as er:

        LOGS.exception(er)

        try:

            await msg.eor(
                "⎆ حدث خطأ أثناء البحث أو التحميل.\n\n"
                f"<code>{er}</code>",
                parse_mode="html"
            )

        except BaseException:

            pass

    finally:

        # =================================================
        # حذف الملف من السيرفر
        # =================================================

        if downloaded_file:

            try:

                if os.path.exists(
                    downloaded_file
                ):

                    os.remove(
                        downloaded_file
                    )

            except BaseException:

                pass
