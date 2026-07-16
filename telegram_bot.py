import requests
import os
from analytics import today_stats, top_products

TOKEN = os.getenv("TELEGRAM_TOKEN")


def send_command_answer(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text
        }
    )


def handle_command(message):

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/today":

        stats = today_stats()

        answer = (
            "☕ На Волне\n\n"
            "📅 Сегодня\n\n"
            f"💰 Выручка: {stats['total']} ₽\n"
            f"🧾 Чеков: {stats['checks']}\n"
            f"📊 Средний чек: {stats['average']} ₽"
        )

        send_command_answer(chat_id, answer)


    elif text == "/top":

        products = top_products()

        answer = (
            "🥤 Топ продаж\n\n"
        )

        for i, item in enumerate(products, 1):
            answer += f"{i}. {item[0]} — {item[1]} шт.\n"

        send_command_answer(chat_id, answer)
