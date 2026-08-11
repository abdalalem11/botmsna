"""
◙ `{i}تنزيل` <اسم المقطع>

للبحث عن مقطع وتنزيله صوتيًا مباشرة.

أمثلة:
.تنزيل سورة الكهف
.تنزيل اسم المقطع

حقوق السورس:
SSSTlFd
"""

import os
import tempfile
from yt_dlp import YoutubeDL

from .. import Tepthon_cmd, LOGS


# =========================================================
# مجلد التحميل
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
# تنظيف الملفات القديمة
# =========================================================

def cleanup_downloads():
    try:
        for name in os.listdir(DOWNLOAD_DIR):
            path = os.path.join(
                DOWNLOAD_DIR,
                name
            )

            if os.path.isfile(path):
                try:
                    os.remove(path)
                except BaseException:
                    pass

    except BaseException:
        pass


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
    # التحقق من البحث
    # =====================================================

    if not query:

        return await event.eor(
            "⎆ اكتب اسم المقطع بعد الأمر\n\n"
            "مثال:\n"
            ".تنزيل سورة الكهف"
        )

    # =====================================================
    # رسالة البحث
    # =====================================================

    msg = await event.eor(
        f"⎆ جاري البحث عن:\n"
        f"「 {query} 」\n\n"
        "⏳ يرجى الانتظار..."
    )

    # =====================================================
    # تنظيف الملفات القديمة
    # =====================================================

    cleanup_downloads()

    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    # =====================================================
    # إعداد yt-dlp
    # =====================================================

    ytd = {
        "format": "bestaudio/best",

        "noplaylist": True,

        "quiet": False,

        "no_warnings": False,

        "outtmpl": output_template,

        "default_search": "ytsearch",

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
        # البحث + التنزيل
        # =================================================

        search_query = (
            f"ytsearch1:{query}"
        )

        def do_download():

            with YoutubeDL(ytd) as ydl:

                return ydl.extract_info(
                    search_query,
                    download=True
                )

        info = await event.client.loop.run_in_executor(
            None,
            do_download
        )

        # =================================================
        # التحقق من النتيجة
        # =================================================

        if not info:

            return await msg.eor(
                "❌ لم يتم العثور على أي نتيجة."
            )

        entries = info.get("entries")

        if entries:

            video = entries[0]

        else:

            video = info

        if not video:

            return await msg.eor(
                "❌ لم يتم العثور على المقطع."
            )

        # =================================================
        # بيانات المقطع
        # =================================================

        title = (
            video.get("title")
            or query
        )

        video_id = video.get(
            "id"
        )

        # =================================================
        # العثور على الملف
        # =================================================

        if video_id:

            for ext in (
                "mp3",
                "m4a",
                "webm",
                "opus",
            ):

                path = os.path.join(
                    DOWNLOAD_DIR,
                    f"{video_id}.{ext}"
                )

                if os.path.isfile(path):

                    downloaded_file = path
                    break

        # =================================================
        # بحث احتياطي
        # =================================================

        if not downloaded_file:

            files = []

            try:

                for name in os.listdir(
                    DOWNLOAD_DIR
                ):

                    path = os.path.join(
                        DOWNLOAD_DIR,
                        name
                    )

                    if os.path.isfile(path):

                        files.append(path)

            except BaseException:
                files = []

            if files:

                downloaded_file = max(
                    files,
                    key=os.path.getmtime
                )

        # =================================================
        # التأكد من وجود الملف
        # =================================================

        if not downloaded_file:

            return await msg.eor(
                "❌ تم العثور على المقطع، "
                "لكن لم يتم إنشاء الملف الصوتي."
            )

        # =================================================
        # تحديث الرسالة
        # =================================================

        await msg.eor(
            "⎆ تم العثور على المقطع ✅\n"
            "⎆ جاري إرسال الصوت..."
        )

        # =================================================
        # إرسال الصوت مباشرة
        # =================================================

        await event.client.send_file(
            event.chat_id,

            downloaded_file,

            caption=(
                f"🎵 <b>{title}</b>\n\n"
                "© <b>SSSTlFd</b>"
            ),

            parse_mode="html",

            voice_note=False,

            supports_streaming=True,
        )

        # =================================================
        # حذف رسالة التحميل
        # =================================================

        try:
            await msg.delete()
        except BaseException:
            pass

    except Exception as er:

        # =================================================
        # تسجيل الخطأ
        # =================================================

        try:
            LOGS.exception(er)
        except BaseException:
            pass

        error = str(er)

        lower_error = error.lower()

        # =================================================
        # YouTube Anti-Bot
        # =================================================

        if (
            "sign in to confirm" in lower_error
            or
            "not a bot" in lower_error
            or
            "confirm you're not a bot" in lower_error
        ):

            text = (
                "❌ تعذر تنزيل المقطع من YouTube.\n\n"
                "يوتيوب طلب التحقق من الطلب، "
                "ولم يسمح بعملية التنزيل."
            )

        # =================================================
        # FFmpeg
        # =================================================

        elif (
            "ffmpeg" in lower_error
            or
            "postprocessor" in lower_error
        ):

            text = (
                "❌ تعذر تحويل الصوت.\n\n"
                "تأكد من أن FFmpeg مثبت في Render."
            )

        # =================================================
        # باقي الأخطاء
        # =================================================

        else:

            text = (
                "❌ حدث خطأ أثناء البحث أو التنزيل.\n\n"
                f"<code>{error}</code>"
            )

        try:

            await msg.eor(
                text,
                parse_mode="html"
            )

        except BaseException:
            pass

    finally:

        # =================================================
        # حذف الملف بعد الإرسال
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
