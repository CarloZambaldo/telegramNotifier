import os
from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


@restricted
async def superuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reboot/poweroff commands."""

    if not context.args:
        await update.message.reply_text("Usage: /super <reboot|poweroff> yes")
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
