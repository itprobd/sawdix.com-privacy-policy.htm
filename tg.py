import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = "8392938310:AAEWmjx_8cKkiPouCb4-uKC-M2cGz_XC0v8"

DIVISIONS = {
    "dhaka": "Dhaka",
    "chattogram": "Chittagong",
    "rajshahi": "Rajshahi",
    "khulna": "Khulna",
    "barishal": "Barisal",
    "sylhet": "Sylhet",
    "rangpur": "Rangpur",
    "mymensingh": "Mymensingh"
}

scheduler = BackgroundScheduler()
scheduler.start()

def get_prayer_times(city):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Bangladesh&method=1"
    response = requests.get(url).json()
    return response["data"]["timings"]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📍 Dhaka", callback_data="dhaka")],
        [InlineKeyboardButton("📍 Chattogram", callback_data="chattogram")],
        [InlineKeyboardButton("📍 Rajshahi", callback_data="rajshahi")],
        [InlineKeyboardButton("📍 Khulna", callback_data="khulna")],
        [InlineKeyboardButton("📍 Barishal", callback_data="barishal")],
        [InlineKeyboardButton("📍 Sylhet", callback_data="sylhet")],
        [InlineKeyboardButton("📍 Rangpur", callback_data="rangpur")],
        [InlineKeyboardButton("📍 Mymensingh", callback_data="mymensingh")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌙 Ramadan Tracker BD\n\n"
        "আপনার বিভাগ নির্বাচন করুন:\n\n"
        "──────────────\n"
        "POWER BY : FARHAN",
        reply_markup=reply_markup
    )

# Button click
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    division_key = query.data
    city = DIVISIONS[division_key]
    timings = get_prayer_times(city)

    message = f"""
🌙 Ramadan Tracker BD

📍 বিভাগ: {city}

🌅 সেহরি শেষ: {timings['Fajr']}
🌇 ইফতার: {timings['Maghrib']}

🕌 নামাজের সময়:
ফজর: {timings['Fajr']}
যোহর: {timings['Dhuhr']}
আসর: {timings['Asr']}
মাগরিব: {timings['Maghrib']}
এশা: {timings['Isha']}

──────────────
POWER BY : FARHAN
    """

    await query.edit_message_text(message)

    chat_id = query.message.chat_id
    schedule_prayers(context.application, chat_id, city)

async def send_prayer_reminder(application, chat_id, prayer_name):
    await application.bot.send_message(
        chat_id=chat_id,
        text=f"🕌 এখন {prayer_name} এর সময় হয়েছে!\n\nPOWER BY : FARHAN"
    )

def schedule_prayers(application, chat_id, city):
    timings = get_prayer_times(city)

    for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        time_str = timings[prayer]
        hour, minute = map(int, time_str.split(":")[:2])

        scheduler.add_job(
            send_prayer_reminder,
            'cron',
            hour=hour,
            minute=minute,
            args=[application, chat_id, prayer],
            id=f"{chat_id}_{prayer}",
            replace_existing=True
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

print("Ramadan Tracker BD 🌙 Running...")
app.run_polling()