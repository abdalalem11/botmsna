# -*- coding: utf-8 -*-
"""
Tepthon Multi-Account Installer
--------------------------------
ضع هذا الملف داخل:
plugins/account/

الأوامر:
.تنصيب
    يطلب Session String برسالة منفصلة ثم يشغل الحساب.

.تنصيب <SESSION>
    يثبت الحساب مباشرة.

.حسابات
    يعرض الحسابات الإضافية.

.حذف حساب account1
    يوقف ويحذف حساباً إضافياً.

مهم:
- API_ID و API_HASH تبقى نفسها.
- كل حساب له Session String مختلفة.
- الحسابات الإضافية تعمل في عمليات مستقلة من نفس سورس Tepthon.
- التخزين محلي في database/extra_accounts.json.
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

from telethon import events

from .. import JmdB, jmubot, Tepthon_cmd


# الحسابات الإضافية لا تدير حسابات أخرى حتى لا يحدث تشغيل متكرر.
CHILD_FLAG = "TEPTHON_EXTRA_ACCOUNT"

if os.getenv(CHILD_FLAG) != "1":
    ACCOUNTS_FILE = Path("database") / "extra_accounts.json"
    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    _children = {}
    _pending_install = set()

    def _load_accounts():
        try:
            if not ACCOUNTS_FILE.exists():
                return {}
            data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_accounts(data):
        ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp = ACCOUNTS_FILE.with_suffix(".tmp")
        temp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp.replace(ACCOUNTS_FILE)

    def _is_owner(event):
        try:
            owner = JmdB.get_key("OWNER_ID")
            return owner is not None and int(owner) == int(event.sender_id)
        except Exception:
            return False

    def _start_account(name, session):
        env = os.environ.copy()
        env["SESSION"] = session
        env[CHILD_FLAG] = "1"
        env["TEPTHON_ACCOUNT_NAME"] = name

        return subprocess.Popen(
            [sys.executable, "-m", "Tepthon"],
            cwd=os.getcwd(),
            env=env,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _stop_account(proc):
        if not proc or proc.poll() is not None:
            return
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass

    async def _ask_for_session(event):
        future = event.client.loop.create_future()

        async def receive(reply_event):
            if reply_event.sender_id != event.sender_id:
                return
            if reply_event.chat_id != event.chat_id:
                return

            text = (reply_event.raw_text or "").strip()
            if not future.done():
                future.set_result((text, reply_event))

        event.client.add_event_handler(
            receive,
            events.NewMessage(
                chats=event.chat_id,
                from_users=event.sender_id,
            ),
        )

        try:
            await event.eor(
                "**⎆ أرسل Session String للحساب الجديد الآن.**\n\n"
                "سيتم حذف رسالتك بعد استلامها.\n"
                "⚠️ استخدم Session لحساب تملكه فقط."
            )
            text, reply_event = await asyncio.wait_for(future, timeout=120)
            return text, reply_event
        except asyncio.TimeoutError:
            return None, None
        finally:
            event.client.remove_event_handler(receive)

    @Tepthon_cmd(pattern=r"تنصيب(?:\s+([\s\S]+))?$")
    async def install_account(event):
        if not _is_owner(event):
            return

        session = (event.pattern_match.group(1) or "").strip()
        reply_event = None

        if not session:
            session, reply_event = await _ask_for_session(event)

        if not session:
            return await event.eor("**⎆ انتهى وقت انتظار الـ Session.**")

        # StringSession القياسية في Telethon تكون أطول من ذلك.
        if len(session) < 300:
            return await event.eor("**⎆ الـ Session قصيرة أو غير صحيحة.**")

        accounts = _load_accounts()

        if any(item.get("session") == session for item in accounts.values()):
            return await event.eor("**⎆ هذا الحساب مثبت مسبقاً.**")

        index = 1
        while f"account{index}" in accounts:
            index += 1

        name = f"account{index}"
        accounts[name] = {"session": session}
        _save_accounts(accounts)

        status = await event.eor("**⎆ جاري تشغيل الحساب الإضافي...**")

        try:
            proc = _start_account(name, session)
            _children[name] = proc

            # نعطي العملية وقتاً بسيطاً لبدء Telethon.
            await asyncio.sleep(5)

            if proc.poll() is not None:
                _children.pop(name, None)
                accounts.pop(name, None)
                _save_accounts(accounts)
                return await status.edit(
                    "**⎆ فشل تشغيل الحساب ❌**\n"
                    "راجع Logs لمعرفة سبب فشل تسجيل الدخول."
                )

            await status.edit(
                f"**⎆ تم تنصيب الحساب بنجاح ✅**\n"
                f"**⎆ الحساب:** `{name}`\n"
                "**⎆ يعمل الآن بشكل مستقل.**"
            )

        except Exception as exc:
            _children.pop(name, None)
            accounts.pop(name, None)
            _save_accounts(accounts)
            await status.edit(f"**⎆ فشل التشغيل:** `{exc}`")

    @Tepthon_cmd(pattern=r"حسابات$")
    async def list_accounts(event):
        if not _is_owner(event):
            return

        accounts = _load_accounts()

        if not accounts:
            return await event.eor("**⎆ لا توجد حسابات إضافية.**")

        lines = ["**⎆ الحسابات الإضافية:**"]
        for name in accounts:
            proc = _children.get(name)
            if proc and proc.poll() is None:
                state = "🟢 يعمل"
            else:
                state = "🟡 محفوظ"
            lines.append(f"• `{name}` — {state}")

        await event.eor("\n".join(lines))

    @Tepthon_cmd(pattern=r"حذف حساب(?:\s+(\S+))?$")
    async def remove_account(event):
        if not _is_owner(event):
            return

        name = (event.pattern_match.group(1) or "").strip()
        accounts = _load_accounts()

        if not name or name not in accounts:
            return await event.eor(
                "**⎆ الاستخدام:** `.حذف حساب account1`"
            )

        _stop_account(_children.pop(name, None))
        accounts.pop(name, None)
        _save_accounts(accounts)

        await event.eor(f"**⎆ تم حذف `{name}` وإيقافه ✅**")

    async def _auto_start():
        # بعد تحميل السورس الأساسي، شغل الحسابات المحفوظة.
        await asyncio.sleep(8)

        accounts = _load_accounts()

        for name, data in list(accounts.items()):
            session = data.get("session")

            if not session or name in _children:
                continue

            try:
                proc = _start_account(name, session)
                _children[name] = proc
                await asyncio.sleep(2)
            except Exception:
                pass

    jmubot.loop.create_task(_auto_start())
