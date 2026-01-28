import io
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ======= تنظیمات توکن و API =======
TELEGRAM_TOKEN = "8274627721:AAFNlN1jNxBjHRdK4K4MNhBTLxBQJExSz9I"
WEATHER_API_KEY = "9adced7ddff5c6dc7f031455d3dec00e"

# ======= شهرها =======
CITIES = {
    "تهران": "Tehran,IR",
    "اصفهان": "Isfahan,IR",
    "شیراز": "Shiraz,IR",
    "آلمان": "Berlin,DE",
    "فرانسه": "Paris,FR",
    "ترکیه": "Istanbul,TR"
}

# ======= استارت ربات =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(city, callback_data=city)] for city in CITIES.keys()
    ]
    keyboard.append([InlineKeyboardButton("دیگه شهر می‌خوام بنویسم", callback_data="manual")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "سلام! یه شهر انتخاب کن یا اگه خواستی اسمشو خودت بنویس:",
        reply_markup=reply_markup
    )

# ======= هندل دکمه‌ها =======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    city_name = query.data
    if city_name == "manual":
        await query.message.reply_text("اسم شهر رو برام بنویس:")
    else:
        await send_weather(query.message, CITIES[city_name])

# ======= هندل متن وارد شده =======
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_text = update.message.text
    if city_text in CITIES:
        await send_weather(update.message, CITIES[city_text])
    else:
        await update.message.reply_text("متأسفم، این شهر داخل لیست ما نیست.")

# ======= ارسال وضعیت هوا =======
async def send_weather(source, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    response = requests.get(url).json()
    
    if response.get("cod") != 200:
        await source.reply_text("نتونستم وضعیت هوا رو پیدا کنم 😢")
        return

    weather = response["weather"][0]["description"]
    temp = response["main"]["temp"]
    humidity = response["main"]["humidity"]
    wind = response["wind"]["speed"]

    text = f"🌤 وضعیت هوا برای {city}:\n" \
           f"وضعیت: {weather}\n" \
           f"دما: {temp}°C\n" \
           f"رطوبت: {humidity}%\n" \
           f"سرعت باد: {wind} m/s"

    # عکس ساده از آیکون هوا
    icon_code = response["weather"][0]["icon"]
    img_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    img_data = requests.get(img_url).content
    bio = io.BytesIO(img_data)
    bio.name = "weather.png"
    bio.seek(0)

    await source.reply_photo(photo=bio, caption=text)

# ======= ساخت اپلیکیشن و هندلرها =======
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("ربات آماده است...")
app.run_polling()
