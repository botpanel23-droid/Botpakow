import asyncio
import uuid
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

# ================= CONFIG =================
BOT_TOKEN = "8211519124:AAEG5NE2HI91ISvRtV50DzfGb71IM0KF030"
ADMIN_ID = 8452357204
CHANNEL_ID = -1001683128300

MEMEZ_CHANNEL = "https://t.me/Meme_Channel_SL"
MOVIE_CHANNEL = "https://t.me/Movie_Zone_Vip"

# ================= TEXT =================
CAPTION_TEXT = f"""😹😾😂

Join us :- {MEMEZ_CHANNEL}
Send Memez :- @Memez_Channel_Bot

#Funny_Picture
"""

WELCOME_TEXT = f"""
👋 <b>Hey There! Welcome to the Memez Zone</b> 😹🔥

📸 Photo | 🎥 Video | 🖼 Sticker
ඔයාගෙ Memez මෙතනට send කරන්න 😍

━━━━━━━━━━━━━━━
📢 <b>Memez Channel</b>
👉 {MEMEZ_CHANNEL}

🎬 <b>Movie Channel</b>
👉 {MOVIE_CHANNEL}
━━━━━━━━━━━━━━━

😹😾😂 <b>Send your Memez now</b>
"""

# ================= BOT =================
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# TEMP STORAGE (IMPORTANT)
MEME_STORE = {}

# ================= START =================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME_TEXT)

# ================= RECEIVE MEME =================
@dp.message(F.photo | F.video | F.sticker)
async def receive_meme(message: Message):

    meme_id = str(uuid.uuid4())

    if message.photo:
        MEME_STORE[meme_id] = ("photo", message.photo[-1].file_id)
    elif message.video:
        MEME_STORE[meme_id] = ("video", message.video.file_id)
    elif message.sticker:
        MEME_STORE[meme_id] = ("sticker", message.sticker.file_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"approve|{meme_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"reject|{meme_id}"
                )
            ]
        ]
    )

    await bot.send_message(
        ADMIN_ID,
        "🆕 <b>New Meme Submitted</b>",
        reply_markup=keyboard
    )

    # Send preview to admin
    if message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id)
    elif message.sticker:
        await bot.send_sticker(ADMIN_ID, message.sticker.file_id)

    await message.reply("✅ Meme sent for admin approval 😹🔥")

# ================= CALLBACK =================
@dp.callback_query()
async def callback_handler(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Not allowed", show_alert=True)
        return

    action, meme_id = call.data.split("|")

    if meme_id not in MEME_STORE:
        await call.message.edit_text("⚠️ Meme expired")
        return

    meme_type, file_id = MEME_STORE[meme_id]

    if action == "approve":
        if meme_type == "photo":
            await bot.send_photo(CHANNEL_ID, file_id, caption=CAPTION_TEXT)
        elif meme_type == "video":
            await bot.send_video(CHANNEL_ID, file_id, caption=CAPTION_TEXT)
        elif meme_type == "sticker":
            await bot.send_sticker(CHANNEL_ID, file_id)

        await call.message.edit_text("✅ Approved & Posted")
        del MEME_STORE[meme_id]

    elif action == "reject":
        await call.message.edit_text("❌ Meme Rejected")
        del MEME_STORE[meme_id]

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
