import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.enums import ParseMode

# ================= CONFIG =================
BOT_TOKEN = "8528454589:AAHffKDtvFJ2s_1_qX_NK2Gfkdz5wA4csCE"
OWNER_ID = 8452357204
WELCOME_IMAGE_PATH = "https://files.catbox.moe/zzlz4j.jpg"  # ඔබේ welcome image path
# ==========================================

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# =============== DATABASE =================
db = sqlite3.connect("starbot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    referrals INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    tasks_done INTEGER DEFAULT 0,
    referred_by INTEGER
)
""")
db.commit()
# ==========================================

# =============== DASHBOARD KB ===============
def dashboard_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🎯 Mission"), KeyboardButton("👥 Invite"))
    kb.row(KeyboardButton("📊 My Chart"), KeyboardButton("🏆 Leaderboard"))
    kb.row(KeyboardButton("🎁 Gifts Info"))  # 👑 Admin Panel button අයිම් කරලා
    return kb
# ============================================

# =============== START / WELCOME =============
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

    photo_path = FSInputFile(WELCOME_IMAGE_PATH)
    await message.answer_photo(
        photo=photo_path,
        caption=f"""
🎉🌟 WELCOME TO STAR GIFT REWARDS BOT 🎁🌟

👋 Hello @{message.from_user.username or 'User'}!

🏆 You are now a participant in the exclusive
✨ STAR EVENT – January Edition ✨

Use the buttons below to start your adventure and earn stars!
        """,
        reply_markup=dashboard_kb()
    )
# ============================================

# =============== DASHBOARD / USER ACTIONS =========
@router.message()
async def dashboard_handler(message: Message):
    uid = message.from_user.id
    text = message.text

    # ---------------- USER DASHBOARD ----------------
    if text == "🎯 Mission":
        await message.answer("🎯 Mission functionality coming soon.")
    elif text == "👥 Invite":
        await message.answer(
            f"👥 Your invite link:\nhttps://t.me/{(await bot.me()).username}?start={uid}"
        )
    elif text == "📊 My Chart":
        cursor.execute("SELECT referrals, coins, tasks_done FROM users WHERE user_id=?", (uid,))
        row = cursor.fetchone()
        referrals, coins, tasks = row if row else (0, 0, 0)
        await message.answer(
            f"📊 My Chart\n\n👥 Referrals: {referrals}\n⭐ Coins: {coins}\n🎯 Tasks Done: {tasks}"
        )
    elif text == "🏆 Leaderboard":
        cursor.execute("SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 10")
        rows = cursor.fetchall()
        text = "🏆 Top 10 Users\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            text += f"{medal} @{r[0]} — {r[1]} refs\n"
        await message.answer(text)
    elif text == "🎁 Gifts Info":
        await message.answer(
            "🎁 Star Gifts Info\n🥇 100 Stars for 1st\n🥈 50 Stars for 2nd\n🥉 25 Stars for 3rd"
        )

# ============================================

# =============== ADMIN COMMANDS ===============
@router.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    text = message.get_args()
    if not text:
        await message.reply("❌ Usage: /broadcast <message>")
        return
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    sent = 0
    for u in users:
        try:
            await bot.send_message(u[0], text)
            sent += 1
        except:
            pass
    await message.reply(f"✅ Broadcast sent to {sent} users.")

@router.message(Command("winners"))
async def winners(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    cursor.execute("SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 3")
    top = cursor.fetchall()
    medals = ["🥇", "🥈", "🥉"]
    text = "🎬 TOP 3 REFERRAL LEADERS\n\n"
    for i, u in enumerate(top):
        text += f"{medals[i]} @{u[0]} — {u[1]} referrals\n"
    await message.reply(text)

@router.message(Command("admine"))
async def admine(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    await message.reply(
        "👑 Admin Commands:\n"
        "/broadcast <msg> — send message to all users\n"
        "/winners — show top 3 referral users\n"
    )
# ============================================

# =============== RUN BOT ===============
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
