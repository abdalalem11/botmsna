
from . import zq_lo
from ...core.managers import edit_or_reply

plugin_category = "الادوات"


@zq_lo.rep_cmd(
    pattern="المطور$",
    command=("المطور", plugin_category),
    info={
        "header": "عرض معلومات مبرمج السورس",
        "الاستـخـدام": "{tr}المطور",
    },
)
async def developer_info(event):
    text = (
        "**⎉╎مبـرمـج سـورس النسر الأسود 🦅**\n\n"
        "**👤╎اليوزر :** [@SSSTlF](https://t.me/SSSTlF)\n"
        "**🆔╎ايدي المبرمج :** `1170411845`\n"
        "**🛠╎السورس :** سورس النسر الأسود\n"
    )

    await edit_or_reply(event, text)
