import os
import base64
import json
import tempfile
import logging
from flask import Flask
from telegram.ext import Updater, CommandHandler
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from threading import Thread

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Validate essential environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
if not GDRIVE_FOLDER_ID:
    raise ValueError("Please set the GDRIVE_FOLDER_ID environment variable")

# Function to authenticate with Google Drive using a service account
def get_google_drive():
    credentials_b64 = os.getenv("GDRIVE_CREDENTIALS")
    if not credentials_b64:
        raise ValueError("GDRIVE_CREDENTIALS environment variable is missing!")
    
    # Decode the Base64-encoded service account JSON
    credentials_json = base64.b64decode(credentials_b64).decode("utf-8")
    service_account_info = json.loads(credentials_json)
    
    # Set up PyDrive2 to use service account authentication
    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "service"
    gauth.settings["service_config"] = service_account_info
    gauth.ServiceAuth()  # Authenticate using the service account credentials
    drive = GoogleDrive(gauth)
    return drive

# Initialize Google Drive
drive = get_google_drive()

# Define the file ranges for each mdss command
MDSS_RANGES = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

# Helper function: retrieve a file by its exact name from the designated Drive folder
def get_drive_file(file_name):
    query = f"'{GDRIVE_FOLDER_ID}' in parents and title = '{file_name}'"
    file_list = drive.ListFile({'q': query}).GetList()
    return file_list[0] if file_list else None

# Telegram /start command handler.
# Usage: /start mdss1  → Sends files 1.mp3 to 100.mp3, etc.
def start(update, context):
    chat_id = update.message.chat_id
    args = context.args
    if not args or args[0] not in MDSS_RANGES:
        context.bot.send_message(chat_id=chat_id, text="Usage: /start mdss1 (or mdss2, mdss3, etc.)")
        return

    command = args[0]
    start_num, end_num = MDSS_RANGES[command]
    context.bot.send_message(chat_id=chat_id, text=f"Sending files {start_num}.mp3 to {end_num}.mp3...")

    # Loop through the desired file numbers and send each file
    for i in range(start_num, end_num + 1):
        file_name = f"{i}.mp3"
        drive_file = get_drive_file(file_name)
        if drive_file:
            local_path = f"/tmp/{file_name}"
            try:
                drive_file.GetContentFile(local_path)
                with open(local_path, "rb") as audio_file:
                    context.bot.send_audio(chat_id=chat_id, audio=audio_file, filename=file_name)
            except Exception as e:
                context.bot.send_message(chat_id=chat_id, text=f"Error sending {file_name}: {e}")
            finally:
                if os.path.exists(local_path):
                    os.remove(local_path)
        else:
            context.bot.send_message(chat_id=chat_id, text=f"File {file_name} not found.")

# Function to run the Telegram bot
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    # Add the /start command handler (which expects an argument like mdss1, mdss2, etc.)
    dp.add_handler(CommandHandler("start", start, pass_args=True))
    # Start polling (clean=True helps avoid conflicts if another instance was running)
    updater.start_polling(clean=True)
    updater.idle()

# Set up a Flask app for Railway (or any uptime monitoring)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    # Run Flask in a separate thread so that the Telegram bot runs in the main thread (required for signal handling)
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=8080))
    flask_thread.start()
    # Run the Telegram bot in the main thread
    run_bot()
