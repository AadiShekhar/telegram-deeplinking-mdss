import os
from telegram.ext import Updater, CommandHandler
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

# Authenticate Google Drive
def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # Open browser for first-time login
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")  # Save session
    return GoogleDrive(gauth)

drive = authenticate_google_drive()

# Mapping for MP3 file ranges
MDSS_MAP = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

# Function to fetch a file from Google Drive
def get_drive_file(file_name):
    query = f"'{GDRIVE_FOLDER_ID}' in parents and title = '{file_name}'"
    file_list = drive.ListFile({'q': query}).GetList()
    return file_list[0] if file_list else None

# Command Handler for /start
def start(update, context):
    chat_id = update.message.chat_id
    args = context.args

    if args and args[0] in MDSS_MAP:
        start_num, end_num = MDSS_MAP[args[0]]

        for num in range(start_num, end_num + 1):
            file_name = f"{num}.mp3"
            drive_file = get_drive_file(file_name)

            if drive_file:
                file_url = drive_file['webContentLink']  # Direct download link
                context.bot.send_audio(chat_id=chat_id, audio=file_url)
            else:
                context.bot.send_message(chat_id=chat_id, text=f"{file_name} not found in Drive.")
    else:
        context.bot.send_message(chat_id=chat_id, text="Invalid code or no code provided. Try again.")

# Function to run the bot
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start, pass_args=True))
    updater.start_polling()
    updater.idle()

# Flask App for Railway
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
