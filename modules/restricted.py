from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes


def restricted(func):
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
