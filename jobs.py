from telegram.constants import ParseMode
from messages import new_vacancy_message
from logger import logger
import api
import db


async def notify_new_vacancies_task(context):
    try:
        json_data = api.call_get_vacancies_api(offset=0, limit=10000)
        vacancies = json_data.get("vacancies", [])
        logger.warning(f"Total number of received vacancies: {len(vacancies)}")
        logger.warning(f"Total number of vacancies from API: {json_data.get('count', 'unknown')}")

        # Read known vacancy ids from DB
        known_ids = db.get_known_vacancy_ids()

        new_vacancies = [v for v in vacancies if str(v.get("id")) not in known_ids]
        if new_vacancies:
            # Get subscribed users from DB
            user_ids = db.list_users()
            for vacancy in new_vacancies:
                for uid in user_ids:
                    try:
                        await context.bot.send_message(chat_id=uid, text=new_vacancy_message(vacancy), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
                    except Exception as e:
                        logger.warning(f"Failed to send {vacancy.get('id')} to {uid}: {e}")
            # Persist new vacancy ids to DB
            db.add_vacancy_ids([v.get('id') for v in new_vacancies if v.get('id') is not None])
            logger.warning(f"Sent {len(new_vacancies)} new vacancies to {len(user_ids)} users.")
        else:
            logger.warning("No new vacancies found.")
    except Exception as e:
        logger.error(f"Error in notify_new_vacancies_task: {e}")