from telegram.ext import ContextTypes
from telegram import Update
from main import logger

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
    user = update.effective_user
    # Save the user_id to users.txt file
    with open("users.txt", "a") as f:
        f.write(f"{user.id}\n")
    logger.warning(f"User {user.username} ({user.id}) subscribed.")
    await update.message.reply_text("Вы подписались на обновления о новых вакансиях!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
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
    pass