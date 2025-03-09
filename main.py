import os
import json
import base64
from flask import Flask
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from telegram.ext import Updater, CommandHandler

# Load Google Drive Service Account Credentials
def authenticate_google_drive():
    creds_json = os.getenv("GDRIVE_CREDENTIALS")  # Base64 encoded JSON
    if not creds_json:
        raise ValueError("GDRIVE_CREDENTIALS environment variable is missing!")

    creds_path = "/tmp/service_account.json"
    with open(creds_path, "w") as f:
        f.write(base64.b64decode(creds_json).decode())

    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile(creds_path)
    drive = GoogleDrive(gauth)
    return drive

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Hello! Send /mdss1 to /mdss6 to receive MP3 files.")

def send_files(update, context):
    chat_id = update.message.chat_id
    command = update.message.text.strip()
    drive = authenticate_google_drive()

    # Define file ranges
    ranges = {
        "/mdss1": (1, 100),
        "/mdss2": (101, 200),
        "/mdss3": (201, 300),
        "/mdss4": (301, 400),
        "/mdss5": (401, 500),
        "/mdss6": (501, 600),
    }

    if command in ranges:
        start_num, end_num = ranges[command]
        query = f"title contains '.mp3'"
        file_list = drive.ListFile({'q': query}).GetList()

        found_files = [
            file for file in file_list
            if file["title"].endswith(".mp3") and start_num <= int(file["title"].split(".")[0]) <= end_num
        ]

        if found_files:
            for file in found_files:
                context.bot.send_document(chat_id=chat_id, document=file["downloadUrl"])
        else:
            context.bot.send_message(chat_id=chat_id, text="No files found in this range.")

def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    for cmd in ["/mdss1", "/mdss2", "/mdss3", "/mdss4", "/mdss5", "/mdss6"]:
        dp.add_handler(CommandHandler(cmd[1:], send_files))
    
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
