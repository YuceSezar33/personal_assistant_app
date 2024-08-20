import requests
import asyncio
import executor as exc
import logging
from telegram import Bot, ForceReply, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    Application,
)

from handlers.message_handler import meeting_entry

config = exc.get_telegram_config()
TELEGRAM_TOKEN = config['token']
CHAT_ID = config['chat_id']

# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! This is your bot.")
    context.user_data['started'] = True

# Handler for the /cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    context.user_data['started'] = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('started'):
        user_input = update.message.text
        message = f"did you just say {user_input}?"
        logging.info("are we here?")
        mes = meeting_entry(user_input)
        #await update.message.reply_text(f"{mes}")
        
        await send_message(mes)
    else:
        await update.message.reply_text("Please use /start to begin.")


async def send_message(message):
    # Create a Bot instance
    bot = Bot(token=TELEGRAM_TOKEN)
    # Send a message
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def start_bot():
    try:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        logging.getLogger('httpx').setLevel(logging.WARNING) # To avoid the flood of httpx info messages.

        app = Application.builder().token(TELEGRAM_TOKEN).build()
        # Add handlers to the Application
        app.add_handler(CommandHandler('cancel', cancel))
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.Text(), handle_message))
        logging.info("Starting the bot")

        await app.initialize()
        await app.start()
        await app.updater.start_polling()
    except Exception as e:
            logging.error(f"An error occurred in start_bot: {type(e).__name__} - {str(e)}")