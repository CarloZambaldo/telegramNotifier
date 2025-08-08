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
import shutil
import time
from functools import wraps

import cv2
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
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


class App:
    """Main application class for the Telegram bot."""

    def __init__(self, token: str, chat_id: str) -> None:
        self.chat_id = chat_id
        self.token = token
        self.start_time = time.time()
        self.bot_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.active_process: asyncio.subprocess.Process | None = None

        # Notify owner on startup
        self.send_message_to_owner("> raspi is online <")

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
        """Start polling."""
        self.app.run_polling()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def restricted(func):  # type: ignore[misc]
        """Decorator to restrict commands to the authorised user."""

        @wraps(func)
        async def wrapped(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = str(update.effective_user.id)
            allowed_id = str(self.chat_id)
            if user_id != allowed_id:
                user_tag = str(update) or "<unknown>"
                self.send_message_to_owner(f"UNAUTHORISED QUERY: {user_tag}")
                await update.message.reply_text("❌ UNAUTHORIZED USER ❌")
                return
            return await func(self, update, context, *args, **kwargs)

        return wrapped

    def send_message_to_owner(self, message: str) -> None:
        """Send a plain text message to the authorised user."""

        data = {"chat_id": self.chat_id, "text": message}
        try:
            response = requests.post(self.bot_url, data=data)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network failure
            print(f"Errore nell'invio: {exc}")

    def _cpu_temp(self) -> str:
        """Return the CPU temperature if available."""

        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as fh:
                return f"{int(fh.read()) / 1000:.1f}°C"
        except Exception:
            temp = os.popen("vcgencmd measure_temp").read().strip()
            return temp.replace("temp=", "") if temp else "N/A"

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------
    @restricted
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Report basic system statistics."""

        uptime = os.popen("uptime -p").read().strip()
        total, used, _ = shutil.disk_usage("/")
        disk = f"{used // (2 ** 30)}/{total // (2 ** 30)} GB"
        message = (
            f"# RASPI STATUS #\n\nOnline\n"
            f"Uptime:\t{uptime}\n"
            f"Disk:\t{disk}\n"
            f"CPU Temp:\t{self._cpu_temp()}"
        )
        await update.message.reply_text(message)

    @restricted
    async def send_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Capture a photo from the USB camera and send it."""

        try:  # pragma: no cover - requires camera hardware
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                raise RuntimeError("Cannot read from camera")
            _, buffer = cv2.imencode(".jpg", frame)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=buffer.tobytes()
            )
        except Exception as exc:
            await update.message.reply_text(f"Errore invio immagine: {exc}")

    @restricted
    async def led(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Toggle an LED connected to a GPIO pin."""

        if GPIO is None:
            await update.message.reply_text("GPIO not available")
            return
        if not context.args:
            await update.message.reply_text("Usage: /led <on|off>")
            return
        state = context.args[0].lower()
        if state == "on":
            GPIO.output(LED_PIN, True)
            await update.message.reply_text("LED on")
        elif state == "off":
            GPIO.output(LED_PIN, False)
            await update.message.reply_text("LED off")
        else:
            await update.message.reply_text("Usage: /led <on|off>")

    @restricted
    async def run_script(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start an external script and allow interaction via chat."""

        if self.active_process is not None:
            await update.message.reply_text("A process is already running")
            return

        if not context.args:
            await update.message.reply_text("Usage: /run <command>")
            return

        command = " ".join(context.args)
        self.active_process = await asyncio.create_subprocess_shell(
            command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        await update.message.reply_text(
            f"Started `{command}`. Send messages to interact.", parse_mode="Markdown"
        )
        asyncio.create_task(self._forward_output(update.effective_chat.id))

    async def _forward_output(self, chat_id: int) -> None:
        """Forward subprocess output back to the chat."""

        assert self.active_process is not None
        proc = self.active_process
        while proc and not proc.stdout.at_eof():
            line = await proc.stdout.readline()
            if line:
                await self.app.bot.send_message(chat_id, line.decode().rstrip())
        if proc:
            code = await proc.wait()
            await self.app.bot.send_message(
                chat_id, f"Process finished with code {code}"
            )
        self.active_process = None

    @restricted
    async def handle_process_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Forward user messages to the running subprocess."""

        if self.active_process is None:
            await update.message.reply_text("No active process")
            return

        self.active_process.stdin.write((update.message.text + "\n").encode())
        await self.active_process.stdin.drain()

    @restricted
    async def superuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle reboot/poweroff commands."""

        if not context.args:
            await update.message.reply_text(
                "Usage: /super <reboot|poweroff> yes"
            )
            return

        action = context.args[0].lower()
        if action == "reboot":
            if len(context.args) < 2 or context.args[1].lower() != "yes":
                await update.message.reply_text(
                    "⚠️ Confirm with: `/super reboot yes`",
                    parse_mode="Markdown",
                )
                return
            await update.message.reply_text("Rebooting the system...")
            os.system("sudo reboot")

        elif action == "poweroff":
            if len(context.args) < 2 or context.args[1].lower() != "yes":
                await update.message.reply_text(
                    "⚠️ Confirm with: `/super poweroff yes`",
                    parse_mode="Markdown",
                )
                return
            await update.message.reply_text("Shutting down...")
            os.system("sudo poweroff")

    async def process_report(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send periodic updates of the top running processes."""

        procs = os.popen(
            "ps -eo pid,comm,pcpu --sort=-pcpu | head -n 5"
        ).read()
        await context.bot.send_message(
            chat_id=self.chat_id, text=f"# TOP PROCESSES #\n{procs}"
        )


if __name__ == "__main__":
    load_dotenv(dotenv_path=".env")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    application = App(BOT_TOKEN, CHAT_ID)
    application.run()

