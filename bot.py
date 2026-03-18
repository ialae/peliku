import os
import subprocess

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))


def is_authorized(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("Ready. Send me a command to run.")


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("Unauthorized.")
        return

    cmd = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        result = subprocess.run(
            cmd,
            shell=True,  # lets you run any Windows command
            capture_output=True,
            text=True,
            timeout=30,  # kill if it hangs
        )
        output = result.stdout or result.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        output = "❌ Command timed out after 30 seconds."
    except Exception as e:
        output = f"❌ Error: {e}"

    # Telegram messages max out at 4096 chars
    if len(output) > 4096:
        output = output[:4090] + "\n..."

    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_command))
    print("Bot running — waiting for commands...")
    app.run_polling()
