"""
❃ `{i}لوك`
    لـ عرض آخر أسطر من عملية التنصيب وعرض سجل العمليات
    
❃ `{i}اعادة تشغيل`
    لـ إعـادة تشغيل سورس النسرالاسود 🧸 ( استخدمه في مجموعة الحفظ )
    
❃ `{i}تحديث`
لـ تحديث سورس تيبثون تابع قناة السورس @SSSTlF
"""


import os
import sys
import time
from Tepthon.helper.git import repo
from Tepthon.helper import check_update, bash, get_client
from .. import jmdB, Tepthon_cmd


@Tepthon_cmd(pattern="لوك( (.*)|$)")
async def logs_Tepthon(event):
    arg = event.pattern_match.group(1).strip()

    file_path = "tepthon logs"
    if not arg: 
        with open(file_path, "r") as file:
            content = file.read()[-4000:]
        return await event.eor(f"`{content}`")
    elif arg == "تلجراف":
        client = get_client()
        with open(file_path, "r") as file:
            title = "Tepthon Logs"
            page = client.create_page(title=title, content=[file.read()])
        await event.eor(f'[Tepthon Logs]({page["url"]})', link_preview=True)
    await event.eor(file=file_path)


@Tepthon_cmd(pattern="اعادة تشغيل$")
async def restart_Tepthon(event):
    await event.eor("⎆ جاريي إعادة تشغيل سورس تيبثون العربي.....")
    os.execl(sys.executable, sys.executable, "-m", "Tepthon")

@Tepthon_cmd(pattern="تحديث( (.*)|$)")
async def update_Tepthon(e):
    xx = await e.eor("**⎆ جاريي معرفة إذا كان هناك تحديثات**")
    cmd = e.pattern_match.group(1).strip()
    if cmd and ("سريع" in cmd or "خفيف" in cmd):
        await bash("git pull -f")
        await xx.edit("**⎆ جاري التحديـث الخفيف يرجى الانتظــار**")
        os.execl(sys.executable, sys.executable, "-m", "Tepthon")
    remote_url = repo.get_remote_url()
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    m = check_update()
    if not m:
        return await xx.edit(
            f'<strong>سورس النسرالاسود مُحدث بآخر إصدار</strong>',
            parse_mode="html",
            link_preview=False,
        )
    msg = await xx.eor(
        f'<strong>جاري تحديث سورس النسرالاسود يرجى الانتظار قليلًا</strong>',
        parse_mode="html",
        link_preview=False,
    )
    await update(msg)


async def update(eve):
    await bash(f"git pull && {sys.executable} -m pip install -r requirements.txt")
    os.execl(sys.executable, sys.executable, "-m", "Tepthon")
