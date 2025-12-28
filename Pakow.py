import asyncio
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
from aiogram.enums import ParseMode

# ================= CONFIG =================
BOT_TOKEN = "8488957878:AAHxqi_KRoErGQnKjVl-8qOtOWiEmtaWlrE"

CHANNELS = [
    "@Quote_Pro_Sl",
    "@your_channel_2"
]

POST_INTERVAL = 1200  # 20 minutes
FONT_PATH = "NotoSansSinhala-Bold.ttf"  # Sinhala font file
IMAGE_SIZE = (800, 800)
BACKGROUND_COLORS = [(255, 228, 225), (224, 255, 255), (240, 255, 240), (255, 250, 205)]
# ==========================================

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

# -------- Quote Line Banks --------
LINE1 = [
    "ජීවිතේ හැම දවසක්ම",
    "කාලය අපිට කියලා දෙන්නේ",
    "සාර්ථකත්වය කියන්නේ",
    "ඔයාගේ හිත ඇතුලේ",
    "අද දවස කියන්නේ"
]

LINE2 = [
    "අපි නොදකින අර්ථයක් තියෙනවා",
    "අපිව වෙනස් කරන මොහොතක්",
    "ඉවසීම පරීක්ෂා වෙන වෙලාවක්",
    "නව ආරම්භයක් ලඟා වෙන තැනක්"
]

LINE3 = [
    "අද කරන පොඩි උත්සාහය",
    "නවතින්නේ නැති හිතක්",
    "අතහැර නොයන සිහිනක්",
    "විශ්වාසයෙන් ගත්ත පියවරක්"
]

LINE4 = [
    "හෙට ලොකු ජයග්‍රහණයක් වෙනවා",
    "ඔයාගේ ජීවිතය සම්පූර්ණයෙන් වෙනස් කරයි",
    "අනාගතය ලස්සන කරලා දමයි",
    "කාලයත් එක්ක අගය දෙනවා"
]

EMOJIS = ["✨", "🔥", "💫", "🌱", "💭", "❤️"]

HASHTAGS = [
    "#Motivation",
    "#LifeQuotes",
    "#Mindset",
    "#Success",
    "#DailyQuote",
    "#PositiveVibes"
]

USED_QUOTES = set()

# -------- Quote Generator --------
def generate_quote():
    while True:
        quote = (
            f"{random.choice(LINE1)}\n"
            f"{random.choice(LINE2)}\n\n"
            f"{random.choice(LINE3)}\n"
            f"{random.choice(LINE4)}"
        )
        if quote not in USED_QUOTES:
            USED_QUOTES.add(quote)
            return quote

# -------- Image Generator --------
def create_quote_image(quote):
    bg_color = random.choice(BACKGROUND_COLORS)
    image = Image.new("RGB", IMAGE_SIZE, color=bg_color)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(FONT_PATH, 36)
    except:
        font = ImageFont.load_default()

    lines = quote.split("\n")
    y_text = 50
    for line in lines:
        w, h = draw.textsize(line, font=font)
        draw.text(((IMAGE_SIZE[0]-w)/2, y_text), line, font=font, fill=(0,0,0))
        y_text += h + 20

    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

# -------- Auto Poster --------
async def auto_post():
    print("🤖 Ultimate Quote + Image Bot Started (20 min / 2 channels)")

    while True:
        try:
            quote = generate_quote()
            emoji = random.choice(EMOJIS)
            tags = " ".join(random.sample(HASHTAGS, 3))
            caption = f"{emoji} <b>{quote}</b>\n\n{tags}"

            image_bytes = create_quote_image(quote)

            for channel in CHANNELS:
                await bot.send_photo(channel, photo=image_bytes, caption=caption, parse_mode=ParseMode.HTML)

            print("✅ Quote image sent to all channels")

        except Exception as e:
            print("⚠️ Error:", e)

        await asyncio.sleep(POST_INTERVAL)

# -------- Runner --------
async def main():
    while True:
        try:
            await auto_post()
        except Exception as e:
            print("♻️ Restarting bot loop:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
