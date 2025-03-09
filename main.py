import os
import json
import base64
import tempfile
import logging
from flask import Flask
from telegram.ext import Updater, CommandHandler
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ✅ Enable logging
logging.basicConfig(level=logging.INFO)

# ✅ Load Telegram bot token from env
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("⚠️ Please set the BOT_TOKEN environment variable!")

# ✅ Decode Google Service Account from Base64
def get_google_drive():
    credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
    if not credentials_b64:
        raise ValueError("⚠️ GOOGLE_CREDENTIALS_B64 is not set!")

    # Convert Base64 to JSON
    credentials_json = base64.b64decode(credentials_b64).decode('utf-8')

    # Write to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(credentials_json.encode())
        temp_credentials_path = temp_file.name

    # ✅ Authenticate with Google Drive
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(temp_credentials_path)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile(temp_credentials_path)
    
    return GoogleDrive(gauth)

drive = get_google_drive()  # Initialize Google Drive

# ✅ Flask app for Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Bot is running!"

# ✅ Command to fetch `.mp3` files
def send_files(update, context):
    chat_id = update.message.chat_id
    args = context.args

    if not args or not args[0].startswith("mdss"):
        context.bot.send_message(chat_id=chat_id, text="⚠️ Invalid command. Use /start mdss1 to /start mdss6")
        return

    try:
        # ✅ Extract number from "mdss1" to "mdss6"
        num = int(args[0].replace("mdss", ""))
        start_range = (num - 1) * 100 + 1
        end_range = num * 100

        context.bot.send_message(chat_id=chat_id, text=f"🔍 Searching for files {start_range}.mp3 to {end_range}.mp3...")

        # ✅ Search & send files from Google Drive
        query = f"title contains '.mp3'"
        file_list = drive.ListFile({'q': query}).GetList()

        for file in file_list:
            file_name = file['title']
            try:
                file_num = int(file_name.replace(".mp3", ""))
                if start_range <= file_num <= end_range:
                    file.GetContentFile(file_name)
                    context.bot.send_audio(chat_id=chat_id, audio=open(file_name, 'rb'))
            except ValueError:
                continue  # Skip non-matching files

    except Exception as e:
        logging.error(f"Error: {e}")
        context.bot.send_message(chat_id=chat_id, text="⚠️ Something went wrong.")

# ✅ Start Telegram bot
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", send_files, pass_args=True))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
