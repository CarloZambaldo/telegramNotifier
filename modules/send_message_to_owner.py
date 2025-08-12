import requests


def send_message_to_owner(self, message: str) -> None:
    """Send a plain text message to the authorised user."""

    data = {"chat_id": self.chat_id, "text": message}
    try:
        response = requests.post(self.bot_url, data=data)
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - network failure
        print(f"Errore nell'invio: {exc}")
