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
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from .. import Tepthon_cmd
from ..core.managers import edit_delete, edit_or_reply

LOGS = logging.getLogger(__name__)

# مجلد حفظ جلسات الحسابات.
# لا يتم إرسال الجلسات أو كلمات المرور إلى أي مكان.
SESSIONS_DIR = Path("database/account_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

_pending = {}


def _get_api_credentials():
    """يقرأ API_ID و API_HASH من إعدادات Tepthon."""
    try:
        from .. import API_ID, API_HASH
        return int(API_ID), str(API_HASH)
    except Exception:
        pass

    try:
        from ..core.config import API_ID, API_HASH
        return int(API_ID), str(API_HASH)
    except Exception:
        pass

    return None, None


@Tepthon_cmd(pattern=r"مصنع(?:\s+|$)([\s\S]*)")
async def account_factory(event):
    """مصنع تنصيب حساب Telegram إضافي."""

    api_id, api_hash = _get_api_credentials()

    if not api_id or not api_hash:
        return await edit_or_reply(
            event,
            "❌ لم يتم العثور على API_ID و API_HASH في إعدادات السورس."
        )

    arg = event.pattern_match.group(1).strip()

    if not arg:
        return await edit_or_reply(
            event,
            "🛠 **مصنع الحسابات**\n\n"
            "أرسل الأمر هكذا:\n"
            "`مصنع +966xxxxxxxxx`\n\n"
            "بعدها سيرسل Telegram كود تسجيل الدخول."
        )

    phone = arg.replace(" ", "")

    if not phone.startswith("+"):
        return await edit_or_reply(
            event,
            "❌ أرسل الرقم بالصيغة الدولية.\nمثال:\n`مصنع +9665xxxxxxxx`"
        )

    if not phone[1:].isdigit():
        return await edit_or_reply(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    session_name = phone.replace("+", "").replace("-", "")
    session_path = SESSIONS_DIR / session_name

    if session_name in _pending:
        return await edit_or_reply(
            event,
            "⏳ توجد عملية تنصيب معلقة لهذا الرقم بالفعل."
        )

    client = TelegramClient(
        str(session_path),
        api_id,
        api_hash,
    )

    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.disconnect()
            return await edit_or_reply(
                event,
                f"✅ الحساب `{phone}` مثبت مسبقًا."
            )

        sent = await client.send_code_request(phone)

        _pending[session_name] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "event": event,
        }

        await edit_or_reply(
            event,
            "📲 **تم إرسال كود Telegram.**\n\n"
            "أرسل الكود في رسالة خاصة بهذا الشكل:\n"
            "`كود 12345`\n\n"
            "⚠️ لا ترسل كود الدخول لأي شخص آخر."
        )

    except ApiIdInvalidError:
        await client.disconnect()
        return await edit_or_reply(
            event,
            "❌ API_ID أو API_HASH غير صحيح."
        )
    except Exception as e:
        LOGS.exception("Account installer error")
        await client.disconnect()
        return await edit_delete(event, f"❌ خطأ:\n`{e}`", 8)


@Tepthon_cmd(pattern=r"كود(?:\s+|$)([\s\S]*)")
async def account_code(event):
    """إدخال كود تسجيل الدخول للحساب الجاري تنصيبه."""

    code = event.pattern_match.group(1).strip()

    if not code:
        return await edit_or_reply(
            event,
            "❌ أرسل الكود هكذا:\n`كود 12345`"
        )

    # نحاول العثور على العملية المعلقة الخاصة بالمرسل.
    item = None
    session_name = None

    for name, data in _pending.items():
        if data["event"].sender_id == event.sender_id:
            item = data
            session_name = name
            break

    if item is None:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك."
        )

    client = item["client"]

    try:
        await client.sign_in(
            phone=item["phone"],
            code=code,
            phone_code_hash=item["phone_code_hash"],
        )

        me = await client.get_me()
        username = f"@{me.username}" if me.username else "بدون معرف"

        await client.disconnect()
        _pending.pop(session_name, None)

        return await edit_or_reply(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ جلسة الحساب محليًا."
        )

    except SessionPasswordNeededError:
        return await edit_or_reply(
            event,
            "🔐 الحساب محمي بالتحقق بخطوتين.\n\n"
            "أرسل كلمة مرور 2FA بهذا الشكل:\n"
            "`كلمة_مرور 123456`"
        )

    except PhoneCodeInvalidError:
        return await edit_or_reply(
            event,
            "❌ كود Telegram غير صحيح."
        )

    except PhoneCodeExpiredError:
        _pending.pop(session_name, None)
        await client.disconnect()
        return await edit_or_reply(
            event,
            "❌ انتهت صلاحية الكود. ابدأ عملية جديدة باستخدام أمر `مصنع`."
        )

    except Exception as e:
        LOGS.exception("Account code error")
        return await edit_delete(event, f"❌ خطأ:\n`{e}`", 8)


@Tepthon_cmd(pattern=r"كلمة_مرور(?:\s+|$)([\s\S]*)")
async def account_password(event):
    """إدخال كلمة مرور 2FA للحساب الجاري تنصيبه."""

    password = event.pattern_match.group(1).strip()

    if not password:
        return await edit_or_reply(
            event,
            "❌ أرسل كلمة المرور هكذا:\n`كلمة_مرور ********`"
        )

    item = None
    session_name = None

    for name, data in _pending.items():
        if data["event"].sender_id == event.sender_id:
            item = data
            session_name = name
            break

    if item is None:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك."
        )

    client = item["client"]

    try:
        await client.sign_in(password=password)

        me = await client.get_me()
        username = f"@{me.username}" if me.username else "بدون معرف"

        await client.disconnect()
        _pending.pop(session_name, None)

        return await edit_or_reply(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ جلسة الحساب محليًا."
        )

    except Exception as e:
        LOGS.exception("Account password error")
        return await edit_delete(event, f"❌ خطأ:\n`{e}`", 8)


@Tepthon_cmd(pattern=r"حسابات$")
async def list_accounts(event):
    """عرض الحسابات المثبتة محليًا."""

    sessions = sorted(SESSIONS_DIR.glob("*.session"))

    if not sessions:
        return await edit_or_reply(
            event,
            "📂 لا توجد حسابات مثبتة حاليًا."
        )

    text = "📋 **الحسابات المثبتة محليًا:**\n\n"

    for index, session in enumerate(sessions, 1):
        text += f"{index}. `{session.stem}`\n"

    text += "\n🔐 ملفات الجلسات محفوظة محليًا فقط."

    return await edit_or_reply(event, text)
