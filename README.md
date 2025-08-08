# 📡 Raspberry Pi Telegram Bot

This project provides a simple Telegram bot that allows remote management of your Raspberry Pi via Telegram messages.

## 🚀 Features

Once deployed, the bot lets you:

- `/status` – View uptime, disk usage and CPU temperature.
- `/photo` – Capture a live photo from an attached USB camera.
- `/led on|off` – Toggle a GPIO pin (e.g. an LED).
- `/run <command>` – Start a shell command and interact with it via chat.
- `/super reboot yes` – Remotely reboot the Raspberry Pi.
- `/super poweroff yes` – Remotely power off the Raspberry Pi.
- Automatic hourly updates of the top running processes are sent to the owner.

> ❗️ Only one authorized user (defined in `.env`) can use the bot. Unauthorized users will be notified with a rejection message.

---

## 🧰 Requirements

- Python 3.7+
- Telegram account with a bot token
- A Raspberry Pi (or Linux machine)
- The Python packages listed in `requirements.txt` (includes job-queue extras):

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

The `/photo` command uses the first available USB camera to capture an image in
real time.

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
├── .env               # Environment variables (not committed)
├── main.py            # The main bot script
└── requirements.txt   # Python dependencies
```

---

## 🛠️ Future Improvements

- Implement the `/start` and `/help` command handlers.
- Expand sensor integration and additional GPIO controls.
- Improve process monitoring and logging.
- And much more!

---

## 🧑‍💻 License

MIT License – use at your own risk.

