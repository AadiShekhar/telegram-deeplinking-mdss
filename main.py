import os
import base64
import json
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Load Google Drive credentials from Base64
def authenticate_google_drive():
    credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
    if not credentials_b64:
        raise ValueError("GOOGLE_CREDENTIALS_B64 environment variable is missing")

    credentials_json = base64.b64decode(credentials_b64).decode("utf-8")
    temp_credentials_path = "/tmp/credentials.json"

    with open(temp_credentials_path, "w") as f:
        f.write(credentials_json)

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(temp_credentials_path)
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

drive = authenticate_google_drive()

# Bot Token & Admin Chat ID
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Fetch files from Google Drive based on range
def get_files_from_drive(start, end):
    query = f"title contains '.mp3'"
    file_list = drive.ListFile({'q': query}).GetList()
    
    matched_files = [
        f for f in file_list if f["title"].endswith(".mp3")
        and start <= int(f["title"].split(".")[0]) <= end
    ]
    
    return matched_files

# Command to send MP3s based on range
def send_files(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id != ADMIN_ID:
        return  # Ignore non-admin users

    args = context.args
    if not args or not args[0].isdigit():
        context.bot.send_message(chat_id=chat_id, text="Usage: /start mdss1 - mdss6")
        return

    range_map = {
        "mdss1": (1, 100),
        "mdss2": (101, 200),
        "mdss3": (201, 300),
        "mdss4": (301, 400),
        "mdss5": (401, 500),
        "mdss6": (501, 600),
    }

    key = args[0].lower()
    if key not in range_map:
        context.bot.send_message(chat_id=chat_id, text="Invalid code. Use mdss1 - mdss6.")
        return

    start, end = range_map[key]
    files = get_files_from_drive(start, end)

    if not files:
        context.bot.send_message(chat_id=chat_id, text=f"No files found for {key}.")
        return

    for file in files:
        file.GetContentFile(file["title"])
        with open(file["title"], "rb") as f:
            context.bot.send_audio(chat_id=chat_id, audio=f)
        os.remove(file["title"])

# Telegram Bot Setup
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", send_files, pass_args=True))
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
