from fastapi import FastAPI, Request
import os
import requests
import json
from datetime import datetime

from database import engine, SessionLocal
from models import Base, Receipt, ReceiptItem
from telegram_bot import handle_command


app = FastAPI()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# создаём таблицы
Base.metadata.create_all(bind=engine)


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
        f"💰 Сумма: {receipt.get('totalAmount')} ₽\n"
        f"{payment_name(receipt.get('paymentSource'))}\n\n"
        "🥤 Товары:\n"
    )

    for item in receipt.get("items", []):
        text += (
            f"• {item.get('name')} — "
            f"{item.get('sumPrice', item.get('price'))} ₽\n"
        )

    text += (
        f"\n🕒 {receipt.get('dateTime','')[11:16]}"
    )

    return text


def save_to_database(data):

    receipt = data["data"]

    db = SessionLocal()

    try:

        new_receipt = Receipt(
            receipt_id=receipt.get("id"),
            date=datetime.fromisoformat(
                receipt["dateTime"].replace("Z", "+00:00")
            ),
            payment=receipt.get("paymentSource"),
            amount=receipt.get("totalAmount", 0)
        )

        db.add(new_receipt)

        for item in receipt.get("items", []):

            new_item = ReceiptItem(
                receipt_id=receipt.get("id"),
                name=item.get("name"),
                price=item.get(
                    "sumPrice",
                    item.get("price", 0)
                )
            )

            db.add(new_item)

        db.commit()

        print("SAVED TO POSTGRES")

    except Exception as e:

        print("DATABASE ERROR:", e)
        db.rollback()

    finally:
        db.close()



@app.get("/")
def home():
    return {
        "status": "WaveOS is running"
    }



# Эвотор

@app.post("/webhook")
@app.put("/webhook")
async def evotor_webhook(request: Request):

    body = await request.body()

    if not body:
        return {"ok": True}


    data = json.loads(body)


    print("EVOTOR DOCUMENT:")
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )


    if data.get("type") == "ReceiptCreated":

        save_to_database(data)

        message = format_receipt(data)

        send_message(message)


    return {"ok": True}




# Telegram

@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()


    print("TELEGRAM UPDATE:")
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )


    if data.get("message"):

        handle_command(
            data["message"]
        )


    return {"ok": True}
