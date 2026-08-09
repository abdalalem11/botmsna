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

from .. import Tepthon_cmd
from ..config import Var
from ..core.managers import edit_delete, edit_or_reply

LOGS = logging.getLogger(__name__)

# =========================================================
# إعدادات الجلسات
# =========================================================

SESSIONS_DIR = Path("database/account_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# العمليات المعلقة:
# key = sender_id
# value = بيانات عملية التنصيب
_pending = {}

# مدة انتهاء العملية المعلقة: 10 دقائق
PENDING_TIMEOUT = 600


# =========================================================
# أدوات مساعدة
# =========================================================

def _get_api_credentials():
    """الحصول على API_ID و API_HASH من إعدادات Tepthon."""

    try:
        api_id = int(Var.API_ID)
        api_hash = str(Var.API_HASH).strip()

        if not api_id or not api_hash:
            return None, None

        return api_id, api_hash

    except Exception:
        LOGS.exception("Unable to load API_ID/API_HASH")
        return None, None


def _clean_phone(phone):
    """تنظيف رقم الهاتف."""

    phone = phone.strip()
    phone = phone.replace(" ", "")
    phone = phone.replace("-", "")
    phone = phone.replace("(", "")
    phone = phone.replace(")", "")

    return phone


def _session_name(phone):
    """إنشاء اسم آمن لملف الجلسة."""

    return phone.replace("+", "").replace(" ", "").replace("-", "")


async def _cleanup_pending(sender_id):
    """إغلاق وحذف العملية المعلقة."""

    data = _pending.pop(sender_id, None)

    if not data:
        return

    client = data.get("client")

    if client:
        try:
            if client.is_connected():
                await client.disconnect()
        except Exception:
            LOGS.exception("Failed to disconnect pending client")


async def _expire_pending(sender_id):
    """إلغاء العملية تلقائيًا بعد مدة معينة."""

    try:
        await asyncio.sleep(PENDING_TIMEOUT)

        if sender_id in _pending:
            await _cleanup_pending(sender_id)
            LOGS.info(
                "Account installation expired for sender_id=%s",
                sender_id,
            )

    except asyncio.CancelledError:
        pass
    except Exception:
        LOGS.exception("Pending expiration error")


def _get_pending(event):
    """الحصول على العملية المعلقة الخاصة بالمستخدم."""

    try:
        sender_id = event.sender_id
    except Exception:
        return None

    if not sender_id:
        return None

    return _pending.get(sender_id)


# =========================================================
# مصنع الحسابات
# =========================================================

@Tepthon_cmd(pattern=r"مصنع(?:\s+|$)([\s\S]*)")
async def account_factory(event):
    """
    بدء تنصيب حساب Telegram إضافي.
    
    الاستخدام:
    مصنع +9665xxxxxxxx
    """

    api_id, api_hash = _get_api_credentials()

    if not api_id or not api_hash:
        return await edit_or_reply(
            event,
            "❌ لم يتم العثور على API_ID و API_HASH.\n\n"
            "تأكد من إعداد:\n"
            "`Var.API_ID`\n"
            "`Var.API_HASH`\n\n"
            "داخل ملف config.py."
        )

    try:
        sender_id = event.sender_id
    except Exception:
        sender_id = None

    if not sender_id:
        return await edit_or_reply(
            event,
            "❌ تعذر تحديد صاحب العملية."
        )

    # منع تشغيل عمليتين لنفس المستخدم
    if sender_id in _pending:
        return await edit_or_reply(
            event,
            "⏳ لديك عملية تنصيب معلقة بالفعل.\n\n"
            "أكمل العملية الحالية أولًا."
        )

    arg = event.pattern_match.group(1).strip()

    if not arg:
        return await edit_or_reply(
            event,
            "🛠 **مصنع الحسابات**\n\n"
            "الاستخدام:\n"
            "`مصنع +9665xxxxxxxx`\n\n"
            "مثال:\n"
            "`مصنع +966512345678`\n\n"
            "بعدها سيتم إرسال كود تسجيل الدخول من Telegram."
        )

    phone = _clean_phone(arg)

    # التحقق من الرقم
    if not phone.startswith("+"):
        return await edit_or_reply(
            event,
            "❌ يجب إرسال الرقم بالصيغة الدولية.\n\n"
            "مثال:\n"
            "`مصنع +966512345678`"
        )

    if not phone[1:].isdigit():
        return await edit_or_reply(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    if len(phone) < 8:
        return await edit_or_reply(
            event,
            "❌ رقم الهاتف قصير جدًا."
        )

    session_name = _session_name(phone)
    session_path = SESSIONS_DIR / session_name

    # =====================================================
    # إنشاء العميل
    # =====================================================

    client = TelegramClient(
        str(session_path),
        api_id,
        api_hash,
    )

    try:
        await client.connect()

        # إذا كانت الجلسة موجودة ومسجلة مسبقًا
        if await client.is_user_authorized():
            me = await client.get_me()

            await client.disconnect()

            username = (
                f"@{me.username}"
                if me.username
                else "بدون معرف"
            )

            return await edit_or_reply(
                event,
                "✅ **الحساب مثبت مسبقًا**\n\n"
                f"👤 الاسم: `{me.first_name or ''}`\n"
                f"🆔 ID: `{me.id}`\n"
                f"🔗 المعرف: `{username}`\n"
                f"📱 الرقم: `{phone}`"
            )

        # =================================================
        # إرسال كود Telegram
        # =================================================

        sent = await client.send_code_request(phone)

        _pending[sender_id] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "session_name": session_name,
            "task": None,
        }

        # مهمة انتهاء العملية
        task = asyncio.create_task(
            _expire_pending(sender_id)
        )

        _pending[sender_id]["task"] = task

        return await edit_or_reply(
            event,
            "📲 **تم إرسال كود Telegram.**\n\n"
            "أرسل الكود هنا:\n"
            "`كود 12345`\n\n"
            "⚠️ لا تشارك كود تسجيل الدخول مع أي شخص."
        )

    except ApiIdInvalidError:
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
            "❌ رقم الهاتف غير صحيح أو غير صالح."
        )

    except FloodWaitError as e:
        try:
            await client.disconnect()
        except Exception:
            pass

        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار لمدة `{e.seconds}` ثانية."
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
# إدخال كود Telegram
# =========================================================

@Tepthon_cmd(pattern=r"كود(?:\s+|$)([\s\S]*)")
async def account_code(event):
    """
    إدخال كود تسجيل الدخول.

    الاستخدام:
    كود 12345
    """

    code = event.pattern_match.group(1).strip()

    if not code:
        return await edit_or_reply(
            event,
            "❌ أرسل الكود بهذا الشكل:\n"
            "`كود 12345`"
        )

    # إزالة المسافات من الكود
    code = code.replace(" ", "").replace("-", "")

    if not code.isdigit():
        return await edit_or_reply(
            event,
            "❌ الكود يجب أن يحتوي على أرقام فقط."
        )

    item = _get_pending(event)

    if not item:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك.\n\n"
            "ابدأ أولًا باستخدام:\n"
            "`مصنع +رقم`"
        )

    client = item["client"]

    try:
        if not client.is_connected():
            await client.connect()

        # =================================================
        # تسجيل الدخول بالكود
        # =================================================

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

        session_file = str(
            SESSIONS_DIR / f"{item['session_name']}.session"
        )

        # إلغاء مؤقت انتهاء العملية
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
            "🔐 تم حفظ جلسة الحساب محليًا.\n"
            f"📂 `{session_file}`"
        )

    except SessionPasswordNeededError:
        return await edit_or_reply(
            event,
            "🔐 **الحساب محمي بالتحقق بخطوتين.**\n\n"
            "أرسل كلمة مرور 2FA بهذا الشكل:\n"
            "`كلمة_مرور كلمة_المرور`\n\n"
            "⚠️ لا ترسل كلمة المرور لأي شخص."
        )

    except PhoneCodeInvalidError:
        return await edit_or_reply(
            event,
            "❌ كود Telegram غير صحيح.\n\n"
            "حاول مرة أخرى."
        )

    except PhoneCodeExpiredError:
        await _cleanup_pending(event.sender_id)

        return await edit_or_reply(
            event,
            "❌ انتهت صلاحية كود Telegram.\n\n"
            "ابدأ عملية جديدة باستخدام:\n"
            "`مصنع +رقم`"
        )

    except FloodWaitError as e:
        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار لمدة `{e.seconds}` ثانية."
        )

    except Exception as e:
        LOGS.exception("Account code error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ أثناء تسجيل الدخول:\n`{e}`",
            10,
        )


# =========================================================
# إدخال كلمة مرور 2FA
# =========================================================

@Tepthon_cmd(pattern=r"كلمة_مرور(?:\s+|$)([\s\S]*)")
async def account_password(event):
    """
    إدخال كلمة مرور التحقق بخطوتين.

    الاستخدام:
    كلمة_مرور password
    """

    password = event.pattern_match.group(1).strip()

    if not password:
        return await edit_or_reply(
            event,
            "❌ أرسل كلمة المرور بهذا الشكل:\n"
            "`كلمة_مرور ********`"
        )

    item = _get_pending(event)

    if not item:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك."
        )

    client = item["client"]

    try:
        if not client.is_connected():
            await client.connect()

        # =================================================
        # تسجيل الدخول بكلمة مرور 2FA
        # =================================================

        await client.sign_in(password=password)

        me = await client.get_me()

        username = (
            f"@{me.username}"
            if me.username
            else "بدون معرف"
        )

        session_file = str(
            SESSIONS_DIR / f"{item['session_name']}.session"
        )

        # إلغاء مؤقت انتهاء العملية
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
            "🔐 تم حفظ جلسة الحساب محليًا.\n"
            f"📂 `{session_file}`"
        )

    except PasswordHashInvalidError:
        return await edit_or_reply(
            event,
            "❌ كلمة مرور التحقق بخطوتين غير صحيحة."
        )

    except FloodWaitError as e:
        return await edit_or_reply(
            event,
            f"⏳ Telegram طلب الانتظار لمدة `{e.seconds}` ثانية."
        )

    except Exception as e:
        LOGS.exception("Account password error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ أثناء التحقق:\n`{e}`",
            10,
        )


# =========================================================
# عرض الحسابات
# =========================================================

@Tepthon_cmd(pattern=r"حسابات$")
async def list_accounts(event):
    """عرض الحسابات المثبتة محليًا."""

    try:
        sessions = sorted(
            SESSIONS_DIR.glob("*.session")
        )

        if not sessions:
            return await edit_or_reply(
                event,
                "📂 **لا توجد حسابات مثبتة حاليًا.**"
            )

        text = "📋 **الحسابات المثبتة محليًا:**\n\n"

        for index, session in enumerate(sessions, 1):
            text += (
                f"{index}. `{session.stem}`\n"
            )

        text += (
            "\n🔐 ملفات الجلسات محفوظة محليًا فقط."
        )

        return await edit_or_reply(event, text)

    except Exception as e:
        LOGS.exception("List accounts error")

        return await edit_delete(
            event,
            f"❌ حدث خطأ:\n`{e}`",
            8,
        )


# =========================================================
# إلغاء العملية الحالية
# =========================================================

@Tepthon_cmd(pattern=r"الغاء_المصنع$")
async def cancel_factory(event):
    """إلغاء عملية تنصيب معلقة."""

    item = _get_pending(event)

    if not item:
        return await edit_or_reply(
            event,
            "❌ لا توجد عملية تنصيب معلقة."
        )

    await _cleanup_pending(event.sender_id)

    return await edit_or_reply(
        event,
        "✅ تم إلغاء عملية تنصيب الحساب."
    )


# =========================================================
# حقوق المطور: @SSSTlF
# =========================================================
