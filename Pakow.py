import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

# ========== CONFIG ==========
BOT_TOKEN = "8211519124:AAEG5NE2HI91ISvRtV50DzfGb71IM0KF030"
ADMIN_ID = 8452357204
CHANNEL_ID = -1001683128300

MEMEZ_CHANNEL = "https://t.me/Meme_Channel_SL"
MOVIE_CHANNEL = "https://t.me/Movie_Zone_Vip"

CAPTION_TEXT = f"""😹😾😂

Join us :- {MEMEZ_CHANNEL}
Send Memez :- @Memez_Channel_Bot

#Funny_Picture
"""

WELCOME_TEXT = f"""
👋 <b>Hey There! Welcome to the Memez Zone</b> 😹🔥

ඔයාට තියෙන්නෙ ඔයාගෙ ලස්සන Memez
📸 Photo | 🎥 Video | 🖼 Sticker
මෙතනට send කරන්න 😍

😂 Best & Funny Memez
🎯 Daily Entertainment
💥 Sri Lanka Meme Hub

━━━━━━━━━━━━━━━
📢 <b>Memez Channel</b> :-
👉 {MEMEZ_CHANNEL}

🎬 <b>Movie Channel</b> :-
👉 {MOVIE_CHANNEL}
━━━━━━━━━━━━━━━

😹😾😂 <b>Send your Memez now & make everyone laugh</b> 😂🔥
"""

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ========== START ==========
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(WELCOME_TEXT)

# ========== RECEIVE MEME ==========
@dp.message(F.photo | F.video | F.sticker)
async def receive_meme(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"approve_{message.message_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"reject_{message.message_id}"
                )
            ]
        ]
    )

    await message.forward(ADMIN_ID)
    await bot.send_message(
        ADMIN_ID,
        "🆕 <b>New Meme Submission</b>",
        reply_markup=keyboard
    )

    await message.reply("✅ Meme sent for admin review 😹🔥")

# ========== CALLBACK ==========
@dp.callback_query()
async def callback_handler(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Not allowed", show_alert=True)
        return

    action, msg_id = call.data.split("_")
    replied = call.message.reply_to_message

    if not replied:
        await call.message.edit_text("⚠️ Original meme not found")
        return

    if action == "approve":
        if replied.photo:
            await bot.send_photo(
                CHANNEL_ID,
                replied.photo[-1].file_id,
                caption=CAPTION_TEXT
            )
        elif replied.video:
            await bot.send_video(
                CHANNEL_ID,
                replied.video.file_id,
                caption=CAPTION_TEXT
            )
        elif replied.sticker:
            await bot.send_sticker(
                CHANNEL_ID,
                replied.sticker.file_id
            )

        await call.message.edit_text("✅ Approved & Posted to Channel")

    elif action == "reject":
        await call.message.edit_text("❌ Meme Rejected")

# ========== RUN ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
