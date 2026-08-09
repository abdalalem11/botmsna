# =========================================================
# Tepthon Account Installer
# حقوق المطور: @SSSTlF
# =========================================================

import asyncio
import logging
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)

# نفس طريقة Plugins الرسمية في Tepthon
from .. import Tepthon_cmd
from ..config import Var
from ..core.managers import edit_delete, edit_or_reply


LOGS = logging.getLogger(__name__)

SESSIONS_DIR = Path("database/account_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

_pending = {}
PENDING_TIMEOUT = 600


def _get_api_credentials():
    try:
        return int(Var.API_ID), str(Var.API_HASH).strip()
    except Exception:
        LOGS.exception("Failed to load API credentials")
        return None, None


def _clean_phone(phone):
    return (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def _session_name(phone):
    return phone.replace("+", "").replace("-", "")


def _get_pending(event):
    return _pending.get(event.sender_id)


async def _cleanup_pending(sender_id):
    data = _pending.pop(sender_id, None)

    if not data:
        return

    task = data.get("task")

    if task and task is not asyncio.current_task():
        task.cancel()

    client = data.get("client")

    if client:
        try:
            if client.is_connected():
                await client.disconnect()
        except Exception:
            LOGS.exception("Failed to disconnect client")


async def _expire_pending(sender_id):
    try:
        await asyncio.sleep(PENDING_TIMEOUT)

        if sender_id in _pending:
            await _cleanup_pending(sender_id)

    except asyncio.CancelledError:
        pass

    except Exception:
        LOGS.exception("Pending expiration error")


# =========================================================
# مصنع الحسابات
# =========================================================

@Tepthon_cmd(pattern=r"مصنع(?:\s+|$)([\s\S]*)")
async def account_factory(event):

    api_id, api_hash = _get_api_credentials()

    if not api_id or not api_hash:
        return await edit_or_reply(
            event,
            "❌ API_ID أو API_HASH غير موجود.\n\n"
            "تأكد من إعدادات Tepthon."
        )

    sender_id = event.sender_id

    if sender_id in _pending:
        return await edit_or_reply(
            event,
            "⏳ لديك عملية تنصيب معلقة بالفعل."
        )

    phone = event.pattern_match.group(1).strip()

    if not phone:
        return await edit_or_reply(
            event,
            "🛠 **مصنع الحسابات**\n\n"
            "الاستخدام:\n"
            "`مصنع +9665xxxxxxxx`\n\n"
            "مثال:\n"
            "`مصنع +966512345678`"
        )

    phone = _clean_phone(phone)

    if not phone.startswith("+"):
        return await edit_or_reply(
            event,
            "❌ أرسل الرقم بالصيغة الدولية.\n\n"
            "مثال:\n"
            "`مصنع +966512345678`"
        )

    if not phone[1:].isdigit():
        return await edit_or_reply(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    session_name = _session_name(phone)
    session_path = SESSIONS_DIR / session_name

    client = TelegramClient(
        str(session_path),
        api_id,
        api_hash,
    )

    try:
        await client.connect()

        if await client.is_user_authorized():

            me = await client.get_me()

            username = (
                f"@{me.username}"
                if me.username
                else "بدون معرف"
            )

            await client.disconnect()

            return await edit_or_reply(
                event,
                "✅ **الحساب مثبت مسبقًا**\n\n"
                f"👤 الاسم: `{me.first_name or ''}`\n"
                f"🆔 ID: `{me.id}`\n"
                f"🔗 المعرف: `{username}`\n"
                f"📱 الرقم: `{phone}`"
            )

        sent = await client.send_code_request(phone)

        _pending[sender_id] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "session_name": session_name,
            "task": None,
        }

        _pending[sender_id]["task"] = asyncio.create_task(
            _expire_pending(sender_id)
        )

        return await edit_or_reply(
            event,
            "📲 **تم إرسال كود Telegram.**\n\n"
            "أرسل الكود:\n"
            "`كود 12345`\n\n"
            "⚠️ لا تشارك كود تسجيل الدخول."
        )

    except ApiIdInvalidError:

        await _cleanup_pending(sender_id)

        try:
            await client.disconnect()
        except Exception:
            pass

        return await edit_or_reply(
            event,
            "❌ API_ID أو API_HASH غير صحيح."
        )

    except PhoneNumberInvalidError:

        try:
            await client.disconnect()
        except Exception:
            pass

        return await edit_or_reply(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    except FloodWaitError as e:

        try:
            await client.disconnect()
        except Exception:
            pass

        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار `{e.seconds}` ثانية."
        )

    except Exception as e:

        LOGS.exception("Account factory error")

        try:
            await client.disconnect()
        except Exception:
            pass

        return await edit_delete(
            event,
            f"❌ حدث خطأ:\n`{e}`",
            10,
        )


# =========================================================
# كود Telegram
# =========================================================

@Tepthon_cmd(pattern=r"كود(?:\s+|$)([\s\S]*)")
async def account_code(event):

    code = event.pattern_match.group(1).strip()
    code = code.replace(" ", "").replace("-", "")

    if not code:
        return await edit_or_reply(
            event,
            "❌ أرسل الكود:\n`كود 12345`"
        )

    if not code.isdigit():
        return await edit_or_reply(
            event,
            "❌ الكود يجب أن يكون أرقامًا فقط."
        )

    item = _get_pending(event)

    if not item:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة.\n\n"
            "ابدأ بـ:\n"
            "`مصنع +رقم`"
        )

    client = item["client"]

    try:
        if not client.is_connected():
            await client.connect()

        await client.sign_in(
            phone=item["phone"],
            code=code,
            phone_code_hash=item["phone_code_hash"],
        )

        me = await client.get_me()

        username = (
            f"@{me.username}"
            if me.username
            else "بدون معرف"
        )

        task = item.get("task")

        if task:
            task.cancel()

        _pending.pop(event.sender_id, None)

        await client.disconnect()

        return await edit_or_reply(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ الجلسة محليًا."
        )

    except SessionPasswordNeededError:

        return await edit_or_reply(
            event,
            "🔐 **الحساب محمي بـ 2FA**\n\n"
            "أرسل كلمة المرور:\n"
            "`كلمة_مرور كلمة_المرور`"
        )

    except PhoneCodeInvalidError:

        return await edit_or_reply(
            event,
            "❌ كود Telegram غير صحيح."
        )

    except PhoneCodeExpiredError:

        await _cleanup_pending(event.sender_id)

        return await edit_or_reply(
            event,
            "❌ انتهت صلاحية الكود.\n\n"
            "ابدأ عملية جديدة:\n"
            "`مصنع +رقم`"
        )

    except FloodWaitError as e:

        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار `{e.seconds}` ثانية."
        )

    except Exception as e:

        LOGS.exception("Account code error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ:\n`{e}`",
            10,
        )


# =========================================================
# كلمة مرور 2FA
# =========================================================

@Tepthon_cmd(pattern=r"كلمة_مرور(?:\s+|$)([\s\S]*)")
async def account_password(event):

    password = event.pattern_match.group(1).strip()

    if not password:
        return await edit_or_reply(
            event,
            "❌ أرسل كلمة المرور:\n"
            "`كلمة_مرور ********`"
        )

    item = _get_pending(event)

    if not item:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة."
        )

    client = item["client"]

    try:
        if not client.is_connected():
            await client.connect()

        await client.sign_in(
            password=password
        )

        me = await client.get_me()

        username = (
            f"@{me.username}"
            if me.username
            else "بدون معرف"
        )

        task = item.get("task")

        if task:
            task.cancel()

        _pending.pop(event.sender_id, None)

        await client.disconnect()

        return await edit_or_reply(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ الجلسة محليًا."
        )

    except PasswordHashInvalidError:

        return await edit_or_reply(
            event,
            "❌ كلمة مرور 2FA غير صحيحة."
        )

    except FloodWaitError as e:

        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار `{e.seconds}` ثانية."
        )

    except Exception as e:

        LOGS.exception("Account password error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ:\n`{e}`",
            10,
        )


# =========================================================
# عرض الحسابات
# =========================================================

@Tepthon_cmd(pattern=r"حسابات$")
async def list_accounts(event):

    try:

        sessions = sorted(
            SESSIONS_DIR.glob("*.session")
        )

        if not sessions:
            return await edit_or_reply(
                event,
                "📂 لا توجد حسابات مثبتة حاليًا."
            )

        text = "📋 **الحسابات المثبتة:**\n\n"

        for index, session in enumerate(sessions, 1):
            text += f"{index}. `{session.stem}`\n"

        text += "\n🔐 الجلسات محفوظة محليًا."

        return await edit_or_reply(
            event,
            text
        )

    except Exception as e:

        LOGS.exception("List accounts error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ:\n`{e}`",
            8,
        )


# =========================================================
# إلغاء المصنع
# =========================================================

@Tepthon_cmd(pattern=r"الغاء_المصنع$")
async def cancel_factory(event):

    if not _get_pending(event):
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية معلقة."
        )

    await _cleanup_pending(event.sender_id)

    return await edit_or_reply(
        event,
        "✅ تم إلغاء عملية تنصيب الحساب."
    )


# =========================================================
# حقوق المطور: @SSSTlF
# =========================================================
