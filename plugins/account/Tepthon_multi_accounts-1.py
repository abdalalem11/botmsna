# -*- coding: utf-8 -*-

"""
Tepthon Multi Accounts
تشغيل الحسابات الإضافية كـ Tepthon Userbot مستقل.

الأوامر:
.تنصيب
.تنصيب SESSION
.حسابات
.حذف حساب account1
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

from .. import JmdB, Tepthon_cmd, LOGS


CHILD_FLAG = "TEPTHON_MULTI_ACCOUNT_CHILD"

ACCOUNTS_FILE = Path("database") / "extra_accounts.json"
LOG_DIR = Path("database") / "extra_accounts_logs"

ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

_children = {}


if os.getenv(CHILD_FLAG) != "1":

    LOGS.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGS.info("✅ تم تحميل نظام الحسابات الإضافية")
    LOGS.info("✅ Multi Accounts جاهز")
    LOGS.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


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

        temp.replace(
            ACCOUNTS_FILE
        )


    # =====================================================
    # المالك
    # =====================================================

    def _is_owner(event):

        try:

            owner = JmdB.get_key(
                "OWNER_ID"
            )

            if owner is None:
                return False

            return (
                int(owner)
                == int(event.sender_id)
            )

        except Exception:

            return False


    # =====================================================
    # التحقق من Session
    # =====================================================

    def _valid_session(session):

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
            362
        }


    # =====================================================
    # Log
    # =====================================================

    def _log_path(name):

        return (
            LOG_DIR
            / f"{name}.log"
        )


    # =====================================================
    # API
    # =====================================================

    def _get_api():

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

                return (
                    int(api_id),
                    str(api_hash)
                )

        except Exception as exc:

            LOGS.error(
                f"❌ خطأ API config: {exc}"
            )

        api_id = os.getenv(
            "API_ID"
        )

        api_hash = os.getenv(
            "API_HASH"
        )

        if api_id and api_hash:

            return (
                int(api_id),
                str(api_hash)
            )

        raise RuntimeError(
            "API_ID/API_HASH غير موجودين"
        )


    # =====================================================
    # كود الحساب الفرعي
    # =====================================================

    def _child_script():

        return r'''
import asyncio
import importlib
import os
import sys
import traceback

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

    print(
        "==========================================",
        flush=True
    )

    print(
        f"🚀 [{name}] تشغيل Tepthon",
        flush=True
    )

    print(
        "==========================================",
        flush=True
    )

    if not api_id:
        print(
            "❌ API_ID غير موجود",
            flush=True
        )
        return 10

    if not api_hash:
        print(
            "❌ API_HASH غير موجود",
            flush=True
        )
        return 11

    if not session:
        print(
            "❌ Session غير موجودة",
            flush=True
        )
        return 12

    try:

        api_id = int(api_id)

    except Exception:

        print(
            "❌ API_ID غير صالح",
            flush=True
        )

        return 13


    # =================================================
    # استيراد TepthonClient بدون تشغيل __main__
    # =================================================

    try:

        from Tepthon.core.client import TepthonClient
        from Tepthon.core.session import both_session
        from Tepthon.core.logger import LOGS

    except Exception as exc:

        print(
            f"❌ فشل استيراد TepthonClient: {exc}",
            flush=True
        )

        traceback.print_exc()

        return 30


    # =================================================
    # إنشاء Client للحساب الإضافي
    # =================================================

    try:

        session_obj = both_session(
            session,
            LOGS,
            _exit=False
        )

        if session_obj is None:

            session_obj = StringSession(
                session
            )

        print(
            f"🔌 [{name}] إنشاء TepthonClient...",
            flush=True
        )

        client = TepthonClient(
            session=session_obj,
            api_id=api_id,
            api_hash=api_hash,
            log_attempt=True,
            exit_on_error=False,
            device_model="Tepthon Multi Account",
            app_version="1.0.0",
        )

        print(
            f"✅ [{name}] تم إنشاء TepthonClient",
            flush=True
        )

    except Exception as exc:

        print(
            f"❌ [{name}] فشل إنشاء العميل: {exc}",
            flush=True
        )

        traceback.print_exc()

        return 31


    # =================================================
    # استبدال jmubot للحساب الفرعي
    # =================================================

    try:

        tep_module = importlib.import_module(
            "Tepthon"
        )

        tep_module.jmubot = client
        tep_module.jmthon_bot = client

        print(
            f"✅ [{name}] تم ربط jmubot بالحساب الإضافي",
            flush=True
        )

    except Exception as exc:

        print(
            f"⚠️ [{name}] تعذر ربط jmubot: {exc}",
            flush=True
        )


    # =================================================
    # تحميل Plugins
    # =================================================

    try:

        from Tepthon.load_plug import load

        print(
            f"📦 [{name}] جاري تحميل Plugins...",
            flush=True
        )

        load(
            log=True,
            key=f"الحساب الإضافي {name}",
            path="plugins"
        )

        print(
            f"✅ [{name}] تم تحميل Plugins",
            flush=True
        )

    except Exception as exc:

        print(
            f"❌ [{name}] فشل تحميل Plugins: {exc}",
            flush=True
        )

        traceback.print_exc()

        return 40


    # =================================================
    # بيانات الحساب
    # =================================================

    try:

        me = await client.get_me()

        if not me:

            print(
                f"❌ [{name}] لم يتم العثور على الحساب",
                flush=True
            )

            return 41

        username = (
            f"@{me.username}"
            if me.username
            else "بدون username"
        )

        print(
            "==========================================",
            flush=True
        )

        print(
            f"✅ [{name}] الحساب يعمل",
            flush=True
        )

        print(
            f"الاسم: {me.first_name or ''}",
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


    except Exception as exc:

        print(
            f"❌ [{name}] فشل جلب بيانات الحساب: {exc}",
            flush=True
        )

        return 42


    # =================================================
    # تشغيل الحساب
    # =================================================

    print(
        f"🟢 [{name}] Tepthon يعمل الآن...",
        flush=True
    )

    try:

        await client.run_until_disconnected()

    except KeyboardInterrupt:

        pass

    except Exception as exc:

        print(
            f"❌ [{name}] توقف بسبب: {exc}",
            flush=True
        )

        traceback.print_exc()

        return 50

    finally:

        try:
            await client.disconnect()
        except Exception:
            pass

    return 0


if __name__ == "__main__":

    try:

        result = asyncio.run(
            main()
        )

        sys.exit(
            result
        )

    except KeyboardInterrupt:

        sys.exit(0)

    except Exception as exc:

        print(
            f"FATAL: {type(exc).__name__}: {exc}",
            flush=True
        )

        traceback.print_exc()

        sys.exit(99)
'''


    # =====================================================
    # تشغيل حساب
    # =====================================================

    def _start_account(
        name,
        session
    ):

        api_id, api_hash = _get_api()

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

        log_file = _log_path(
            name
        )

        log_handle = open(
            log_file,
            "a",
            encoding="utf-8",
            buffering=1
        )

        log_handle.write(
            "\n\n"
            "==========================================\n"
            f"START: {name}\n"
            "==========================================\n"
        )

        proc = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-c",
                _child_script()
            ],
            cwd=os.getcwd(),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        _children[name] = (
            proc,
            log_handle
        )

        LOGS.info(
            f"🚀 تم تشغيل {name}"
        )

        return proc


    # =====================================================
    # إيقاف
    # =====================================================

    def _stop_account(name):

        item = _children.pop(
            name,
            None
        )

        if not item:
            return

        proc, handle = item

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
            handle.close()
        except Exception:
            pass


    # =====================================================
    # حالة
    # =====================================================

    def _state(name):

        item = _children.get(
            name
        )

        if not item:
            return "🟡 محفوظ"

        code = item[0].poll()

        if code is None:
            return "🟢 العملية تعمل"

        return (
            f"🔴 متوقف ({code})"
        )


    # =====================================================
    # طلب Session
    # =====================================================

    async def _ask_session(event):

        future = (
            event.client.loop.create_future()
        )

        async def receiver(
            reply
        ):

            if (
                reply.sender_id
                != event.sender_id
            ):
                return

            if (
                reply.chat_id
                != event.chat_id
            ):
                return

            text = (
                reply.raw_text or ""
            ).strip()

            if not future.done():

                future.set_result(
                    (
                        text,
                        reply
                    )
                )

        event.client.add_event_handler(
            receiver,
            events.NewMessage(
                chats=event.chat_id,
                from_users=event.sender_id
            )
        )

        try:

            await event.eor(
                "**⎆ أرسل Session String الآن.**\n\n"
                "⚠️ استخدم Session لحساب تملكه فقط."
            )

            text, reply = await asyncio.wait_for(
                future,
                timeout=120
            )

            try:
                await reply.delete()
            except Exception:
                pass

            return text

        except asyncio.TimeoutError:

            return None

        finally:

            event.client.remove_event_handler(
                receiver
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

            session = await _ask_session(
                event
            )

        if not session:

            return await event.eor(
                "**⎆ انتهى وقت الانتظار ❌**"
            )

        if not _valid_session(
            session
        ):

            return await event.eor(
                "**⎆ الـSession غير صحيحة ❌**"
            )

        accounts = _load_accounts()

        for data in accounts.values():

            if (
                isinstance(data, dict)
                and data.get("session")
                == session
            ):

                return await event.eor(
                    "**⎆ الحساب مثبت مسبقاً.**"
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

        msg = await event.eor(
            f"**⎆ جاري تشغيل `{name}` 🚀**"
        )

        try:

            proc = _start_account(
                name,
                session
            )

            for _ in range(20):

                await asyncio.sleep(
                    1
                )

                if proc.poll() is not None:
                    break

            code = proc.poll()

            if code is not None:

                return await msg.edit(
                    f"**⎆ `{name}` توقف ❌**\n\n"
                    f"Exit: `{code}`\n\n"
                    f"📄 `{_log_path(name)}`"
                )

            return await msg.edit(
                f"**⎆ `{name}` يعمل الآن 🟢**\n\n"
                "تم تشغيل Tepthon للحساب الإضافي.\n\n"
                f"📄 `{_log_path(name)}`"
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

            return await msg.edit(
                f"**⎆ فشل التشغيل ❌**\n\n"
                f"`{type(exc).__name__}`\n"
                f"`{exc}`"
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
                f"{_state(name)}"
            )

        await event.eor(
            "\n".join(lines)
        )


    # =====================================================
    # حذف
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
    # تشغيل تلقائي
    # =====================================================

    async def _auto_start():

        await asyncio.sleep(
            10
        )

        LOGS.info(
            "🔄 بدء فحص الحسابات الإضافية..."
        )

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

            if not session:
                continue

            if name in _children:
                continue

            if not _valid_session(
                session
            ):

                LOGS.error(
                    f"❌ Session غير صالحة: {name}"
                )

                continue

            try:

                proc = _start_account(
                    name,
                    session
                )

                await asyncio.sleep(
                    5
                )

                if proc.poll() is None:

                    LOGS.info(
                        f"🟢 الحساب {name} يعمل"
                    )

                else:

                    LOGS.error(
                        f"❌ الحساب {name} توقف "
                        f"exit={proc.poll()}"
                    )

            except Exception as exc:

                LOGS.error(
                    f"❌ {name}: {exc}"
                )

        LOGS.info(
            "✅ انتهى فحص الحسابات الإضافية"
        )


    # =====================================================
    # مراقبة
    # =====================================================

    async def _monitor():

        while True:

            await asyncio.sleep(
                30
            )

            for name, value in list(
                _children.items()
            ):

                proc, handle = value

                code = proc.poll()

                if code is None:
                    continue

                LOGS.warning(
                    f"⚠️ الحساب {name} توقف "
                    f"(exit={code})"
                )

                try:
                    handle.close()
                except Exception:
                    pass

                _children.pop(
                    name,
                    None
                )


    # =====================================================
    # البداية
    # =====================================================

    try:

        loop = asyncio.get_event_loop()

        loop.create_task(
            _auto_start()
        )

        loop.create_task(
            _monitor()
        )

        LOGS.info(
            "✅ تم تشغيل نظام الحسابات الإضافية"
        )

    except Exception as exc:

        LOGS.error(
            f"❌ فشل تشغيل Multi Accounts: {exc}"
        )
