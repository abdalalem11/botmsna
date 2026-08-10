# -*- coding: utf-8 -*-
"""
Tepthon Multi-Account Installer

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
- الحسابات الإضافية تعمل في عمليات مستقلة.
- التخزين محلي في database/extra_accounts.json.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

from telethon import events
from telethon.sessions.string import CURRENT_VERSION

from .. import JmdB, jmubot, Tepthon_cmd


CHILD_FLAG = "TEPTHON_EXTRA_ACCOUNT"

if os.getenv(CHILD_FLAG) != "1":
    ACCOUNTS_FILE = Path("database") / "extra_accounts.json"
    LOG_DIR = Path("database") / "extra_accounts_logs"

    ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

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

    def _valid_session(session: str) -> bool:
        """
        نفس القواعد الموجودة في core/session.py:
        StringSession تبدأ بـ CURRENT_VERSION وطولها 353،
        أو صيغة Pyrogram المدعومة.
        """
        session = (session or "").strip()

        if session.startswith(CURRENT_VERSION):
            return len(session) == 353

        # الصيغ المدعومة في core/session.py
        return len(session) in {351, 356, 362}

    def _log_path(name):
        return LOG_DIR / f"{name}.log"

    def _start_account(name, session):
        env = os.environ.copy()
        env["SESSION"] = session
        env[CHILD_FLAG] = "1"
        env["TEPTHON_ACCOUNT_NAME"] = name

        log_file = _log_path(name)
        log_handle = open(log_file, "a", encoding="utf-8", buffering=1)

        log_handle.write(
            "\n\n========== STARTING ACCOUNT ==========\n"
            f"ACCOUNT={name}\n"
        )

        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "Tepthon"],
                cwd=os.getcwd(),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except Exception:
            log_handle.close()
            raise

        # نخزن المقبض مع العملية حتى لا يغلق قبل انتهاء العملية.
        _children[name] = (proc, log_handle)
        return proc

    def _get_proc(name):
        value = _children.get(name)
        if not value:
            return None
        return value[0]

    def _stop_account(name):
        value = _children.pop(name, None)
        if not value:
            return

        proc, log_handle = value

        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass

        try:
            log_handle.close()
        except Exception:
            pass

    def _child_state(name):
        proc = _get_proc(name)

        if proc is None:
            return "🟡 محفوظ"

        code = proc.poll()

        if code is None:
            return "🟢 يعمل"

        return f"🔴 توقف (exit={code})"

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
                "سيتم استخدامها لتشغيل الحساب.\n"
                "⚠️ استخدم Session لحساب تملكه فقط."
            )

            text, reply_event = await asyncio.wait_for(
                future,
                timeout=120,
            )

            # محاولة حذف رسالة الـ Session من المحادثة.
            try:
                await reply_event.delete()
            except Exception:
                pass

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

        if not session:
            session, _ = await _ask_for_session(event)

        if not session:
            return await event.eor(
                "**⎆ انتهى وقت انتظار الـ Session.**"
            )

        if not _valid_session(session):
            return await event.eor(
                "**⎆ الـ Session غير صحيحة ❌**\n\n"
                "تأكد أنها Session String صالحة من نفس الصيغة التي يدعمها السورس."
            )

        accounts = _load_accounts()

        if any(
            item.get("session") == session
            for item in accounts.values()
            if isinstance(item, dict)
        ):
            return await event.eor(
                "**⎆ هذا الحساب مثبت مسبقاً.**"
            )

        index = 1
        while f"account{index}" in accounts:
            index += 1

        name = f"account{index}"

        accounts[name] = {
            "session": session,
        }
        _save_accounts(accounts)

        status = await event.eor(
            "**⎆ جاري تشغيل الحساب الإضافي...**"
        )

        try:
            proc = _start_account(name, session)

            # نعطي العملية وقتاً كافياً لتظهر أخطاء البداية في ملفها.
            await asyncio.sleep(8)

            code = proc.poll()

            if code is not None:
                log_file = _log_path(name)

                return await status.edit(
                    "**⎆ الحساب لم يستمر في التشغيل ❌**\n"
                    f"**⎆ الحساب:** `{name}`\n"
                    f"**⎆ Exit code:** `{code}`\n\n"
                    f"**⎆ سجل الحساب:** `{log_file}`\n"
                    "أرسل محتوى سجل الحساب لي إذا أردت تحديد الخطأ."
                )

            await status.edit(
                "**⎆ تم تنصيب الحساب بنجاح ✅**\n"
                f"**⎆ الحساب:** `{name}`\n"
                "**⎆ يعمل الآن بشكل مستقل.**"
            )

        except Exception as exc:
            accounts.pop(name, None)
            _save_accounts(accounts)
            _stop_account(name)

            return await status.edit(
                "**⎆ فشل التشغيل ❌**\n"
                f"`{type(exc).__name__}: {exc}`"
            )

    @Tepthon_cmd(pattern=r"حسابات$")
    async def list_accounts(event):
        if not _is_owner(event):
            return

        accounts = _load_accounts()

        if not accounts:
            return await event.eor(
                "**⎆ لا توجد حسابات إضافية.**"
            )

        lines = ["**⎆ الحسابات الإضافية:**"]

        for name in accounts:
            lines.append(
                f"• `{name}` — {_child_state(name)}"
            )

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

        _stop_account(name)

        accounts.pop(name, None)
        _save_accounts(accounts)

        await event.eor(
            f"**⎆ تم حذف `{name}` وإيقافه ✅**"
        )

    async def _auto_start():
        # الحسابات الإضافية لا تدير حسابات أخرى.
        await asyncio.sleep(8)

        accounts = _load_accounts()

        for name, data in list(accounts.items()):
            if not isinstance(data, dict):
                continue

            session = data.get("session")

            if not session or name in _children:
                continue

            if not _valid_session(session):
                continue

            try:
                _start_account(name, session)
                await asyncio.sleep(2)
            except Exception:
                continue

    jmubot.loop.create_task(_auto_start())
