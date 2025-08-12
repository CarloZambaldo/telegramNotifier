import os
from telegram.ext import ContextTypes


async def process_report(self, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send periodic updates of the top running processes."""

    procs = os.popen(
        "ps -eo pid,comm,pcpu --sort=-pcpu | head -n 5"
    ).read()
    await context.bot.send_message(
        chat_id=self.chat_id, text=f"# TOP PROCESSES #\n{procs}"
    )
