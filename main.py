from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

from handlers import start, help_command, echo, subscribe, unsubscribe, statistics
from jobs import notify_new_vacancies_task
from logger import logger

def main():

    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("statistics", statistics))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.warning("Bot started...")
    app.job_queue.run_repeating(notify_new_vacancies_task, interval=3600, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()