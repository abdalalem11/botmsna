# -*- coding: utf-8 -*-
"""
Tepthon Multi Accounts
======================

هذا الملف يعمل بدون تعديل:
    Tepthon/__init__.py
    Tepthon/__main__.py
    core/client.py

الأوامر:

.تنصيب
    يطلب Session String.

.تنصيب <SESSION>
    يثبت الحساب مباشرة.

.حسابات
    يعرض الحسابات الإضافية.

.حذف حساب account1
    يوقف ويحذف الحساب.

مهم:
الحساب الإضافي لا يشغل:
    python -m Tepthon

بل يتم تشغيل Telethon مباشرة، لذلك لا يتم إنشاء Tgbot
مرة ثانية ولا يحدث ImportBotAuthorizationRequest.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.sessions.string import CURRENT_VERSION

from .. import JmdB, jmubot, Tepthon_cmd


# =========================================================
# إعدادات
# =========================================================

CHILD_FLAG = "TEPTHON_MULTI_ACCOUNT_CHILD"

ACCOUNTS_FILE = (
    Path("database")
    / "extra_accounts.json"
)

LOG_DIR = (
    Path("database")
    / "extra_accounts_logs"
)

ACCOUNTS_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

_children = {}


# =========================================================
# لا تسجل الـ handlers داخل العملية الفرعية
# =========================================================

if os.getenv(CHILD_FLAG) != "1":

    # =====================================================
    # قراءة الحسابات
    # =====================================================

    def _load_accounts():

        try:

            if not ACCOUNTS_FILE.exists():
                return {}

            data = json.loads(
                ACCOUNTS_FILE.read_text(
                    encoding="utf-8"
                )
            )

            if isinstance(data, dict):
                return data

        except Exception:
            pass

        return {}


    # =====================================================
    # حفظ الحسابات
    # =====================================================

    def _save_accounts(data):

        ACCOUNTS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temp = (
            ACCOUNTS_FILE.with_suffix(".tmp")
        )

        temp.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temp.replace(
            ACCOUNTS_FILE
        )


    # =====================================================
    # التحقق من المالك
    # =====================================================

    def _is_owner(event):

        try:

            owner = JmdB.get_key(
                "OWNER_ID"
            )

            if owner is None:
                return False

            return int(owner) == int(
                event.sender_id
            )

        except Exception:

            return False


    # =====================================================
    # فحص Session
    # =====================================================

    def _valid_session(session: str):

        session = (
            session or ""
        ).strip()

        if not session:
            return False

        if session.startswith(
            CURRENT_VERSION
        ):

            return len(session) == 353

        return len(session) in {
            351,
            356,
            362,
        }


    # =====================================================
    # ملف Log
    # =====================================================

    def _log_path(name):

        return (
            LOG_DIR
            / f"{name}.log"
        )


    # =====================================================
    # إنشاء كود الحساب الفرعي
    #
    # لا يستورد Tepthon.
    # يستخدم Telethon مباشرة.
    # =====================================================

    def _build_child_script():

        return r'''
import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():

    api_id = int(os.environ["TEPTHON_API_ID"])
    api_hash = os.environ["TEPTHON_API_HASH"]
    session = os.environ["TEPTHON_SESSION"]
    name = os.environ.get(
        "TEPTHON_ACCOUNT_NAME",
        "account"
    )

    print(
        f"[Tepthon Multi Account] "
        f"Starting {name}",
        flush=True
    )

    client = TelegramClient(
        StringSession(session),
        api_id,
        api_hash,
        device_model="Tepthon Multi Account",
        app_version="1.0.0",
    )

    try:

        await client.connect()

        if not await client.is_user_authorized():

            print(
                f"[{name}] Session غير مصرح بها.",
                flush=True
            )

            return 2

        me = await client.get_me()

        if me:

            username = (
                f"@{me.username}"
                if me.username
                else "بدون username"
            )

            print(
                f"[{name}] تم تسجيل الدخول: "
                f"{me.first_name or ''} "
                f"{username}",
                flush=True
            )

        print(
            f"[{name}] الحساب يعمل الآن.",
            flush=True
        )

        await client.run_until_disconnected()

        return 0

    except KeyboardInterrupt:

        return 0

    except Exception as exc:

        print(
            f"[{name}] ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True
        )

        return 1

    finally:

        try:
            await client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":

    try:

        code = asyncio.run(
            main()
        )

        sys.exit(code)

    except KeyboardInterrupt:

        sys.exit(0)
'''


    # =====================================================
    # تشغيل الحساب
    # =====================================================

    def _start_account(
        name,
        session
    ):

        api_id = getattr(
            __import__(
                "Tepthon.config",
                fromlist=["Var"]
            ).Var,
            "API_ID",
            None
        )

        api_hash = getattr(
            __import__(
                "Tepthon.config",
                fromlist=["Var"]
            ).Var,
            "API_HASH",
            None
        )

        # محاولة الحصول على القيم من Var
        if not api_id:
            try:
                from ..config import Var
                api_id = Var.API_ID
            except Exception:
                pass

        if not api_hash:
            try:
                from ..config import Var
                api_hash = Var.API_HASH
            except Exception:
                pass

        if not api_id or not api_hash:

            raise RuntimeError(
                "لم يتم العثور على API_ID / API_HASH "
                "في Tepthon.config.Var"
            )

        env = os.environ.copy()

        env[
            "TEPTHON_API_ID"
        ] = str(api_id)

        env[
            "TEPTHON_API_HASH"
        ] = str(api_hash)

        env[
            "TEPTHON_SESSION"
        ] = session

        env[
            "TEPTHON_ACCOUNT_NAME"
        ] = name

        env[
            CHILD_FLAG
        ] = "1"

        script = _build_child_script()

        log_file = _log_path(name)

        log_handle = open(
            log_file,
            "a",
            encoding="utf-8",
            buffering=1
        )

        log_handle.write(
            "\n\n"
            "====================================\n"
            "STARTING EXTRA ACCOUNT\n"
            f"ACCOUNT={name}\n"
            "====================================\n"
        )

        try:

            proc = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "-c",
                    script,
                ],
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

        _children[name] = (
            proc,
            log_handle
        )

        return proc


    # =====================================================
    # الحصول على العملية
    # =====================================================

    def _get_proc(name):

        value = _children.get(name)

        if not value:
            return None

        return value[0]


    # =====================================================
    # إيقاف الحساب
    # =====================================================

    def _stop_account(name):

        value = _children.pop(
            name,
            None
        )

        if not value:
            return

        proc, log_handle = value

        if proc.poll() is None:

            try:

                os.killpg(
                    proc.pid,
                    signal.SIGTERM
                )

            except Exception:

                try:
                    proc.terminate()
                except Exception:
                    pass

        try:
            log_handle.close()
        except Exception:
            pass


    # =====================================================
    # حالة الحساب
    # =====================================================

    def _child_state(name):

        proc = _get_proc(name)

        if proc is None:
            return "🟡 محفوظ"

        code = proc.poll()

        if code is None:
            return "🟢 يعمل"

        return (
            f"🔴 توقف (exit={code})"
        )


    # =====================================================
    # طلب Session
    # =====================================================

    async def _ask_for_session(event):

        future = (
            event.client.loop.create_future()
        )

        async def receive(
            reply_event
        ):

            if (
                reply_event.sender_id
                != event.sender_id
            ):
                return

            if (
                reply_event.chat_id
                != event.chat_id
            ):
                return

            text = (
                reply_event.raw_text
                or ""
            ).strip()

            if not future.done():

                future.set_result(
                    (
                        text,
                        reply_event
                    )
                )

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
                "سيتم تشغيل الحساب بشكل مستقل.\n\n"
                "⚠️ استخدم Session لحساب تملكه فقط."
            )

            result = await asyncio.wait_for(
                future,
                timeout=120
            )

            text, reply_event = result

            try:
                await reply_event.delete()
            except Exception:
                pass

            return (
                text,
                reply_event
            )

        except asyncio.TimeoutError:

            return (
                None,
                None
            )

        finally:

            event.client.remove_event_handler(
                receive
            )


    # =====================================================
    # تنصيب
    # =====================================================

    @Tepthon_cmd(
        pattern=r"تنصيب(?:\s+([\s\S]+))?$"
    )
    async def install_account(event):

        if not _is_owner(event):
            return

        session = (
            event.pattern_match.group(1)
            or ""
        ).strip()

        if not session:

            session, _ = (
                await _ask_for_session(
                    event
                )
            )

        if not session:

            return await event.eor(
                "**⎆ انتهى وقت انتظار الـ Session.**"
            )

        if not _valid_session(
            session
        ):

            return await event.eor(
                "**⎆ الـ Session غير صحيحة ❌**"
            )

        accounts = _load_accounts()

        for item in accounts.values():

            if (
                isinstance(item, dict)
                and item.get("session")
                == session
            ):

                return await event.eor(
                    "**⎆ هذا الحساب مثبت مسبقاً.**"
                )

        index = 1

        while (
            f"account{index}"
            in accounts
        ):

            index += 1

        name = (
            f"account{index}"
        )

        accounts[name] = {
            "session": session
        }

        _save_accounts(
            accounts
        )

        status = await event.eor(
            "**⎆ جاري تشغيل الحساب الإضافي...**"
        )

        try:

            proc = _start_account(
                name,
                session
            )

            await asyncio.sleep(5)

            code = proc.poll()

            if code is not None:

                _stop_account(
                    name
                )

                accounts.pop(
                    name,
                    None
                )

                _save_accounts(
                    accounts
                )

                return await status.edit(
                    "**⎆ الحساب لم يستمر في التشغيل ❌**\n"
                    f"**⎆ الحساب:** `{name}`\n"
                    f"**⎆ Exit code:** `{code}`\n\n"
                    f"**⎆ السجل:** `{_log_path(name)}`"
                )

            await status.edit(
                "**⎆ تم تنصيب الحساب بنجاح ✅**\n"
                f"**⎆ الحساب:** `{name}`\n"
                "**⎆ يعمل الآن بشكل مستقل.**"
            )

        except Exception as exc:

            _stop_account(
                name
            )

            accounts.pop(
                name,
                None
            )

            _save_accounts(
                accounts
            )

            return await status.edit(
                "**⎆ فشل تشغيل الحساب ❌**\n"
                f"`{type(exc).__name__}: {exc}`"
            )


    # =====================================================
    # الحسابات
    # =====================================================

    @Tepthon_cmd(
        pattern=r"حسابات$"
    )
    async def list_accounts(event):

        if not _is_owner(event):
            return

        accounts = _load_accounts()

        if not accounts:

            return await event.eor(
                "**⎆ لا توجد حسابات إضافية.**"
            )

        lines = [
            "**⎆ الحسابات الإضافية:**"
        ]

        for name in accounts:

            lines.append(
                f"• `{name}` — "
                f"{_child_state(name)}"
            )

        await event.eor(
            "\n".join(lines)
        )


    # =====================================================
    # حذف حساب
    # =====================================================

    @Tepthon_cmd(
        pattern=r"حذف حساب(?:\s+(\S+))?$"
    )
    async def remove_account(event):

        if not _is_owner(event):
            return

        name = (
            event.pattern_match.group(1)
            or ""
        ).strip()

        accounts = _load_accounts()

        if (
            not name
            or name not in accounts
        ):

            return await event.eor(
                "**⎆ الاستخدام:** "
                "`.حذف حساب account1`"
            )

        _stop_account(
            name
        )

        accounts.pop(
            name,
            None
        )

        _save_accounts(
            accounts
        )

        await event.eor(
            f"**⎆ تم حذف `{name}` وإيقافه ✅**"
        )


    # =====================================================
    # التشغيل التلقائي
    # =====================================================

    async def _auto_start():

        await asyncio.sleep(8)

        accounts = _load_accounts()

        for name, data in list(
            accounts.items()
        ):

            if not isinstance(
                data,
                dict
            ):
                continue

            session = data.get(
                "session"
            )

            if (
                not session
                or name in _children
            ):
                continue

            if not _valid_session(
                session
            ):
                continue

            try:

                proc = _start_account(
                    name,
                    session
                )

                await asyncio.sleep(2)

                if proc.poll() is not None:

                    _stop_account(
                        name
                    )

            except Exception:

                continue


    # =====================================================
    # تشغيل Auto Start
    # =====================================================

    jmubot.loop.create_task(
        _auto_start()
    )
