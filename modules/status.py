import os
import shutil
from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


@restricted
async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Report basic system statistics."""

    uptime = os.popen("uptime -p").read().strip()
    total, used, _ = shutil.disk_usage("/")
    disk = f"{used // (2 ** 30)}/{total // (2 ** 30)} GB"
    message = (
        "# RASPI STATUS #\n\nOnline\n"
        f"Uptime:\t{uptime}\n"
        f"Disk:\t{disk}\n"
        f"CPU Temp:\t{self._cpu_temp()}"
    )
    await update.message.reply_text(message)
