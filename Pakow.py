import asyncio
import sqlite3
import time
from datetime import date

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

# ================= CONFIG =================
BOT_TOKEN = "8528454589:AAHffKDtvFJ2s_1_qX_NK2Gfkdz5wA4csCE"
ADMIN_IDS = [8452357204]  # your telegram ID
WEBSITE_URL = "http://www.quizzygram.com"
WINNER_DATE = date(2026, 1, 4)  # Jan 4
# =========================================

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

db = sqlite3.connect("bot.db")
cursor = db.cursor()

# ================= DATABASE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    referrals INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    tasks_done INTEGER DEFAULT 0,
    last_task INTEGER DEFAULT 0,
    referred_by INTEGER
)
""")
db.commit()
# ===========================================

# ================= KEYBOARD =================
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 Task", callback_data="task"),
            InlineKeyboardButton(text="👥 Referral", callback_data="ref")
        ],
        [
            InlineKeyboardButton(text="📊 My Chart", callback_data="chart"),
            InlineKeyboardButton(text="🏆 Leaders", callback_data="leaders")
        ],
        [
            InlineKeyboardButton(text="🎁 Gifts Info", callback_data="gifts")
        ]
    ])
# ===========================================

# ================= START ====================
@router.message(CommandStart())
async def start(message: Message):
    args = message.text.split()
    ref = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (message.from_user.id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)",
            (message.from_user.id, message.from_user.username, ref)
        )
        db.commit()

    cursor.execute("UPDATE users SET username=? WHERE user_id=?",
                   (message.from_user.username, message.from_user.id))
    db.commit()

    await message.answer(
        f"""
🎉 <b>WELCOME TO ⭐ STAR GIFT REWARD BOT ⭐</b>

👋 Hello @{message.from_user.username or "User"}

🎯 Website එකට ගිහිං
⏳ <b>15 minutes</b> හිටියොත්
➕ <b>Coins 2</b> add වෙනවා

👥 Referral share කරලා
🏆 <b>Jan 4</b> දින
Telegram ⭐ Star Gifts දිනාගන්න!

🥇 100 Stars
🥈 50 Stars
🥉 25 Stars

👇 Buttons භාවිතා කරන්න
        """,
        reply_markup=main_kb()
    )
# ===========================================

# ================= CALLBACKS =================
@router.callback_query()
async def callbacks(call):
    uid = call.from_user.id

    if call.data == "task":
        await call.message.answer(
            "🎯 <b>Website Task</b>\n\n"
            "1️⃣ Website open කරන්න\n"
            "2️⃣ ⏳ 15 minutes හිටින්\n"
            "3️⃣ නැවත ආපහු බොට් එකට ඇවිත් <b>Confirm</b> කරන්න\n\n"
            "⚠️ 하루ට එක task පමණයි",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Visit Website", url=WEBSITE_URL)],
                [InlineKeyboardButton(text="✅ Confirm", callback_data="confirm")]
            ])
        )

    elif call.data == "confirm":
        now = int(time.time())
        cursor.execute("SELECT last_task FROM users WHERE user_id=?", (uid,))
        last = cursor.fetchone()[0]

        if now - last < 86400:
            await call.answer("❌ Today task already completed", show_alert=True)
            return

        cursor.execute("""
        UPDATE users
        SET coins = coins + 2,
            tasks_done = tasks_done + 1,
            last_task = ?
        WHERE user_id=?
        """, (now, uid))

        # referral count
        cursor.execute("SELECT referred_by FROM users WHERE user_id=?", (uid,))
        ref = cursor.fetchone()[0]
        if ref:
            cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (ref,))

        db.commit()
        await call.message.answer("✅ Task completed!\n➕ Coins +2")

    elif call.data == "ref":
        await call.message.answer(
            f"👥 <b>Your Referral Link</b>\n\n"
            f"https://t.me/{(await bot.me()).username}?start={uid}"
        )

    elif call.data == "chart":
        cursor.execute("SELECT referrals, coins, tasks_done FROM users WHERE user_id=?", (uid,))
        r, c, t = cursor.fetchone()
        await call.message.answer(
            f"📊 <b>My Chart</b>\n\n"
            f"👥 Referrals: {r}\n"
            f"⭐ Coins: {c}\n"
            f"🎯 Tasks: {t}"
        )

    elif call.data == "leaders":
        cursor.execute("""
        SELECT username, referrals FROM users
        ORDER BY referrals DESC LIMIT 5
        """)
        rows = cursor.fetchall()
        text = "🏆 <b>Top Leaders</b>\n\n"
        for i, r in enumerate(rows, 1):
            text += f"{i}. @{r[0] or 'User'} — {r[1]} refs\n"
        await call.message.answer(text)

    elif call.data == "gifts":
        await call.message.answer(
            "🎁 <b>Star Gifts</b>\n\n"
            "🥇 1st → ⭐ 100\n"
            "🥈 2nd → ⭐ 50\n"
            "🥉 3rd → ⭐ 25\n\n"
            "📅 Winner date: Jan 4"
        )

# ================= ADMIN =====================
@router.message(Command("movie"))
async def movie(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    cursor.execute("""
    SELECT user_id, username, referrals
    FROM users ORDER BY referrals DESC LIMIT 3
    """)
    data = cursor.fetchall()

    medals = ["🥇", "🥈", "🥉"]
    stars = [100, 50, 25]

    text = "🎬 <b>TOP 3 REFERRAL LEADERS</b>\n\n"
    for i, u in enumerate(data):
        name = f"@{u[1]}" if u[1] else f"<a href='tg://user?id={u[0]}'>User</a>"
        text += f"{medals[i]} {name}\n👥 Referrals: {u[2]}\n⭐ Reward: {stars[i]} Stars\n\n"

    await message.answer(text)
# ============================================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
