import os
import logging
import tempfile
from flask import Flask
from telegram.ext import Updater, CommandHandler
from mega import Mega
from threading import Thread

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Validate required environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set the BOT_TOKEN environment variable")

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")
if not MEGA_EMAIL or not MEGA_PASSWORD:
    raise ValueError("Please set the MEGA_EMAIL and MEGA_PASSWORD environment variables")

MEGA_FOLDER_ID = os.getenv("MEGA_FOLDER_ID")
if not MEGA_FOLDER_ID:
    raise ValueError("Please set the MEGA_FOLDER_ID environment variable")

# Authenticate with MEGA
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# Define file ranges for mdss commands.
# For example, "mdss1" sends files 1.mp3 to 100.mp3, "mdss2" sends 101.mp3 to 200.mp3, etc.
MDSS_RANGES = {
    "mdss1": (1, 100),
    "mdss2": (101, 200),
    "mdss3": (201, 300),
    "mdss4": (301, 400),
    "mdss5": (401, 500),
    "mdss6": (501, 600),
}

def get_mega_file(file_name):
    """
    Searches for a file by name using MEGA's built-in find method.
    Optionally checks that the file is in the designated folder.
    """
    node = m.find(file_name, exclude_deleted=True)
    if node:
        # Uncomment the next lines if you want to enforce that the file is in the specified folder:
        # if node.get("p") == MEGA_FOLDER_ID:
        #     return node
        # else:
        #     logging.info("Found file %s but folder id does not match: found %s vs expected %s", 
        #                  file_name, node.get("p"), MEGA_FOLDER_ID)
        return node
    else:
        logging.info("File %s not found via m.find()", file_name)
    return None

def start(update, context):
    chat_id = update.message.chat_id
    args = context.args
    if not args or args[0] not in MDSS_RANGES:
        context.bot.send_message(chat_id=chat_id,
            text="Usage: /start mdss1 (or mdss2, mdss3, etc.)")
        return

    command = args[0]
    start_num, end_num = MDSS_RANGES[command]
    context.bot.send_message(chat_id=chat_id,
        text=f"Sending files {start_num}.mp3 to {end_num}.mp3...")

    # Loop through the expected file numbers and send each file.
    for i in range(start_num, end_num + 1):
        file_name = f"{i}.mp3"
        mega_file = get_mega_file(file_name)
        if mega_file:
            local_path = f"/tmp/{file_name}"
            try:
                # Download the file from MEGA to the local /tmp directory.
                m.download(mega_file, dest_path="/tmp")
                with open(local_path, "rb") as audio_file:
                    context.bot.send_audio(chat_id=chat_id, audio=audio_file, filename=file_name)
            except Exception as e:
                context.bot.send_message(chat_id=chat_id,
                    text=f"Error sending {file_name}: {e}")
            finally:
                if os.path.exists(local_path):
                    os.remove(local_path)
        else:
            context.bot.send_message(chat_id=chat_id,
                text=f"File {file_name} not found on MEGA.")

def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    # Single /start command handler expecting an argument like mdss1
    dp.add_handler(CommandHandler("start", start, pass_args=True))
    updater.start_polling(clean=True)
    updater.idle()

# Flask app for uptime monitoring (e.g., Railway)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    # Run Flask in a separate thread so the Telegram bot can run in the main thread.
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    run_bot()
