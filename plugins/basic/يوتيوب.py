"""
◙ `{i}تنزيل` <اسم المقطع>
   يبحث عن المقطع تلقائيًا ثم ينزله صوتيًا ويرسله مباشرة.

مثال:
.تنزيل سورة الكهف
.تنزيل اسم الأغنية

حقوق الملفات:
SSSTlFd
"""

import os
import tempfile
from yt_dlp import YoutubeDL

from .. import Tepthon_cmd


DOWNLOAD_DIR = os.path.join(
    tempfile.gettempdir(),
    "tepthon_downloads"
)

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


@Tepthon_cmd(pattern=r"تنزيل(?:\s+(.+))?$")
async def download_audio(event):

    query = (
        event.pattern_match.group(1)
        or ""
    ).strip()

    if not query:
        return await event.eor(
            "⎆ اكتب اسم المقطع بعد الأمر\n\n"
            "مثال:\n"
            ".تنزيل سورة الكهف"
        )

    msg = await event.eor(
        f"⎆ جاري البحث عن:\n"
        f"「 {query} 」\n\n"
        "⏳ يرجى الانتظار..."
    )

    output_template = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    ytd = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": output_template,
        "geo_bypass": True,
        "nocheckcertificate": True,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            },
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
        # البحث عن أول نتيجة
        # =================================================

        search_query = (
            f"ytsearch1:{query}"
        )

        def download():

            with YoutubeDL(ytd) as ydl:

                return ydl.extract_info(
                    search_query,
                    download=True
                )

        info = await event.client.loop.run_in_executor(
            None,
            download
        )

        if not info:

            return await msg.eor(
                "⎆ لم يتم العثور على المقطع."
            )

        # =================================================
        # الحصول على النتيجة
        # =================================================

        entries = info.get("entries")

        if entries:

            video = entries[0]

        else:

            video = info

        if not video:

            return await msg.eor(
                "⎆ لم يتم العثور على نتيجة."
            )

        title = (
            video.get("title")
            or query
        )

        video_id = video.get("id")

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
        # البحث الاحتياطي عن الملف
        # =================================================

        if not downloaded_file:

            files = []

            for name in os.listdir(
                DOWNLOAD_DIR
            ):

                path = os.path.join(
                    DOWNLOAD_DIR,
                    name
                )

                if os.path.isfile(path):

                    files.append(path)

            if files:

                downloaded_file = max(
                    files,
                    key=os.path.getmtime
                )

        # =================================================
        # لم يتم إنشاء الملف
        # =================================================

        if not downloaded_file:

            return await msg.eor(
                "⎆ تم العثور على المقطع، "
                "لكن تعذر إنشاء الملف الصوتي."
            )

        # =================================================
        # إرسال الملف مباشرة
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
            await msg.delete()
        except BaseException:
            pass

    except Exception as er:

        LOGS.exception(er)

        error_text = str(er).lower()

        # =================================================
        # خطأ YouTube الخاص بالتحقق
        # =================================================

        if (
            "sign in to confirm" in error_text
            or "not a bot" in error_text
        ):

            text = (
                "⎆ تعذر تنزيل المقطع من YouTube.\n\n"
                "يوتيوب طلب التحقق من الطلب، "
                "لذلك لم يتمكن السورس من إكمال التنزيل."
            )

        else:

            text = (
                "⎆ حدث خطأ أثناء البحث أو التحميل.\n\n"
                f"<code>{er}</code>"
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
