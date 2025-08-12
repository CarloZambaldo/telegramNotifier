import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


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
