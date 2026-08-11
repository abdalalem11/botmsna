"""
❃ `{i}فحص`
    لـ عرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ ملاحظة: يمكنك وضع أو تغيير الفيديو من خلال البوت المساعد الخاص بك

❃ `{i}بنك`
    أمر تجريبي لتجربة السورس
"""

import time
from datetime import datetime
from platform import python_version
from random import choice

from Tepthon.config import version
from telethon.errors import BotMethodInvalidError, ChatSendMediaForbiddenError
from telethon.extensions import html, markdown
from telethon.utils import resolve_bot_file_id
from telethon.version import __version__

from .. import *


buttons = [
    [
        Button.url("مجموعة المساعدة", "https://t.me/SSSTlFd"),
        Button.url("قناة السورس", "https://t.me/SSSTlFd"),
    ]
]


alive_txt = """
**سورس النسرالاسود يعمـل بنجـاح .. ✅**

❃ إصدار تيبثون - {}
❃ إصدار التليثون - {}
"""


# صورة أمر بنك
PING_PIC = (
    jmdB.get_key("PING_PIC")
    or "https://i.ibb.co/gLZ8ZQVT/Gsz.jpg"
)

# فيديو أمر فحص
ALIVE_VIDEO = "https://files.catbox.moe/aghgg7.mp4"

JM_TXT = "لا تحزن لأن الله معك ♥️"


in_alive = (
    "{}\n\n"
    "❃ <b>إصدار النسرالاسود -></b> <code>{}</code>\n"
    "❃ <b>إصدار البايثون -></b> <code>{}</code>\n"
    "❃ <b>مدة التشغيل -></b> <code>{}</code>\n\n"
    "<b>قناة السورس @SSSTlFd</b>"
)


alive_1 = (
    "**سورس النسرالاسود يعمل بنجاح ✅**\n\n"
    "❃ **مالك الحساب** - `{}`\n"
    "❃ **إصدار تيبثون** - `{}`\n"
    "❃ **مدة التشغيل** - `{}`\n"
    "❃ **إصدار البايثون** - `{}`\n"
    "❃ **إصدار التليثون** - `{}`\n\n"
    "@SSSTlFd"
)


@callback("alive")
async def alive(event):
    text = alive_txt.format(version, __version__)
    await event.answer(text, alert=True)


@Tepthon_cmd(pattern="فحص( (.*)|$)")
async def alive_func(e):
    match = (e.pattern_match.group(1) or "").strip()
    inline = False

    if match in ["انلاين", "إنلاين"]:
        try:
            res = await e.client.inline_query(
                tgbot.me.username,
                "alive",
            )
            return await res[0].click(e.chat_id)

        except BotMethodInvalidError:
            inline = False

        except BaseException as er:
            LOGS.exception(er)
            inline = False

    OWNER_NAME = jmubot.me.first_name or "المالك"

    # فيديو الفحص
    pic = ALIVE_VIDEO

    if isinstance(pic, list) and pic:
        pic = choice(pic)

    uptime = time_formatter(
        (time.time() - start_time) * 1000
    )

    if inline:
        parse = html

        als = in_alive.format(
            version,
            python_version(),
            uptime,
        )

        emoji = jmdB.get_key("ALIVE_EMOJI")

        if emoji:
            als = als.replace("❃", emoji)

    else:
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

    if pic:
        try:
            await e.reply(
                als,
                file=pic,
                parse_mode=parse,
                link_preview=False,
                buttons=buttons if inline else None,
            )

            return await e.try_delete()

        except ChatSendMediaForbiddenError:
            pass

        except BaseException as er:
            LOGS.exception(er)

            try:
                await e.reply(file=pic)

                await e.reply(
                    als,
                    parse_mode=parse,
                    buttons=buttons if inline else None,
                    link_preview=False,
                )

                return await e.try_delete()

            except BaseException as er:
                LOGS.exception(er)

    await e.eor(
        als,
        parse_mode=parse,
        link_preview=False,
        buttons=buttons if inline else None,
    )


@in_pattern("alive", owner=True)
async def inline_alive(e):
    # فيديو الفحص الإنلاين
    pic = ALIVE_VIDEO

    if isinstance(pic, list) and pic:
        pic = choice(pic)

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

    if pic:
        try:
            if str(pic).lower().split("?")[0].endswith(".mp4"):

                results = [
                    await builder.document(
                        pic,
                        title="Alive Video",
                        description="@SSSTlFd",
                        type="video",
                        mime_type="video/mp4",
                        text=als,
                        parse_mode="html",
                        buttons=buttons,
                    )
                ]

            else:
                results = [
                    await builder.article(
                        "Alive",
                        text=als,
                        parse_mode="html",
                        link_preview=False,
                        buttons=buttons,
                    )
                ]

            return await e.answer(results)

        except BaseException as er:
            LOGS.exception(er)

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


@Tepthon_cmd(pattern="بنك$")
async def ping_cmd(event):
    start = datetime.now()

    await event.client.get_me()

    ms = (
        datetime.now() - start
    ).total_seconds() * 1000

    caption = (
        f"<b><i>{JM_TXT}</i></b>\n"
        f"<code>"
        f"┏━━━━━━━┓\n"
        f"┃ ✦ {ms:.2f} ms\n"
        f"┃ ✦ {jmubot.me.first_name}\n"
        f"┗━━━━━━━┛"
        f"</code>"
    )

    try:
        # إرسال صورة البنك من الرابط المباشر
        await event.client.send_file(
            event.chat_id,
            PING_PIC,
            caption=caption,
            parse_mode="html",
            link_preview=False,
        )

    except BaseException as er:
        LOGS.exception(er)

        return await event.eor(
            f"<b>خطأ في إرسال صورة البنك:</b>\n"
            f"<code>{er}</code>",
            parse_mode="html",
        )

    return await event.delete()
