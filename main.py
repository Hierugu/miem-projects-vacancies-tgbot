import os
import api
import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

# Messages
def escape_markdown_v2(text):
    if not isinstance(text, str):
        return text
    escape_chars = r'_*[]()~`>#+-=|{}.!' # List of all special characters in MarkdownV2 that must be escaped
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def new_vacancy_message(vacancy):
    values = {
        "id": vacancy.get('id', 'ERR'),
        "role": vacancy.get('role', 'ERR'),
        "description": vacancy.get('description', 'ERR').strip(),
        "manager": vacancy.get('managerName', 'ERR'),
        "requiredSkills": '\n'.join(["• " + s for s in vacancy.get('requiredSkills', ['ERR'])]),
        "developedSkills": '\n'.join(["• " + s for s in vacancy.get('developedSkills', ['ERR'])]),
        "project": vacancy.get('projectName', 'ERR'),
        "pid": vacancy.get('projectId', 'ERR'),
    }

    if values["role"] and isinstance(values["role"], str) and values["role"][0].isalpha():
        values["role"] = values["role"][0].upper() + values["role"][1:]

    for k in values:
        values[k] = escape_markdown_v2(values[k])

    template_path = os.path.join(os.path.dirname(__file__), "templates", "newVacancyMessage.md")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    return template.format(**values)

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот вакансий проектов МИЭМ. Ты можешь подписаться на обновления и я буду сообщать тебе о новых вакансиях!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/subscribe - Подписаться на обновления\n"
        "/unsubscribe - Отписаться от обновлений"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"Received message from {user.id} ({user.username}): {update.message.text}")
    # await update.message.reply_text(update.message.text)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Save the user_id to users.txt file
    with open("users.txt", "a") as f:
        f.write(f"{user_id}\n")
    logger.warning(f"User {user_id} subscribed.")
    await update.message.reply_text("Вы подписались на обновления о новых вакансиях!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        with open("users.txt", "r") as f:
            users = f.readlines()
        users = [u.strip() for u in users if u.strip()]
        if str(user_id) not in users:
            await update.message.reply_text("Вы не были подписаны.")
        else:
            users = [u for u in users if u != str(user_id)]
            with open("users.txt", "w") as f:
                for u in users:
                    f.write(f"{u}\n")
        logger.warning(f"User {user_id} unsubscribed.")
        await update.message.reply_text("Вы отписались от обновлений о вакансиях.")
    except FileNotFoundError:
        await update.message.reply_text("Внутренняя ошибка: база пользователей не найдена.")

async def notify_new_vacancies_task(context):
    try:
        # Fetch all vacancies
        json_data = api.call_get_vacancies_api(offset=0, limit=10000)
        vacancies = json_data.get("vacancies", [])
        logger.warning(f"Total number of received vacancies: {len(vacancies)}")
        logger.warning(f"Total number of vacancies from API: {json_data.get('count', 'unknown')}")

        # Read known IDs
        try:
            with open("vacancy_ids.txt", "r", encoding="utf-8") as f:
                known_ids = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            known_ids = set()

        # Find new vacancies
        new_vacancies = [v for v in vacancies if str(v.get("id")) not in known_ids]
        if new_vacancies:
            # Read all user IDs
            try:
                with open("users.txt", "r", encoding="utf-8") as f:
                    user_ids = [int(line.strip()) for line in f if line.strip()]
            except FileNotFoundError:
                user_ids = []
            # Prepare message for each new vacancy (customize as needed)
            for vacancy in new_vacancies:
                msg = f"New vacancy: {vacancy.get('role', 'No title')}\nID: {vacancy.get('id')}"
                for uid in user_ids:
                    try:
                        await context.bot.send_message(chat_id=uid, text=new_vacancy_message(vacancy), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
                    except Exception as e:
                        logger.warning(f"Failed to send to {uid}: {e}")
            # Update known IDs file
            with open("vacancy_ids.txt", "a", encoding="utf-8") as f:
                for v in new_vacancies:
                    vid = v.get("id")
                    if vid is not None:
                        f.write(str(vid) + "\n")
            logger.warning(f"Sent {len(new_vacancies)} new vacancies to {len(user_ids)} users.")
        else:
            logger.warning("No new vacancies found.")
    except Exception as e:
        logger.error(f"Error in notify_new_vacancies_task: {e}")

def main():

    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.warning("Bot started...")
    # Schedule the job to run every hour using JobQueue
    app.job_queue.run_repeating(notify_new_vacancies_task, interval=3600, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()