import asyncio
import aiohttp
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime

# ================= CONFIG =================
BOT_TOKEN = "7988776219:AAETqzJOvOFNc2904BkOhMAu8UDLU7QV2E4"
CHANNEL_ID = "@Binanse_Auto_news_update_Sl"  # Telegram channel username or ID
DEFAULT_IMAGE = "https://files.catbox.moe/s3z235.jpg"
FOOTER_TEXT = "Join Us:- https://t.me/Binanse_Auto_news_update_Sl"
NEWS_FEED_URL = "https://www.binance.com/en/support/announcement/c-48?navId=48"  # Binance official announcements

# ================= DB =================
conn = sqlite3.connect("posted_news.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS posted_news (
    news_id TEXT PRIMARY KEY
)
""")
conn.commit()

# ================= BOT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= GLOBALS =================
bot_running = False
post_image = DEFAULT_IMAGE

# ================= FUNCTIONS =================
async def fetch_binance_news():
    async with aiohttp.ClientSession() as session:
        async with session.get(NEWS_FEED_URL) as resp:
            if resp.status == 200:
                data = await resp.text()
                return data
            return None

# Dummy parser: implement proper parsing from Binance page / RSS
def parse_news(html_text):
    """
    Parse latest news from HTML or RSS feed.
    Returns list of dicts: [{'id': '1234', 'title': 'New Coin Listing XYZ', 'desc': 'Trading starts ...', 'link': 'https://...'}]
    """
    # For demo, return a fake single news
    news_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return [{
        "id": news_id,
        "title": "New Coin Listing: XYZ",
        "desc": "Trading starts today on Binance spot market.",
        "link": "https://www.binance.com/en/trade/XYZ"
    }]

async def post_news(news_item):
    # Check duplicate
    c.execute("SELECT news_id FROM posted_news WHERE news_id=?", (news_item['id'],))
    if c.fetchone():
        return
    # Format message
    msg_text = f"🚨 BINANCE OFFICIAL UPDATE 🚨\n\n📰 {news_item['title']}\n💡 {news_item['desc']}\n📌 More info: {news_item['link']}\n\n{FOOTER_TEXT}"
    # Send photo + caption
    await bot.send_photo(chat_id=CHANNEL_ID, photo=post_image, caption=msg_text)
    # Save to DB
    c.execute("INSERT INTO posted_news (news_id) VALUES (?)", (news_item['id'],))
    conn.commit()

async def news_loop():
    global bot_running
    while bot_running:
        html = await fetch_binance_news()
        if html:
            news_list = parse_news(html)
            for news in news_list:
                await post_news(news)
        await asyncio.sleep(120)  # check every 2 minutes

# ================= ADMIN COMMANDS =================
@dp.message(Command("startbot"))
async def cmd_startbot(message: types.Message):
    global bot_running
    if bot_running:
        await message.reply("Bot is already running!")
    else:
        bot_running = True
        asyncio.create_task(news_loop())
        await message.reply("Bot started posting Binance news!")

@dp.message(Command("stopbot"))
async def cmd_stopbot(message: types.Message):
    global bot_running
    bot_running = False
    await message.reply("Bot stopped posting.")

@dp.message(Command("setimage"))
async def cmd_setimage(message: types.Message):
    global post_image
    args = message.get_args()
    if not args:
        await message.reply("Usage: /setimage <image_url>")
        return
    post_image = args
    await message.reply(f"Post image updated to: {post_image}")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    global bot_running
    status = "running" if bot_running else "stopped"
    await message.reply(f"Bot status: {status}\nCurrent image: {post_image}")

# ================= RUN BOT =================
if __name__ == "__main__":
    print("Bot is starting...")
    asyncio.run(dp.start_polling(bot))
