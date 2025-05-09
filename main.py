import os
import json
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets authentication
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds_json = os.getenv("GOOGLE_CREDS_JSON")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open your Google Sheet
sheet = client.open("OrderTracking").sheet1  # Change to your sheet name

# Telegram bot Token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to SolarBot! Send /track <order_id> to track your order.")

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide an order ID. Example: /track 12345")
        return

    order_id = context.args[0]
    data = sheet.get_all_records()

    for row in data:
        if str(row.get("Order ID")) == order_id:
            status = row.get("Status", "Unknown")
            await update.message.reply_text(f"Order {order_id} status: {status}")
            return

    await update.message.reply_text("Order not found.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("track", track))
    app.run_polling()
