from fastapi import FastAPI, Request
import os
import requests
import json

from database import init_db, save_receipt

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

init_db()


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print("Telegram:", response.status_code, response.text)


def payment_name(payment):
    return {
        "PAY_CASH": "💵 Наличные",
        "PAY_CARD": "💳 Карта",
        "PAY_QR": "📱 СБП"
    }.get(payment, payment)


def format_receipt(data):

    receipt = data["data"]

    text = (
        "☕ На Волне\n\n"
        "🧾 Новый чек\n\n"
        f"💰 Сумма: {receipt['totalAmount']} ₽\n"
        f"{payment_name(receipt['paymentSource'])}\n\n"
        "🥤 Товары:\n"
    )

    for item in receipt["items"]:
        text += (
            f"• {item['name']} — "
            f"{item['sumPrice']} ₽\n"
        )

    text += (
        f"\n🕒 {receipt['dateTime'][11:16]}"
    )

    return text


@app.get("/")
def home():
    return {
        "status": "Evotor bot is running"
    }


@app.post("/webhook")
@app.put("/webhook")
async def webhook(request: Request):

    body = await request.body()

    if not body:
        return {"ok": True}

    data = json.loads(body)

    print("NEW DOCUMENT:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if data.get("type") == "ReceiptCreated":

        save_receipt(data)

        message = format_receipt(data)

        send_message(message)

    return {
        "ok": True
    }
