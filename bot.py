#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════
#         ✦  A R C E N   W E B   F E T C H E R   B O T  ✦
#           Private Only · Colored Buttons · Notifications
# ══════════════════════════════════════════════════════════════

import subprocess, sys

def _ensure(pkg, imp=None):
    imp = imp or pkg
    try: __import__(imp)
    except ImportError:
        print(f"⏳ تثبيت {pkg}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"✅ تم — أعد التشغيل"); sys.exit(0)
        except Exception as e:
            print(f"❌ {e}"); sys.exit(1)

_ensure("aiogram")
_ensure("aiohttp")

import asyncio, aiohttp, urllib.parse, socket, time, json, os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus

# ══════════════════════════════════════════════════════════════
# الإعدادات
# ══════════════════════════════════════════════════════════════
TOKEN = "8739785882:AAHkiglPDis5oCtFGGsmXYUckvCZmSld5Bc"
OWNER_ID = 8746978949

FORCE_CHANNELS = ["@ebh_7", "@ehb_z", "@ft2_q"]

CHANNEL_LINKS = [
    ("📢 قناة 1", "https://t.me/ebh_7"),
    ("📢 قناة 2", "https://t.me/ehb_z"),
    ("📢 قناة 3", "https://t.me/ft2_q"),
]

CONTACT_URL = "https://t.me/ehb3bot"
CHANNEL_URL = "https://t.me/ehb_z"

USERS_FILE = "bot_users.json"
API = f"https://api.telegram.org/bot{TOKEN}"

_b0t1 = Bot(token=TOKEN)
_d1sp = Dispatcher()

# ══════════════════════════════════════════════════════════════
# تخزين المستخدمين
# ══════════════════════════════════════════════════════════════
def _load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except: pass
    return set()

def _save_users(users_set):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users_set), f)
    except Exception as e:
        print(f"[users save] {e}")

_known_users = _load_users()

# ══════════════════════════════════════════════════════════════
# Raw API
# ══════════════════════════════════════════════════════════════
async def _raw_post(method, payload, form_data=None):
    async with aiohttp.ClientSession() as s:
        if form_data is not None:
            async with s.post(f"{API}/{method}", data=form_data) as r:
                return await r.json()
        else:
            async with s.post(f"{API}/{method}", json=payload) as r:
                return await r.json()

async def _send_styled(chat_id, text, buttons):
    kb = {"inline_keyboard": [[b] for b in buttons]}
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(kb),
    }
    return await _raw_post("sendMessage", payload)

async def _send_doc_styled(chat_id, text, buttons, file_bytes, filename):
    kb = {"inline_keyboard": [[b] for b in buttons]}
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field("caption", text)
    form.add_field("parse_mode", "HTML")
    form.add_field("reply_markup", json.dumps(kb))
    form.add_field("document", file_bytes, filename=filename,
                   content_type="application/octet-stream")
    return await _raw_post("sendDocument", {}, form_data=form)

# ══════════════════════════════════════════════════════════════
# لوحة الاشتراك الإجباري
# ══════════════════════════════════════════════════════════════
async def _send_subscription_prompt(chat_id):
    kb = {"inline_keyboard": []}
    for name, url in CHANNEL_LINKS:
        kb["inline_keyboard"].append([
            {"text": name, "url": url, "style": "danger"}
        ])
    kb["inline_keyboard"].append([
        {"text": "✅ تحقق من الاشتراك",
         "callback_data": "check_sub",
         "style": "success"}
    ])
    payload = {
        "chat_id": chat_id,
        "text": ("🔒 <b>أهلاً بك! 👋</b>\n\n"
                 "يجب الاشتراك في القنوات التالية أولاً لاستخدام البوت:"),
        "parse_mode": "HTML",
        "reply_markup": json.dumps(kb),
    }
    await _raw_post("sendMessage", payload)

# ══════════════════════════════════════════════════════════════
# فحص الاشتراك
# ══════════════════════════════════════════════════════════════
async def _is_subscribed(bot: Bot, user_id: int) -> bool:
    for ch in FORCE_CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if m.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                return False
        except Exception as e:
            print(f"[sub] {ch}: {e}")
            return False
    return True

async def _require_subscription(_m: types.Message) -> bool:
    if await _is_subscribed(_m.bot, _m.from_user.id):
        return True
    await _send_subscription_prompt(_m.chat.id)
    return False

# ══════════════════════════════════════════════════════════════
# إشعار مستخدم جديد
# ══════════════════════════════════════════════════════════════
async def _notify_new_user(u: types.User):
    global _known_users
    uid_str = str(u.id)
    if uid_str in _known_users:
        return
    _known_users.add(uid_str)
    _save_users(_known_users)

    full_name = f"{u.first_name or ''} {u.last_name or ''}".strip() or "بدون اسم"
    username = f"@{u.username}" if u.username else "بدون يوزر"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = (
        "🆕 <b>مستخدم جديد دخل البوت</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>الاسم:</b> {full_name}\n"
        f"📛 <b>اليوزر:</b> {username}\n"
        f"🆔 <b>الآيدي:</b> <code>{u.id}</code>\n"
        f"🌐 <b>اللغة:</b> {u.language_code or 'غير محدد'}\n"
        f"🕐 <b>الوقت:</b> {now}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>الإجمالي:</b> {len(_known_users)}"
    )
    buttons = [
        {"text": "🛡️ تواصل مع المستخدم", "url": f"tg://user?id={u.id}", "style": "primary"},
        {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "danger"},
    ]
    try:
        await _send_styled(OWNER_ID, text, buttons)
    except Exception as e:
        print(f"[notif] {e}")

# ══════════════════════════════════════════════════════════════
# إشعار التوقف
# ══════════════════════════════════════════════════════════════
async def _notify_ban(bot: Bot, reason: str = "غير معروف"):
    try:
        text = (
            "🚨 <b>تحذير — البوت توقف</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>السبب:</b> {reason}\n"
            f"🕐 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🔧 <b>تحقق من التوكن أو الاستضافة</b>"
        )
        try:
            await bot.send_message(OWNER_ID, text, parse_mode="HTML")
        except:
            async with aiohttp.ClientSession() as s:
                await s.post(f"{API}/sendMessage", json={
                    "chat_id": OWNER_ID, "text": text, "parse_mode": "HTML"
                })
    except Exception as e:
        print(f"[notify ban] {e}")

# ══════════════════════════════════════════════════════════════
# /start — خاص فقط
# ══════════════════════════════════════════════════════════════
@_d1sp.message(Command("start"), F.chat.type == "private")
async def _sT4rt(_m: types.Message):
    await _notify_new_user(_m.from_user)

    if not await _require_subscription(_m):
        return

    await _send_styled(
        _m.chat.id,
        "👋 <b>مرحباً بك في بوت سحب ملفات المواقع</b>\n\n"
        "⚡ أرسل أي رابط يبدأ بـ http أو https\n"
        "📄 سيتم تحميل الصفحة كملف HTML\n"
        "🎨 مع معلومات الموقع التقنية\n\n"
        "👤 المطور: @ehb3bot",
        buttons=[
            {"text": "تواصل مع المطور 🛡️", "url": CONTACT_URL, "style": "primary"},
            {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "danger"},
        ]
    )

# ══════════════════════════════════════════════════════════════
# زر التحقق
# ══════════════════════════════════════════════════════════════
@_d1sp.callback_query(F.data == "check_sub")
async def _check_sub_cb(call: types.CallbackQuery):
    if await _is_subscribed(call.bot, call.from_user.id):
        await call.answer("✅ تم التحقق — يمكنك استخدام البوت الآن", show_alert=True)
        try: await call.message.delete()
        except: pass
        await _send_styled(
            call.message.chat.id,
            "👋 <b>مرحباً بك في بوت سحب ملفات المواقع</b>\n\n"
            "⚡ أرسل أي رابط يبدأ بـ http أو https\n"
            "📄 سيتم تحميل الصفحة كملف HTML\n\n"
            "👤 المطور: @ehb3bot",
            buttons=[
                {"text": "تواصل مع المطور 🛡️", "url": CONTACT_URL, "style": "primary"},
                {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "danger"},
            ]
        )
    else:
        await call.answer("❌ لم تشترك في كل القنوات بعد", show_alert=True)

# ══════════════════════════════════════════════════════════════
# سحب الرابط — خاص فقط
# ══════════════════════════════════════════════════════════════
@_d1sp.message(F.text.startswith("http"), F.chat.type == "private")
async def _f3tch(_m: types.Message):
    await _notify_new_user(_m.from_user)

    if not await _require_subscription(_m):
        return

    _w = await _m.answer("⏳ <b>جاري سحب الملف...</b>", parse_mode="HTML")
    t0 = time.time()

    try:
        _u = _m.text.strip()
        _p = urllib.parse.urlparse(_u)
        if _p.scheme not in ("http", "https") or not _p.netloc:
            await _m.answer("❌ الرابط غير صحيح.")
            return

        try:
            ip = socket.gethostbyname(_p.netloc)
        except:
            ip = "غير معروف"

        timeout = aiohttp.ClientTimeout(total=20, connect=8)
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        }

        async with aiohttp.ClientSession() as s:
            async with s.get(_u, timeout=timeout, headers=headers,
                             allow_redirects=True) as r:
                if r.status != 200:
                    await _m.answer(f"❌ فشل — رمز: <code>{r.status}</code>",
                                    parse_mode="HTML")
                    return

                data = await r.read()
                ctype = r.headers.get("Content-Type", "text/html").split(";")[0]
                size_kb = len(data) / 1024

                if size_kb > 500:
                    await _m.answer("❌ الملف كبير (>500 KB)")
                    return

                fname = "website_source.html"
                elapsed = time.time() - t0

                caption = (
                    f"🌍 <b>رابط الموقع:</b> <code>{_u}</code>\n\n"
                    f"📁 <b>الملف:</b>\n"
                    f"📄 <b>الاسم:</b> <code>{fname}</code>\n"
                    f"📦 <b>الحجم:</b> {size_kb:.2f} KB\n"
                    f"📃 <b>النوع:</b> {ctype}\n\n"
                    f"🧰 <b>معلومات تقنية:</b>\n"
                    f"🔌 <b>السيرفر:</b> {_p.netloc}\n"
                    f"📡 <b>IP:</b> <code>{ip}</code>\n"
                    f"⚡ <b>الوقت:</b> {elapsed:.2f}ث"
                )

                await _send_doc_styled(
                    _m.chat.id, caption,
                    buttons=[
                        {"text": "تواصل مع المطور 🛡️", "url": CONTACT_URL, "style": "primary"},
                        {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "danger"},
                    ],
                    file_bytes=data,
                    filename=fname
                )

    except asyncio.TimeoutError:
        await _m.answer("⏰ <b>انتهت المهلة</b>", parse_mode="HTML")
    except aiohttp.ClientError as e:
        await _m.answer(f"❌ <b>خطأ اتصال:</b>\n<code>{str(e)[:150]}</code>",
                        parse_mode="HTML")
    except Exception as e:
        await _m.answer(f"❌ <b>خطأ:</b>\n<code>{str(e)[:150]}</code>",
                        parse_mode="HTML")
    finally:
        try: await _w.delete()
        except: pass

# ══════════════════════════════════════════════════════════════
# رسائل أخرى — خاص فقط
# ══════════════════════════════════════════════════════════════
@_d1sp.message(F.chat.type == "private")
async def _eRr0r(_m: types.Message):
    await _notify_new_user(_m.from_user)

    if not await _require_subscription(_m):
        return
    await _send_styled(
        _m.chat.id,
        "❌ <b>يرجى إرسال رابط صحيح</b>\n\n"
        "📌 الرابط يجب أن يبدأ بـ <code>http</code> أو <code>https</code>",
        buttons=[
            {"text": "تواصل مع المطور 🛡️", "url": CONTACT_URL, "style": "primary"},
            {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "danger"},
        ]
    )

# ══════════════════════════════════════════════════════════════
# /stats
# ══════════════════════════════════════════════════════════════
@_d1sp.message(Command("stats"), F.chat.type == "private")
async def _st4ts(_m: types.Message):
    if _m.from_user.id != OWNER_ID:
        return
    await _m.answer(
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون: <b>{len(_known_users)}</b>\n"
        f"📢 القنوات: <b>{len(FORCE_CHANNELS)}</b>\n"
        f"⚙️ الحالة: <b>يعمل</b>",
        parse_mode="HTML"
    )

# ══════════════════════════════════════════════════════════════
# التشغيل
# ══════════════════════════════════════════════════════════════
async def _rUn():
    print("=" * 50)
    print("🚀 ARCEN Web Fetcher (Private Only)")
    print(f"👤 Owner: {OWNER_ID}")
    print(f"👥 Users: {len(_known_users)}")
    print("=" * 50)

    try:
        await _send_styled(
            OWNER_ID,
            f"✅ <b>البوت اشتغل</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 <b>الحالة:</b> يعمل\n"
            f"💬 <b>النوع:</b> خاص فقط (Private)\n"
            f"👥 <b>المستخدمون:</b> {len(_known_users)}\n"
            f"🕐 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            buttons=[
                {"text": "📢 قناة البوت", "url": CHANNEL_URL, "style": "primary"}
            ]
        )
    except Exception as e:
        print(f"[start notify] {e}")

    print("🤖 البوت يعمل...")
    try:
        await _d1sp.start_polling(_b0t1)
    except Exception as e:
        print(f"❌ توقف: {e}")
        await _notify_ban(_b0t1, reason=str(e)[:100])
        raise

if __name__ == "__main__":
    try:
        asyncio.run(_rUn())
    except KeyboardInterrupt:
        try: asyncio.run(_notify_ban(_b0t1, reason="إيقاف يدوي (Ctrl+C)"))
        except: pass
        print("⛔ تم الإيقاف")
    except Exception as e:
        print(f"❌ خطأ نهائي: {e}")
        try: asyncio.run(_notify_ban(_b0t1, reason=f"خطأ: {str(e)[:100]}"))
        except: pass