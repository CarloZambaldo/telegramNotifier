#!/usr/bin/env -S python3

import os
from dotenv import load_dotenv
import time
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from functools import wraps

"""
Telegram Bot for Raspberry Pi Management

This bot allows you to manage your Raspberry Pi remotely via Telegram.
Commands included:
- /start - Start the bot and receive a welcome message.
- /status - Get the current status of the Raspberry Pi.
- /photo - Send a test photo from the Raspberry Pi.
- /test - Test a new bot functionality.
- /super - Execute superuser commands like reboot or poweroff.
- /help - Display this help message.

"""

class App:
    def __init__(self, token: str, chat_id: str):
        self.chat_id = chat_id
        self.token = token
        self.start_time = time.time()
        self.bot_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # notify on startup
        self.send_message_to_owner("> raspi is online <")

        self.app = ApplicationBuilder().token(self.token).build()

        # adding command handlers
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()

        self.app.add_handler(CommandHandler("status", self.status), group=1)
        self.app.add_handler(CommandHandler("super", self.superuser), group=1)
        self.app.add_handler(CommandHandler("photo", self.send_photo), group=1)


    def run(self):
        self.app.run_polling()

    def restricted(func):
        @wraps(func)
        async def wrapped(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = str(update.effective_user.id)
            user_tag = str(update) or "<unknown>"
            allowed_id = str(self.chat_id)

            if user_id != allowed_id:
                self.send_message_to_owner("UNAUTHORIZED QUERY: {}".format(user_tag))
                await update.message.reply_text("❌ UNAUTHORIZED USER ❌")
                return
            return await func(self, update, context, *args, **kwargs)
        return wrapped

    def send_message_to_owner(self, message):
        data = {
            "chat_id": self.chat_id,
            "text": message
        }
        try:
            response = requests.post(self.bot_url, data=data)
            response.raise_for_status()
        except Exception as e:
            print(f"Errore nell'invio: {e}")

    ## Command Handlers ##
    @restricted
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = os.popen("uptime -p").read().strip()
        message = f'# RASPI STATUS #\n\nOnline\nUptime:\t{uptime}\n'
        await update.message.reply_text(message)

    @restricted
    async def send_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo_path = "./img/test.png"
        try:
            with open(photo_path, "rb") as photo_file:
                photo = InputFile(photo_file)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        except Exception as e:
            await update.message.reply_text(f"Errore invio immagine: {e}")

    @restricted
    # Comando /reboot → riavvia il sistema (opzionale, vedi sotto sicurezza)
    async def superuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        allowed_id = os.getenv("CHAT_ID")
        if str(update.effective_user.id) != allowed_id:
            await update.message.reply_text("❌ UNAUTHORIZED USER ❌")
            return
        
        if context.args[0].lower() == "reboot":
            if len(context.args) < 2 or context.args[1].lower() != "yes":
                await update.message.reply_text("⚠️ Confirm with: `/super reboot yes`", parse_mode="Markdown")
                return
            await update.message.reply_text("Rebooting the system...")
            os.system("sudo reboot")

        if context.args[0].lower() == "poweroff":
            if len(context.args) < 2  or context.args[1].lower() != "yes":
                await update.message.reply_text("⚠️ Confirm with: `/super poweroff yes`", parse_mode="Markdown")
                return
            await update.message.reply_text("Shutting down...")
            os.system("sudo poweroff")


# loading the application
if __name__ == "__main__":
    load_dotenv(dotenv_path=".env")

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    application = App(BOT_TOKEN, CHAT_ID)
    application.run()