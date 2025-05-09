import os
import logging
import json
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize gspread with Google Sheets API
def init_gspread():
    # Define the scope for Google Sheets API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Load credentials from the GOOGLE_CRED_JSON environment variable
    google_cred_json = os.getenv("GOOGLE_CRED_JSON")
    if not google_cred_json:
        raise ValueError("The GOOGLE_CRED_JSON environment variable is required.")

    # Parse the JSON credentials from the environment variable
    creds_dict = json.loads(google_cred_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Enhanced /start command with multiple responses
async def start(update: Update, context):
    responses = [
        "Welcome to the SolarTrack Bot! 🌞 Use /help to see how I can assist you.",
        "Hello there! Ready to track your solar data? Type /help to get started.",
        "Hi! I'm your SolarTrack assistant. Use /help to explore what I can do for you!",
        "Greetings! 🌍 Need help with solar data? Type /help to learn more.",
        "Hey! I'm here to make solar tracking easier for you. Type /help to begin.",
        "Welcome aboard! 🚀 Use /help to see how I can help with your solar data.",
        "Hello, Earthling! 🌎 Ready to harness the power of the sun? Type /help to start.",
        "Hi there! ☀️ I'm here to help with your solar tracking needs. Use /help for guidance.",
        "Welcome to SolarTrack! 🔆 Curious about what I can do? Type /help to find out.",
        "Good day! 🌟 I'm your solar assistant. Use /help to unlock my potential."
    ]
    # Select a random response
    response = random.choice(responses)
    await update.message.reply_text(response)

# Command: /help
async def help_command(update: Update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/add <data> - Add a new row to the Google Sheet (comma-separated values).\n"
        "/get <row_number> - Retrieve data from a specific row.\n"
        "/update <row_number> <data> - Update a specific row with new data (comma-separated values)."
    )

# Command: /add
async def add_row(update: Update, context):
    try:
        # Extract the data from the user message
        data = ' '.join(context.args).split(',')
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        sheet.append_row(data)
        await update.message.reply_text("Row added successfully!")
    except Exception as e:
        logger.error(f"Error adding row: {e}")
        await update.message.reply_text("Failed to add row. Please try again.")

# Command: /get
async def get_row(update: Update, context):
    try:
        row_number = int(context.args[0])
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        row = sheet.row_values(row_number)
        await update.message.reply_text(f"Row {row_number}: {', '.join(row)}")
    except Exception as e:
        logger.error(f"Error retrieving row: {e}")
        await update.message.reply_text("Failed to retrieve row. Please provide a valid row number.")

# Command: /update
async def update_row(update: Update, context):
    try:
        row_number = int(context.args[0])
        new_data = ' '.join(context.args[1:]).split(',')
        gc = init_gspread()
        sheet = gc.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
        sheet.delete_row(row_number)
        sheet.insert_row(new_data, row_number)
        await update.message.reply_text(f"Row {row_number} updated successfully!")
    except Exception as e:
        logger.error(f"Error updating row: {e}")
        await update.message.reply_text("Failed to update row. Please provide valid inputs.")

# Flask route to handle Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Process updates from Telegram"""
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

def main():
    # Load Telegram bot token from environment variables
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is required.")

    # Set up the Telegram bot application
    global application  # Make application accessible in the webhook route
    application = Application.builder().token(TOKEN).build()

    # Add handlers to the bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_row))
    application.add_handler(CommandHandler("get", get_row))
    application.add_handler(CommandHandler("update", update_row))

    # Set webhook for Telegram updates
    webhook_url = "https://solartrak-bot.onrender.com/webhook"
    application.bot.set_webhook(webhook_url)

    # Run Flask app
    app.run(port=5000)

if __name__ == '__main__':
    main()