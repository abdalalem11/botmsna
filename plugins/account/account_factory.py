# =========================================================
# Tepthon Account Factory
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

# الاستيرادات الصحيحة حسب بنية Tepthon
from Tepthon.decorators.command import Tepthon_cmd
from Tepthon.config import Var


LOGS = logging.getLogger(__name__)

# =========================================================
# إعداد مجلد الجلسات
# =========================================================

SESSIONS_DIR = Path("database/account_sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# العمليات المعلقة:
# sender_id -> بيانات عملية التنصيب
_pending = {}

# مدة صلاحية العملية المعلقة: 10 دقائق
PENDING_TIMEOUT = 600


# =========================================================
# أدوات مساعدة
# =========================================================

def get_api_credentials():
    """جلب API_ID و API_HASH من إعدادات Tepthon."""

    try:
        api_id = int(Var.API_ID)
        api_hash = str(Var.API_HASH).strip()

        if not api_id or not api_hash:
            return None, None

        return api_id, api_hash

    except Exception:
        LOGS.exception("Failed to load API credentials")
        return None, None


def clean_phone(phone):
    """تنظيف رقم الهاتف."""

    return (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def session_name(phone):
    """تحويل الرقم إلى اسم جلسة آمن."""

    return phone.replace("+", "").replace("-", "")


async def safe_edit(event, text):
    """تعديل رسالة الأمر بدون الحاجة إلى managers."""

    try:
        return await event.edit(text)
    except Exception:
        try:
            return await event.respond(text)
        except Exception:
            LOGS.exception("Could not edit/respond to event")


async def safe_delete(event):
    """حذف رسالة الأمر إذا أمكن."""

    try:
        await event.delete()
    except Exception:
        pass


async def cleanup_pending(sender_id):
    """إغلاق وإزالة العملية المعلقة."""

    data = _pending.pop(sender_id, None)

    if not data:
        return

    task = data.get("task")

    if task:
        try:
            if task is not asyncio.current_task():
                task.cancel()
        except Exception:
            pass

    client = data.get("client")

    if client:
        try:
            if client.is_connected():
                await client.disconnect()
        except Exception:
            LOGS.exception("Failed to disconnect pending client")


async def pending_timeout(sender_id):
    """إلغاء العملية تلقائيًا بعد انتهاء الوقت."""

    try:
        await asyncio.sleep(PENDING_TIMEOUT)

        if sender_id in _pending:
            await cleanup_pending(sender_id)

    except asyncio.CancelledError:
        pass

    except Exception:
        LOGS.exception("Pending timeout error")


def get_pending(sender_id):
    """الحصول على العملية المعلقة."""

    return _pending.get(sender_id)


# =========================================================
# مصنع الحسابات
# =========================================================

@Tepthon_cmd(pattern=r"مصنع(?:\s+|$)([\s\S]*)")
async def account_factory(event):

    api_id, api_hash = get_api_credentials()

    if not api_id or not api_hash:
        return await safe_edit(
            event,
            "❌ **خطأ في إعدادات Telegram**\n\n"
            "لم يتم العثور على API_ID أو API_HASH.\n\n"
            "تأكد من إعداد متغيرات البيئة في السيرفر."
        )

    sender_id = event.sender_id

    # منع تشغيل أكثر من عملية لنفس المستخدم
    if sender_id in _pending:
        return await safe_edit(
            event,
            "⏳ لديك عملية تنصيب معلقة بالفعل.\n\n"
            "أرسل `الغاء_المصنع` لإلغائها."
        )

    phone = event.pattern_match.group(1).strip()

    if not phone:
        return await safe_edit(
            event,
            "🛠 **مصنع الحسابات**\n\n"
            "الاستخدام:\n"
            "`مصنع +9665xxxxxxxx`\n\n"
            "مثال:\n"
            "`مصنع +966512345678`"
        )

    phone = clean_phone(phone)

    if not phone.startswith("+"):
        return await safe_edit(
            event,
            "❌ يجب إرسال الرقم بالصيغة الدولية.\n\n"
            "مثال:\n"
            "`مصنع +966512345678`"
        )

    if not phone[1:].isdigit():
        return await safe_edit(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    name = session_name(phone)
    session_path = SESSIONS_DIR / name

    client = TelegramClient(
        str(session_path),
        api_id,
        api_hash,
    )

    try:
        await client.connect()

        # التحقق من وجود جلسة سابقة
        if await client.is_user_authorized():

            me = await client.get_me()

            username = (
                f"@{me.username}"
                if me.username
                else "بدون معرف"
            )

            await client.disconnect()

            return await safe_edit(
                event,
                "✅ **الحساب مثبت مسبقًا**\n\n"
                f"👤 الاسم: `{me.first_name or ''}`\n"
                f"🆔 ID: `{me.id}`\n"
                f"🔗 المعرف: `{username}`\n"
                f"📱 الرقم: `{phone}`"
            )

        # إرسال كود Telegram
        sent = await client.send_code_request(phone)

        _pending[sender_id] = {
            "client": client,
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "session_name": name,
            "task": None,
        }

        # تشغيل مؤقت للعملية
        _pending[sender_id]["task"] = asyncio.create_task(
            pending_timeout(sender_id)
        )

        return await safe_edit(
            event,
            "📲 **تم إرسال كود Telegram بنجاح.**\n\n"
            "أرسل الكود بهذا الشكل:\n"
            "`كود 12345`\n\n"
            "⚠️ لا تشارك كود تسجيل الدخول مع أي شخص."
        )

    except ApiIdInvalidError:

        try:
            await client.disconnect()
        except Exception:
            pass

        return await safe_edit(
            event,
            "❌ API_ID أو API_HASH غير صحيح."
        )

    except PhoneNumberInvalidError:

        try:
            await client.disconnect()
        except Exception:
            pass

        return await safe_edit(
            event,
            "❌ رقم الهاتف غير صحيح."
        )

    except FloodWaitError as error:

        try:
            await client.disconnect()
        except Exception:
            pass

        return await safe_edit(
            event,
            f"⏳ Telegram طلب الانتظار.\n\n"
            f"المدة: `{error.seconds}` ثانية."
        )

    except Exception as error:

        LOGS.exception("Account factory error")

        try:
            await client.disconnect()
        except Exception:
            pass

        return await safe_edit(
            event,
            f"❌ حدث خطأ أثناء إنشاء الحساب:\n\n"
            f"`{error}`"
        )


# =========================================================
# إدخال كود Telegram
# =========================================================

@Tepthon_cmd(pattern=r"كود(?:\s+|$)([\s\S]*)")
async def account_code(event):

    code = event.pattern_match.group(1).strip()

    if not code:
        return await safe_edit(
            event,
            "❌ أرسل الكود بهذا الشكل:\n"
            "`كود 12345`"
        )

    code = (
        code
        .replace(" ", "")
        .replace("-", "")
    )

    if not code.isdigit():
        return await safe_edit(
            event,
            "❌ الكود يجب أن يحتوي على أرقام فقط."
        )

    sender_id = event.sender_id
    item = get_pending(sender_id)

    if not item:
        return await safe_edit(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك.\n\n"
            "ابدأ أولًا باستخدام:\n"
            "`مصنع +رقم`"
        )

    client = item["client"]

    try:
        if not client.is_connected():
            await client.connect()

        # تسجيل الدخول بالكود
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

        # إيقاف المؤقت
        task = item.get("task")

        if task:
            try:
                task.cancel()
            except Exception:
                pass

        _pending.pop(sender_id, None)

        await client.disconnect()

        return await safe_edit(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ جلسة الحساب محليًا."
        )

    except SessionPasswordNeededError:

        return await safe_edit(
            event,
            "🔐 **الحساب محمي بالتحقق بخطوتين 2FA**\n\n"
            "أرسل كلمة المرور بهذا الشكل:\n"
            "`كلمة_مرور كلمة_المرور`"
        )

    except PhoneCodeInvalidError:

        return await safe_edit(
            event,
            "❌ كود Telegram غير صحيح."
        )

    except PhoneCodeExpiredError:

        await cleanup_pending(sender_id)

        return await safe_edit(
            event,
            "❌ انتهت صلاحية الكود.\n\n"
            "ابدأ عملية جديدة باستخدام:\n"
            "`مصنع +رقم`"
        )

    except FloodWaitError as error:

        return await safe_edit(
            event,
            f"⏳ Telegram طلب الانتظار.\n\n"
            f"المدة: `{error.seconds}` ثانية."
        )

    except Exception as error:

        LOGS.exception("Account code error")

        return await safe_edit(
            event,
            f"❌ حدث خطأ:\n\n"
            f"`{error}`"
        )


# =========================================================
# كلمة مرور 2FA
# =========================================================

@Tepthon_cmd(pattern=r"كلمة_مرور(?:\s+|$)([\s\S]*)")
async def account_password(event):

    password = event.pattern_match.group(1).strip()

    if not password:
        return await safe_edit(
            event,
            "❌ أرسل كلمة المرور بهذا الشكل:\n"
            "`كلمة_مرور ********`"
        )

    sender_id = event.sender_id
    item = get_pending(sender_id)

    if not item:
        return await safe_edit(
            event,
            "❌ لا توجد عملية تنصيب معلقة لك."
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
            try:
                task.cancel()
            except Exception:
                pass

        _pending.pop(sender_id, None)

        await client.disconnect()

        return await safe_edit(
            event,
            "✅ **تم تنصيب الحساب بنجاح**\n\n"
            f"👤 الاسم: `{me.first_name or ''}`\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 المعرف: `{username}`\n"
            f"📱 الرقم: `{item['phone']}`\n\n"
            "🔐 تم حفظ جلسة الحساب محليًا."
        )

    except PasswordHashInvalidError:

        return await safe_edit(
            event,
            "❌ كلمة مرور 2FA غير صحيحة."
        )

    except FloodWaitError as error:

        return await safe_edit(
            event,
            f"⏳ Telegram طلب الانتظار.\n\n"
            f"المدة: `{error.seconds}` ثانية."
        )

    except Exception as error:

        LOGS.exception("Account password error")

        return await safe_edit(
            event,
            f"❌ حدث خطأ:\n\n"
            f"`{error}`"
        )


# =========================================================
# عرض الحسابات المثبتة
# =========================================================

@Tepthon_cmd(pattern=r"حسابات$")
async def list_accounts(event):

    try:

        sessions = sorted(
            SESSIONS_DIR.glob("*.session")
        )

        if not sessions:
            return await safe_edit(
                event,
                "📂 **لا توجد حسابات مثبتة حاليًا.**"
            )

        text = "📋 **الحسابات المثبتة محليًا:**\n\n"

        for index, session in enumerate(sessions, 1):
            text += f"{index}. `{session.stem}`\n"

        text += (
            "\n🔐 ملفات الجلسات محفوظة محليًا فقط."
        )

        return await safe_edit(
            event,
            text
        )

    except Exception as error:

        LOGS.exception("List accounts error")

        return await safe_edit(
            event,
            f"❌ حدث خطأ:\n\n"
            f"`{error}`"
        )


# =========================================================
# إلغاء عملية المصنع
# =========================================================

@Tepthon_cmd(pattern=r"الغاء_المصنع$")
async def cancel_factory(event):

    sender_id = event.sender_id

    if not get_pending(sender_id):
        return await safe_edit(
            event,
            "❌ لا توجد عملية تنصيب معلقة."
        )

    await cleanup_pending(sender_id)

    return await safe_edit(
        event,
        "✅ تم إلغاء عملية تنصيب الحساب."
    )


# =========================================================
# حقوق المطور: @SSSTlF
# =========================================================
