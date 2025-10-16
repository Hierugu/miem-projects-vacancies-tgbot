from telegram.ext import ContextTypes
from telegram import Update
from logger import logger
import api
import messages
import random as rand

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /start")
    await update.message.reply_text("Привет! Я бот вакансий проектов МИЭМ. Ты можешь подписаться на обновления и я буду сообщать тебе о новых вакансиях!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /help")
    with open("messageTemplates/helpMessage.md", "r", encoding="utf-8") as f:
        help_text = f.read()
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) sent message: {update.message.text}")
    # await update.message.reply_text(update.message.text)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /subscribe")
    try:
        with open("users.txt", "r") as f:
            users = [u.strip() for u in f.readlines() if u.strip()]
    except FileNotFoundError:
        users = []

    if str(user.id) in users:
        await update.message.reply_text("Вы уже подписаны на обновления.")
        logger.warning(f"User {user.username} ({user.id}) tried to subscribe again.")
    else:
        with open("users.txt", "a") as f:
            f.write(f"{user.id}\n")
        logger.warning(f"User {user.username} ({user.id}) subscribed.")
        await update.message.reply_text("Вы подписались на обновления о новых вакансиях!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /unsubscribe")
    try:
        with open("users.txt", "r") as f:
            users = f.readlines()
        users = [u.strip() for u in users if u.strip()]
        if str(user.id) not in users:
            await update.message.reply_text("Вы не были подписаны.")
        else:
            users = [u for u in users if u != str(user.id)]
            with open("users.txt", "w") as f:
                for u in users:
                    f.write(f"{u}\n")
        logger.warning(f"User {user.username} ({user.id}) unsubscribed.")
        await update.message.reply_text("Вы отписались от обновлений о вакансиях.")
    except FileNotFoundError:
        await update.message.reply_text("Внутренняя ошибка: база пользователей не найдена.")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /statistics")

    json_data = api.call_get_vacancies_api(offset=0, limit=10000)

    msg = messages.new_statistics_message(json_data)
    await update.message.reply_text(msg)

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /random")

    json_data = api.call_get_vacancies_api(offset=0, limit=10000)
    vacancies = json_data.get("vacancies", [])
    if not vacancies:
        await update.message.reply_text("Нет доступных вакансий.")
        return

    vacancy = rand.choice(vacancies)
    msg = messages.new_vacancy_message(vacancy)
    await update.message.reply_text(msg, parse_mode="MarkdownV2", disable_web_page_preview=True)

async def filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /filter")
    await update.message.reply_text("Функция фильтрации пока не реализована.")
