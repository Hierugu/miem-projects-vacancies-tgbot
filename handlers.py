from telegram.ext import ContextTypes
from telegram import Update
from logger import logger
import api
import messages
import random as rand
import db

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
    # If the user is expected to send a filter, save next message as filter
    if context.user_data.get('expecting_filter'):
        filter_text = update.message.text.strip()
        try:
            db.set_filter(user.id, filter_text)
        except Exception as e:
            logger.warning(f"Failed to save filter for user {user.id}: {e}")
            await update.message.reply_text("Не удалось сохранить фильтр. Попробуйте позже.")
            context.user_data['expecting_filter'] = False
            return

        context.user_data['expecting_filter'] = False
        logger.warning(f"User {user.id} ({user.username}) set filter: {filter_text}")
        await update.message.reply_text("Фильтр сохранён.")
        return

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /subscribe")
    # Add user to DB
    try:
        db.add_user(user.id, user.username)
    except Exception as e:
        logger.warning(f"Failed to add user {user.id}: {e}")
        await update.message.reply_text("Не удалось подписать вас на рассылку. Попробуйте позже.")
        return

    logger.warning(f"User {user.username} ({user.id}) subscribed.")
    await update.message.reply_text("Вы подписались на обновления о новых вакансиях!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.warning(f"User {user.id} ({user.username}) called /unsubscribe")
    try:
        db.remove_user(user.id)
    except Exception as e:
        logger.warning(f"Failed to remove user {user.id}: {e}")
        await update.message.reply_text("Не удалось отписать вас. Попробуйте позже.")
        return

    logger.warning(f"User {user.username} ({user.id}) unsubscribed.")
    await update.message.reply_text("Вы отписались от обновлений о вакансиях.")

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
    try:
        current = db.get_filter(user.id)
    except Exception as e:
        logger.warning(f"Failed to read filter for user {user.id}: {e}")
        current = None

    if current:
        await update.message.reply_text(f"Ваш текущий фильтр: {current}\nОтправьте новый фильтр — следующая строка будет сохранена.")
    else:
        await update.message.reply_text("Отправьте фильтр — следующая строка будет сохранена как ваш фильтр.")

    context.user_data['expecting_filter'] = True
