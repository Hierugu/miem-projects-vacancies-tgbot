from telegram.constants import ParseMode
from messages import new_vacancy_message
from main import logger
import api


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