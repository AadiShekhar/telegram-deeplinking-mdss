import os
import base64
import tempfile
import logging
from flask import Flask
from telegram.ext import Updater, CommandHandler
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Validate environment variables
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
    
    # Decode the Base64 string to obtain the JSON credentials
    credentials_json = base64.b64decode(credentials_b64).decode("utf-8")
    
    # Write the JSON credentials to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(credentials_json.encode())
        temp_credentials_path = temp_file.name

    # Authenticate using the service account credentials
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(temp_credentials_path, scope)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)
    return drive

# Initialize Google Drive
drive = get_google_drive()

# Helper function to get a file by its exact name from the specified folder
def get_drive_file(file_name):
    query = f"'{GDRIVE_FOLDER_ID}' in parents and title = '{file_name}'"
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]
    return None

# Mapping for commands: mdss1 sends files 1.mp3 to 100.mp3, mdss2 sends 101.mp3 to 200.mp3, etc.
MDSS_RANGES = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

# /start command handler
# Usage: /start mdss1  (or mdss2, mdss3, etc.)
def start(update, context):
    chat_id = update.message.chat_id
    args = context.args
    if not args or args[0] not in MDSS_RANGES:
        context.bot.send_message(chat_id=chat_id, text="Usage: /start mdss1 (or mdss2, mdss3, etc.)")
        return
    
    command = args[0]
    start_num, end_num = MDSS_RANGES[command]
    context.bot.send_message(chat_id=chat_id, text=f"Sending files {start_num}.mp3 to {end_num}.mp3...")

    # Loop through the specified range and send each file
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
    dp.add_handler(CommandHandler("start", start, pass_args=True))
    updater.start_polling()
    updater.idle()

# Flask app (for Railway uptime pings)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
