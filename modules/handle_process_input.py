from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


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
