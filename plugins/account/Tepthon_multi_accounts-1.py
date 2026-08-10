# -*- coding: utf-8 -*-
"""
Tepthon Multi Accounts - Debug Version

المسار:
plugins/account/Tepthon_multi_accounts-1.py

الأوامر:
.تنصيب
.تنصيب SESSION
.حسابات
.حذف حساب account1

الحساب الإضافي يعمل عبر Telethon مباشرة،
ولا يشغل python -m Tepthon.
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

from .. import JmdB, jmubot, Tepthon_cmd, LOGS


# =========================================================
# رسالة تحميل الملف
# =========================================================

CHILD_FLAG = "TEPTHON_MULTI_ACCOUNT_CHILD"

if os.getenv(CHILD_FLAG) != "1":
    try:
        LOGS.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        LOGS.info("✅ تم تحميل Tepthon_multi_accounts-1.py")
        LOGS.info("✅ نظام الحسابات الإضافية جاهز")
        LOGS.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    except Exception:
        pass


# =========================================================
# الملفات
# =========================================================

ACCOUNTS_FILE = Path("database") / "extra_accounts.json"
LOG_DIR = Path("database") / "extra_accounts_logs"

ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

_children = {}


# =========================================================
# فقط العملية الرئيسية تسجل الأوامر
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

            return data if isinstance(data, dict) else {}

        except Exception as exc:
            LOGS.error(
                f"❌ خطأ قراءة الحسابات: {exc}"
            )
            return {}


    # =====================================================
    # حفظ الحسابات
    # =====================================================

    def _save_accounts(data):
        ACCOUNTS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temp = ACCOUNTS_FILE.with_suffix(".tmp")

        temp.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temp.replace(ACCOUNTS_FILE)


    # =====================================================
    # التحقق من المالك
    # =====================================================

    def _is_owner(event):
        try:
            owner = JmdB.get_key("OWNER_ID")

            if owner is None:
                return False

            return int(owner) == int(event.sender_id)

        except Exception:
            return False


    # =====================================================
    # التحقق من Session
    # =====================================================

    def _valid_session(session):
        session = (session or "").strip()

        if not session:
            return False

        if session.startswith(CURRENT_VERSION):
            return len(session) == 353

        return len(session) in {
            351,
            356,
            362
        }


    # =====================================================
    # Log
    # =====================================================

    def _log_path(name):
        return LOG_DIR / f"{name}.log"


    # =====================================================
    # API
    # =====================================================

    def _get_api_config():

        try:
            from ..config import Var

            api_id = getattr(
                Var,
                "API_ID",
                None
            )

            api_hash = getattr(
                Var,
                "API_HASH",
                None
            )

            if api_id and api_hash:
                return api_id, api_hash

        except Exception as exc:
            LOGS.error(
                f"❌ فشل قراءة API من config: {exc}"
            )

        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")

        if api_id and api_hash:
            return api_id, api_hash

        raise RuntimeError(
            "لم يتم العثور على API_ID أو API_HASH"
        )


    # =====================================================
    # برنامج الحساب الفرعي
    # =====================================================

    def _build_child_script():

        return r'''
import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():

    name = os.environ.get(
        "TEPTHON_ACCOUNT_NAME",
        "account"
    )

    api_id = os.environ.get(
        "TEPTHON_API_ID"
    )

    api_hash = os.environ.get(
        "TEPTHON_API_HASH"
    )

    session = os.environ.get(
        "TEPTHON_SESSION"
    )

    print("", flush=True)

    print(
        "==========================================",
        flush=True
    )

    print(
        f"🚀 [{name}] بدء تشغيل الحساب الإضافي",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    if not api_id:
        print(
            f"❌ [{name}] API_ID غير موجود",
            flush=True
        )
        return 10

    if not api_hash:
        print(
            f"❌ [{name}] API_HASH غير موجود",
            flush=True
        )
        return 11

    if not session:
        print(
            f"❌ [{name}] Session غير موجودة",
            flush=True
        )
        return 12

    try:
        api_id = int(api_id)
    except Exception:
        print(
            f"❌ [{name}] API_ID غير صالح",
            flush=True
        )
        return 13

    print(
        f"[{name}] إنشاء Telethon Client...",
        flush=True
    )

    client = TelegramClient(
        StringSession(session),
        api_id,
        api_hash,
        device_model="Tepthon Multi Account",
        app_version="1.0.0"
    )

    try:

        print(
            f"[{name}] جاري الاتصال بتليجرام...",
            flush=True
        )

        await client.connect()

        print(
            f"✅ [{name}] تم الاتصال بتليجرام",
            flush=True
        )

        authorized = (
            await client.is_user_authorized()
        )

        if not authorized:

            print(
                f"❌ [{name}] Session غير مصرح بها",
                flush=True
            )

            return 20

        print(
            f"[{name}] جاري التحقق من الحساب...",
            flush=True
        )

        me = await client.get_me()

        if not me:

            print(
                f"❌ [{name}] لم يتم العثور على الحساب",
                flush=True
            )

            return 21

        username = (
            f"@{me.username}"
            if me.username
            else "بدون username"
        )

        first_name = me.first_name or ""

        print("", flush=True)

        print(
            "==========================================",
            flush=True
        )

        print(
            f"✅ [{name}] تم تسجيل الدخول بنجاح",
            flush=True
        )

        print(
            f"الاسم: {first_name}",
            flush=True
        )

        print(
            f"المعرف: {username}",
            flush=True
        )

        print(
            f"ID: {me.id}",
            flush=True
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            f"🟢 [{name}] الحساب يعمل الآن",
            flush=True
        )

        await client.run_until_disconnected()

        print(
            f"⚠️ [{name}] تم قطع الاتصال",
            flush=True
        )

        return 0

    except Exception as exc:

        print("", flush=True)

        print(
            "==========================================",
            flush=True
        )

        print(
            f"❌ [{name}] حدث خطأ",
            flush=True
        )

        print(
            f"نوع الخطأ: {type(exc).__name__}",
            flush=True
        )

        print(
            f"الخطأ: {exc}",
            flush=True
        )

        print(
            "==========================================",
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

        code = asyncio.run(main())

        sys.exit(code)

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as exc:

        print(
            f"FATAL ERROR: {type(exc).__name__}: {exc}",
            flush=True
        )

        sys.exit(99)
'''


    # =====================================================
    # تشغيل الحساب
    # =====================================================

    def _start_account(name, session):

        api_id, api_hash = _get_api_config()

        env = os.environ.copy()

        env["TEPTHON_API_ID"] = str(api_id)
        env["TEPTHON_API_HASH"] = str(api_hash)
        env["TEPTHON_SESSION"] = session
        env["TEPTHON_ACCOUNT_NAME"] = name
        env[CHILD_FLAG] = "1"

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
            "==========================================\n"
            f"START ACCOUNT: {name}\n"
            "==========================================\n"
        )

        try:

            proc = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "-c",
                    script
                ],
                cwd=os.getcwd(),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

        except Exception:

            log_handle.close()
            raise

        _children[name] = (
            proc,
            log_handle
        )

        LOGS.info(
            f"🚀 تم بدء العملية للحساب {name}"
        )

        return proc


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

        value = _children.get(name)

        if not value:
            return "🟡 محفوظ"

        proc = value[0]

        code = proc.poll()

        if code is None:
            return "🟢 العملية تعمل"

        return f"🔴 متوقف (exit={code})"


    # =====================================================
    # طلب Session
    # =====================================================

    async def _ask_for_session(event):

        future = event.client.loop.create_future()

        async def receive(reply_event):

            if reply_event.sender_id != event.sender_id:
                return

            if reply_event.chat_id != event.chat_id:
                return

            text = (
                reply_event.raw_text or ""
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
                from_users=event.sender_id
            )
        )

        try:

            await event.eor(
                "**⎆ أرسل Session String للحساب الجديد الآن.**\n\n"
                "بعد الإرسال سيتم تشغيل الحساب مباشرة.\n\n"
                "⚠️ استخدم Session لحساب تملكه فقط."
            )

            text, reply_event = await asyncio.wait_for(
                future,
                timeout=120
            )

            try:
                await reply_event.delete()
            except Exception:
                pass

            return text

        except asyncio.TimeoutError:

            return None

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
            session = await _ask_for_session(event)

        if not session:

            return await event.eor(
                "**⎆ انتهى وقت انتظار الـSession.**"
            )

        if not _valid_session(session):

            return await event.eor(
                "**⎆ الـSession غير صحيحة ❌**\n\n"
                "تأكد أنها String Session صالحة."
            )

        accounts = _load_accounts()

        for item in accounts.values():

            if (
                isinstance(item, dict)
                and item.get("session") == session
            ):

                return await event.eor(
                    "**⎆ هذا الحساب مثبت مسبقاً.**"
                )

        index = 1

        while f"account{index}" in accounts:
            index += 1

        name = f"account{index}"

        accounts[name] = {
            "session": session
        }

        _save_accounts(accounts)

        status = await event.eor(
            f"**⎆ جاري تشغيل `{name}` 🚀**\n\n"
            "⏳ جاري الاتصال والتحقق..."
        )

        try:

            proc = _start_account(
                name,
                session
            )

            await status.edit(
                f"**⎆ تم تشغيل `{name}` 🚀**\n\n"
                "⏳ جاري التحقق من تسجيل الدخول..."
            )

            for _ in range(12):

                await asyncio.sleep(1)

                if proc.poll() is not None:
                    break

            code = proc.poll()

            if code is not None:

                return await status.edit(
                    f"**⎆ `{name}` توقف ❌**\n\n"
                    f"Exit code: `{code}`\n\n"
                    f"📄 Log:\n"
                    f"`{_log_path(name)}`"
                )

            await status.edit(
                f"**⎆ `{name}` يعمل الآن 🟢**\n\n"
                "تم تشغيل الحساب الإضافي بشكل مستقل.\n\n"
                f"📄 Log:\n`{_log_path(name)}`"
            )

        except Exception as exc:

            _stop_account(name)

            accounts.pop(
                name,
                None
            )

            _save_accounts(accounts)

            return await status.edit(
                "**⎆ فشل تشغيل الحساب ❌**\n\n"
                f"نوع الخطأ: `{type(exc).__name__}`\n"
                f"الخطأ: `{exc}`"
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
            "**⎆ الحسابات الإضافية:**",
            ""
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
                "**⎆ الاستخدام:**\n"
                "`.حذف حساب account1`"
            )

        _stop_account(name)

        accounts.pop(
            name,
            None
        )

        _save_accounts(accounts)

        await event.eor(
            f"**⎆ تم حذف `{name}` وإيقافه ✅**"
        )


    # =====================================================
    # التشغيل التلقائي
    # =====================================================

    async def _auto_start():

        await asyncio.sleep(10)

        LOGS.info(
            "🔄 بدء فحص الحسابات الإضافية..."
        )

        accounts = _load_accounts()

        for name, data in list(
            accounts.items()
        ):

            if not isinstance(data, dict):
                continue

            session = data.get("session")

            if (
                not session
                or name in _children
            ):
                continue

            if not _valid_session(session):

                LOGS.error(
                    f"❌ Session غير صالحة للحساب {name}"
                )

                continue

            try:

                LOGS.info(
                    f"🚀 تشغيل الحساب المحفوظ: {name}"
                )

                proc = _start_account(
                    name,
                    session
                )

                await asyncio.sleep(3)

                if proc.poll() is not None:

                    LOGS.error(
                        f"❌ الحساب {name} توقف مباشرة. "
                        f"راجع {_log_path(name)}"
                    )

                else:

                    LOGS.info(
                        f"🟢 الحساب {name}
