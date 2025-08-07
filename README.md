# 📡 Raspberry Pi Telegram Bot

This project provides a simple Telegram bot that allows remote management of your Raspberry Pi via Telegram messages.

## 🚀 Features

Once deployed, the bot lets you:

- `/start` – Receive a welcome message (not implemented yet).
- `/status` – View the system's uptime.
- `/photo` – Get a test photo from the Raspberry Pi.
- `/super reboot yes` – Remotely reboot the Raspberry Pi.
- `/super poweroff yes` – Remotely power off the Raspberry Pi.
- `/help` – Display a help message (not implemented yet).

> ❗️ Only one authorized user (defined in `.env`) can use the bot. Unauthorized users will be notified with a rejection message.

---

## 🧰 Requirements

- Python 3.7+
- Telegram account with a bot token
- A Raspberry Pi (or Linux machine)
 - The Python packages listed in `requirements.txt`:

 ```bash
 pip install -r requirements.txt
 ```

---

## 🔐 .env File Setup

Before running the bot, create a `.env` file in the root directory of your project with the following contents:

```ini
BOT_TOKEN=your_telegram_bot_token_here
CHAT_ID=your_telegram_user_id_here
```

- `BOT_TOKEN`: Get it from [@BotFather](https://t.me/BotFather) on Telegram.
- `CHAT_ID`: Your numeric Telegram user ID.
  - To find it, temporarily print it using:
    ```python
    print(update.effective_user.id)
    ```
  - Or hardcode a reply in a handler to inspect the `update` object.

---

## 📸 Photo Feature

Make sure you have a test image saved at the following path:

```
./img/test.png
```

This image will be sent in response to the `/photo` command.

---

## 🔧 Usage

1. Clone the repository and navigate to the project folder.
 2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create your `.env` file as shown above.
4. Run the bot:
   ```bash
   python3 your_bot_script.py
   ```
5. Send commands to your bot on Telegram.

---

## ⚠️ Security Notes

- This bot only accepts commands from a single authorized user (`CHAT_ID`).
- Superuser commands like `/super reboot yes` and `/super poweroff yes` directly affect the system – use with caution.
- Do **not** expose your `.env` file or share your bot token.

---

## 📁 File Structure

```
├── img/
│   └── test.png          # Image used by the /photo command
├── .env                  # Environment variables (not committed)
└── your_bot_script.py    # The main bot script
```

---

## 🛠️ Future Improvements

- Implement the `/start` and `/help` command handlers.
- Replace static image with live camera capture.
- Add more system commands (e.g., disk space, CPU temp).
- Integrate GPIO or sensor controls.
- Add automatic updates on running processes.
- and much more!

---

## 🧑‍💻 License

MIT License – use at your own risk.

