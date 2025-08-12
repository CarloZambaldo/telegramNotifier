import cv2
from telegram import Update
from telegram.ext import ContextTypes

from .restricted import restricted


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
