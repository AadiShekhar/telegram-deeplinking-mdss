import os
import base64
import tempfile
import logging
from flask import Flask
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import Updater, CommandHandler

# ✅ Enable logging
logging.basicConfig(level=logging.INFO)

# ✅ Google Drive Authentication
def get_google_drive():
    credentials_b64 = os.getenv("GDRIVE_CREDENTIALS")
    if not credentials_b64:
        raise ValueError("⚠️ GDRIVE_CREDENTIALS environment variable is missing!")

    # Convert Base64 to JSON
    credentials_json = base64.b64decode(credentials_b64).decode('utf-8')

    # Write to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(credentials_json.encode())
        temp_credentials_path = temp_file.name

    try:
        gauth = GoogleAuth()
        scope = ["https://www.googleapis.com/auth/drive"]
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(temp_credentials_path, scope)
        return GoogleDrive(gauth)

    except Exception as e:
        logging.error(f"⚠️ Google Drive Authentication Failed: {e}")
        raise

# ✅ Initialize Google Drive
drive = get_google_drive()

# ✅ Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

# ✅ File Ranges for `/mdssX` Commands
MDSS_RANGES = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

# ✅ Start Command
def start(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Welcome! Use /mdss1 to /mdss6 to receive MP3 files.")

# ✅ Function to Send MP3 Files
def send_files(update, context):
    chat_id = update.message.chat_id
    command = update.message.text.strip().lstrip("/")
    
    if command not in MDSS_RANGES:
        context.bot.send_message(chat_id=chat_id, text="Invalid command. Use /mdss1 to /mdss6.")
        return
    
    start_num, end_num = MDSS_RANGES[command]

    # ✅ Query Google Drive for MP3 files in range
    query = f"'{os.getenv('GDRIVE_FOLDER_ID')}' in parents and mimeType='audio/mpeg'"
    file_list = drive.ListFile({'q': query}).GetList()

    found_files = [
        file for file in file_list
        if file["title"].endswith(".mp3") and start_num <= int(file["title"].split(".")[0]) <= end_num
    ]

    if found_files:
        for file in found_files:
            context.bot.send_document(chat_id=chat_id, document=file["downloadUrl"])
    else:
        context.bot.send_message(chat_id=chat_id, text="No MP3 files found in this range.")

# ✅ Run Telegram Bot
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    for cmd in MDSS_RANGES.keys():
        dp.add_handler(CommandHandler(cmd, send_files))
    
    updater.start_polling()
    updater.idle()

# ✅ Flask App for Railway
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
