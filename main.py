from telegram.ext import Updater, CommandHandler
import os
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

# Define the message mapping for sending mp3 files
MDSS_MAP = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

MDSS_FOLDER = "mdss"  # Folder where mp3 files are stored

def start(update, context):
    chat_id = update.message.chat_id
    args = context.args  # Extract command arguments

    if args and args[0] in MDSS_MAP:
        start_num, end_num = MDSS_MAP[args[0]]

        for num in range(start_num, end_num + 1):
            file_path = os.path.join(MDSS_FOLDER, f"{num}.mp3")
            if os.path.exists(file_path):
                context.bot.send_audio(chat_id=chat_id, audio=open(file_path, "rb"))
            else:
                context.bot.send_message(chat_id=chat_id, text=f"File {num}.mp3 not found.")

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
