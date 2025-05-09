import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize gspread with Google Sheets API
def init_gspread():
    # Define the scope for Google Sheets API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Load credentials from the service account JSON file
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google_sheets_credentials.json", scope
    )
    return gspread.authorize(creds)

# Command: /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Google Sheets Bot! Use /help to see available commands."
    )

# Command: /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Available commands:\n"
        "/add <data> - Add a new row to the Google Sheet (comma-separated values).\n"
        "/get <row_number> - Retrieve data from a specific row.\n"
        "/update <row_number> <data> - Update a specific row with new data (comma-separated values)."
    )

# Command: /add
def add_row(update: Update, context: CallbackContext) -> None:
    try:
        # Extract the data from the user message
        data = ' '.join(context.args).split(',')
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        sheet.append_row(data)
        update.message.reply_text("Row added successfully!")
    except Exception as e:
        logger.error(f"Error adding row: {e}")
        update.message.reply_text("Failed to add row. Please try again.")

# Command: /get
def get_row(update: Update, context: CallbackContext) -> None:
    try:
        row_number = int(context.args[0])
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        row = sheet.row_values(row_number)
        update.message.reply_text(f"Row {row_number}: {', '.join(row)}")
    except Exception as e:
        logger.error(f"Error retrieving row: {e}")
        update.message.reply_text("Failed to retrieve row. Please provide a valid row number.")

# Command: /update
def update_row(update: Update, context: CallbackContext) -> None:
    try:
        row_number = int(context.args[0])
        new_data = ' '.join(context.args[1:]).split(',')
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        sheet.delete_row(row_number)
        sheet.insert_row(new_data, row_number)
        update.message.reply_text(f"Row {row_number} updated successfully!")
    except Exception as e:
        logger.error(f"Error updating row: {e}")
        update.message.reply_text("Failed to update row. Please provide valid inputs.")

def main():
    # Load the Telegram bot token from environment variables
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is required.")

    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add_row))
    dispatcher.add_handler(CommandHandler("get", get_row))
    dispatcher.add_handler(CommandHandler("update", update_row))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()