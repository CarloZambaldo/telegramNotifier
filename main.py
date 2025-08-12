#!/usr/bin/env -S python3

"""Telegram bot for Raspberry Pi management.

The bot exposes a small set of commands that allow a user to interact with a
Raspberry Pi.  Features include:

* Live photo capture from an attached USB camera.
* System status information such as uptime, disk usage and CPU temperature.
* Basic GPIO control (LED on/off).
* Periodic updates of the top running processes.
* Ability to start external scripts and interact with them via the chat.

Only one authorised chat ID may interact with the bot.  The ID and bot token
are read from the ``.env`` file.
"""

import asyncio
import os
import time
import socket

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# Try to import GPIO support.  If not available (e.g. when not running on a
# Raspberry Pi) we silently disable GPIO features.
try:  # pragma: no cover - requires hardware
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    LED_PIN = 17
    GPIO.setup(LED_PIN, GPIO.OUT)
except Exception:  # pragma: no cover - gracefully handle missing hardware
    GPIO = None
    LED_PIN = None

from modules.send_message_to_owner import send_message_to_owner
from modules.cpu_temp import _cpu_temp
from modules.status import status
from modules.send_photo import send_photo
from modules.led import led
from modules.run_script import run_script
from modules.forward_output import _forward_output
from modules.handle_process_input import handle_process_input
from modules.superuser import superuser
from modules.process_report import process_report


class App:
    """Main application class for the Telegram bot."""

    def __init__(self, token: str, chat_id: str) -> None:
        self.chat_id = chat_id
        self.token = token
        self.start_time = time.time()
        self.bot_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.active_process: asyncio.subprocess.Process | None = None
        self.GPIO = GPIO
        self.LED_PIN = LED_PIN
        self.hostname = socket.gethostname()

        # Notify owner on startup
        self.send_message_to_owner(f"> {self.hostname} is online <")

        # Build telegram application
        self.app = ApplicationBuilder().token(self.token).build()

        # Register handlers
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("super", self.superuser))
        self.app.add_handler(CommandHandler("photo", self.send_photo))
        self.app.add_handler(CommandHandler("led", self.led))
        self.app.add_handler(CommandHandler("run", self.run_script))

        # Text messages are forwarded to a running subprocess (if any)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_process_input)
        )

        # Periodically report top processes
        if self.app.job_queue:
            self.app.job_queue.run_repeating(
                self.process_report, interval=3600, first=0
            )
        else:  # pragma: no cover - requires job-queue extra
            print("JobQueue not available; periodic process report disabled")

    def run(self) -> None:
        """Start polling and notify when stopping."""
        try:
            self.app.run_polling()
        finally:
            self.send_message_to_owner(
                f"> {self.hostname} notifier disabled <"
            )

    send_message_to_owner = send_message_to_owner
    _cpu_temp = _cpu_temp
    status = status
    send_photo = send_photo
    led = led
    run_script = run_script
    _forward_output = _forward_output
    handle_process_input = handle_process_input
    superuser = superuser
    process_report = process_report


if __name__ == "__main__":
    load_dotenv(dotenv_path=".env")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    application = App(BOT_TOKEN, CHAT_ID)
    application.run()
