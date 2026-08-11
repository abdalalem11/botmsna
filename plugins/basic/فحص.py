"""
❃ `{i}فحص`
    لـ عرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ `{i}فحص انلاين`
    لعرض حالة السورس بالفيديو

❃ `{i}ا`
    لعرض معلومات الحساب ورتبة مبرمج السورس
"""

import time
from platform import python_version
from random import choice

from Tepthon.config import version
from telethon.errors import BotMethodInvalidError, ChatSendMediaForbiddenError
from telethon.extensions import html, markdown
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


# فيديو أمر فحص
ALIVE_VIDEO = "https://files.catbox.moe/aghgg7.mp4"


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


@Tepthon_cmd(pattern="ا$")
async def account_info(event):
    try:
        me = await event.client.get_me()

        first_name = me.first_name or "غير معروف"
        last_name = me.last_name or ""

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        user_id = me.id

        username = (
            f"@{me.username}"
            if me.username
            else "لا يوجد"
        )

        rank = "مبرمج السورس"

        caption = (
            "<b>╭─〔 معلومات الحساب 〕─╮</b>\n\n"
            f"👤 <b>الاسم :</b> <code>{full_name}</code>\n"
            f"🆔 <b>الآيدي :</b> <code>{user_id}</code>\n"
            f"🔗 <b>اليوزر :</b> <code>{username}</code>\n"
            f"👑 <b>الرتبة :</b> <code>{rank}</code>\n\n"
            "<b>╰────────────────╯</b>"
        )

        try:
            profile = await event.client.download_profile_photo(
                me,
                file=bytes,
            )

            if profile:
                await event.reply(
                    profile,
                    caption,
                    parse_mode="html",
                    link_preview=False,
                )

            else:
                await event.reply(
                    caption,
                    parse_mode="html",
                    link_preview=False,
                )

        except BaseException as er:
            LOGS.exception(er)

            await event.reply(
                caption,
                parse_mode="html",
                link_preview=False,
            )

        return await event.try_delete()

    except BaseException as er:
        LOGS.exception(er)

        return await event.eor(
            "<b>حدث خطأ أثناء جلب معلومات الحساب.</b>",
            parse_mode="html",
        )
