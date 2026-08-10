"""
❃ فحص
لعرض حالة سورس النسرالاسود والإصدار ووقت التشغيل

❃ ملاحظة: يمكنك وضع أو تغيير الصورة من خلال البوت المساعد الخاص بك

❃ بنك
أمر تجريبي لتجربة السورس
"""

import time
from platform import python_version
from random import choice

from Tepthon.config import version as TEPTHON_VERSION
from telethon.errors import BotMethodInvalidError, ChatSendMediaForbiddenError
from telethon.extensions import html, markdown
from telethon.utils import resolve_bot_file_id
from telethon.version import version as TELETHON_VERSION

from .. import *

buttons = [
[
Button.url("مجموعة المساعدة", "https://t.me/SSSTlFd"),
Button.url("قناة السورس", "https://t.me/SSSTlFd"),
]
]

alive_txt = """
سورس النسرالاسود يعمـل بنجـاح .. ✅

❃ إصدار تيبثون - {}
❃ إصدار التليثون - {}
"""

PING_PIC = jmdB.get_key("PING_PIC") or "https://t.me/Tepthon/12?single"
JM_TXT = "لا تحزن لأن الله معك ♥️"

in_alive = """
{}

❃ <b>إصدار النسرالاسود -></b> <code>{}</code>
❃ <b>إصدار البايثون -></b> <code>{}</code>
❃ <b>مدة التشغيل -></b> <code>{}</code>

<b>قناة السورس @SSSTlFd</b>
"""

alive_1 = """
سورس النسرالاسود يعمل بنجاح ✅

❃ مالك الحساب - {}
❃ إصدار تيبثون - {}
❃ مدة التشغيل - {}
❃ إصدار البايثون - {}
❃ إصدار التليثون - {}

@SSSTlFd
"""

@callback("alive")
async def alive(event):
text = alive_txt.format(TEPTHON_VERSION, TELETHON_VERSION)
await event.answer(text, alert=True)

@Tepthon_cmd(pattern="فحص( (.*)|$)")
async def alive_func(e):
match = (e.pattern_match.group(1) or "").strip()
inline = False

if match in ["انلاين", "إنلاين"]:
    try:
        res = await e.client.inline_query(tgbot.me.username, "alive")
        if res:
            return await res[0].click(e.chat_id)
    except BotMethodInvalidError:
        inline = True
    except Exception as er:
        LOGS.exception(er)
        inline = True

OWNER_NAME = jmubot.me.first_name

pic = jmdB.get_key("ALIVE_PIC") or "https://envs.sh/GsK.jpg"
if isinstance(pic, list) and pic:
    pic = choice(pic)

uptime = time_formatter((time.time() - start_time) * 1000)

if inline:
    parse = html
    als = in_alive.format(
        "سورس النسرالاسود يعمل بنجاح ✅",
        TEPTHON_VERSION,
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
        TEPTHON_VERSION,
        uptime,
        python_version(),
        TELETHON_VERSION,
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

    except Exception as er:
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

        except Exception as er:
            LOGS.exception(er)

await e.eor(
    als,
    parse_mode=parse,
    link_preview=False,
    buttons=buttons if inline else None,
)

@in_pattern("alive", owner=True)
async def inline_alive(e):
pic = jmdB.get_key("ALIVE_PIC") or "https://envs.sh/Gsz.jpg"

if isinstance(pic, list) and pic:
    pic = choice(pic)

uptime = time_formatter((time.time() - start_time) * 1000)

als = in_alive.format(
    "سورس النسرالاسود يعمل بنجاح ✅",
    TEPTHON_VERSION,
    python_version(),
    uptime,
)

emoji = jmdB.get_key("ALIVE_EMOJI")
if emoji:
    als = als.replace("❃", emoji)

local_buttons = [row[:] for row in buttons]
builder = e.builder

if pic:
    try:
        clean_pic = pic.split("?")[0].lower()

        if clean_pic.endswith((".jpg", ".jpeg", ".png", ".webp")):
            results = [
                await builder.photo(
                    pic,
                    text=als,
                    parse_mode="html",
                    buttons=local_buttons,
                )
            ]
        else:
            bot_file = resolve_bot_file_id(pic)

            if bot_file:
                pic = bot_file
                local_buttons.insert(
                    0,
                    [Button.inline("Stats", data="alive")],
                )

            results = [
                await builder.document(
                    pic,
                    title="Inline Alive",
                    description="@Tepthon",
                    text=als,
                    parse_mode="html",
                    buttons=local_buttons,
                )
            ]

        return await e.answer(results)

    except Exception as er:
        LOGS.exception(er)

result = [
    await builder.article(
        "Alive",
        text=als,
        parse_mode="html",
        link_preview=False,
        buttons=local_buttons,
    )
]

await e.answer(result)

@Tepthon_cmd(pattern="بنك$")
async def ping_cmd(event):
start = time.perf_counter()

try:
    msg = await event.client.send_file(
        event.chat_id,
        PING_PIC,
        caption=(
            f"<b><i>{JM_TXT}</i></b>\n"
            f"<code>┏━━━━━━━┓\n"
            f"┃ ✦ جاري قياس السرعة...\n"
            f"┃ ✦ {jmubot.me.first_name}\n"
            f"┗━━━━━━━┛</code>"
        ),
        parse_mode="html",
        link_preview=False,
    )

    ms = round((time.perf_counter() - start) * 1000, 2)

    caption = (
        f"<b><i>{JM_TXT}</i></b>\n"
        f"<code>┏━━━━━━━┓\n"
        f"┃ ✦ {ms} ms\n"
        f"┃ ✦ {jmubot.me.first_name}\n"
        f"┗━━━━━━━┛</code>"
    )

    await msg.edit(
        caption=caption,
        parse_mode="html",
        link_preview=False,
    )

except Exception as er:
    LOGS.exception(er)

    ms = round((time.perf_counter() - start) * 1000, 2)

    await event.respond(
        f"<b><i>{JM_TXT}</i></b>\n\n"
        f"<b>سرعة الاستجابة:</b> <code>{ms} ms</code>",
        parse_mode="html",
    )

return await event.delete()
