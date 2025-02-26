from telegram.ext import Updater, CommandHandler
import os
import time
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

MESSAGE_MAP = {
    "mvs100": [
        os.getenv("MVS100_MESSAGE", "Message not configured"),
        "⚠️ Deleting in 9 hours",
    ],
    "mvs200": [
        "🚀 Welcome to MVS200! Start your journey here.",
        "📝 Important instructions: Follow step 1, 2, and 3.",
        "🎯 Good luck on your mission!"
    ],
    "deepseek": [
        "deepseek dark icon download high quality by No Headphone Gamerz",
        {"type": "photo", "file": "IMG_20250226_141147_673.jpg"},
        "⚠️ Deleting in 9 hours"
    ]
}

def delete_messages(context):
    try:
        job_data = context.job.context
        chat_id = job_data["chat_id"]
        message_ids = job_data["message_ids"]
        
        for message_id in message_ids:
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass
    except Exception:
        pass

def start(update, context):
    chat_id = update.message.chat_id
    args = context.args
    if args and args[0] in MESSAGE_MAP:
        messages = MESSAGE_MAP[args[0]]
        message_ids = []
        
        for msg in messages:
            if isinstance(msg, dict) and msg["type"] == "photo":
                with open(msg["file"], 'rb') as photo:
                    sent_message = context.bot.send_photo(chat_id=chat_id, photo=photo)
            else:
                sent_message = context.bot.send_message(chat_id=chat_id, text=msg)
            message_ids.append(sent_message.message_id)
        
        context.job_queue.run_once(delete_messages, 32400, context={"chat_id": chat_id, "message_ids": message_ids})
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
