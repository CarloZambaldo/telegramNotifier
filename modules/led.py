from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


@restricted
async def led(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle an LED connected to a GPIO pin."""

    if self.GPIO is None:
        await update.message.reply_text("GPIO not available")
        return
    if not context.args:
        await update.message.reply_text("Usage: /led <on|off>")
        return
    state = context.args[0].lower()
    if state == "on":
        self.GPIO.output(self.LED_PIN, True)
        await update.message.reply_text("LED on")
    elif state == "off":
        self.GPIO.output(self.LED_PIN, False)
        await update.message.reply_text("LED off")
    else:
        await update.message.reply_text("Usage: /led <on|off>")
