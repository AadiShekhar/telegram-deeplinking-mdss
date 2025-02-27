from telegram.ext import Updater, CommandHandler
import os
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

MESSAGE_MAP = {
    "mvs100": [
        os.getenv("MVS100_MESSAGE", "Message not configured"),
    ],
    "mvs200": [
        "🚀 Welcome to MVS200! Start your journey here.",
        "📝 Important instructions: Follow step 1, 2, and 3.",
        "🎯 Good luck on your mission!"
    ],
    "deepseek": [
        "deepseek dark icon download high quality by No Headphone Gamerz",
        {"type": "photo", "file": "IMG_20250226_141147_673.jpg"},
    ]
}

def start(update, context):
    chat_id = update.message.chat_id
    args = context.args
    if args and args[0] in MESSAGE_MAP:
        messages = MESSAGE_MAP[args[0]]

        for msg in messages:
            if isinstance(msg, dict) and msg["type"] == "photo":
                with open(msg["file"], 'rb') as photo:
                    context.bot.send_photo(chat_id=chat_id, photo=photo)
            else:
                context.bot.send_message(chat_id=chat_id, text=msg)
    else:
        context.bot.send_message(chat_id=chat_id, text="Invalid code or no code provided. Try again.")

def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, pass_args=True))
    updater.start_polling()
    updater.idle()

# Flask app for Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
