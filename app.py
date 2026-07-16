from fastapi import FastAPI, Request
import os
import requests
import json
from datetime import datetime

from sqlalchemy import text

from database import engine, SessionLocal
from models import Base, Receipt, ReceiptItem
from telegram_bot import handle_command


app = FastAPI()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ==========================
# СОЗДАНИЕ ТАБЛИЦ
# ==========================

Base.metadata.create_all(bind=engine)


# ==========================
# ОБНОВЛЕНИЕ СТАРОЙ БАЗЫ
# ==========================

def update_database():

    commands = [

        """
        ALTER TABLE receipts
        ADD COLUMN IF NOT EXISTS store_id TEXT;
        """,

        """
        ALTER TABLE receipts
        ADD COLUMN IF NOT EXISTS device_id TEXT;
        """,

        """
        ALTER TABLE receipts
        ADD COLUMN IF NOT EXISTS employee_id TEXT;
        """,

        """
        ALTER TABLE receipts
        ADD COLUMN IF NOT EXISTS shift_id TEXT;
        """,

        """
        ALTER TABLE items
        ADD COLUMN IF NOT EXISTS quantity DOUBLE PRECISION DEFAULT 1;
        """
    ]


    with engine.connect() as conn:

        for command in commands:

            try:
                conn.execute(text(command))
                conn.commit()

                print("DATABASE UPDATE OK")

            except Exception as e:

                print(
                    "DATABASE UPDATE ERROR:",
                    e
                )


update_database()



# ==========================
# TELEGRAM
# ==========================

def send_message(text_message):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        return


    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )


    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text_message
        }
    )


    print(
        "Telegram:",
        response.status_code,
        response.text
    )



# ==========================
# ОПЛАТА
# ==========================

def payment_name(payment):

    return {

        "PAY_CASH":
            "💵 Наличные",

        "PAY_CARD":
            "💳 Карта",

        "PAY_QR":
            "📱 СБП"

    }.get(
        payment,
        payment
    )



# ==========================
# ФОРМАТ ЧЕКА
# ==========================

def format_receipt(data):

    receipt = data["data"]


    text_message = (

        "☕ На Волне\n\n"

        "🧾 Новый чек\n\n"

        f"💰 Сумма: "
        f"{receipt.get('totalAmount')} ₽\n"

        f"{payment_name(receipt.get('paymentSource'))}\n\n"

        "🥤 Товары:\n"
    )


    for item in receipt.get(
        "items",
        []
    ):

        text_message += (

            f"• {item.get('name')} — "

            f"{item.get('sumPrice',0)} ₽ "

            f"x {item.get('quantity',1)}\n"

        )


    date_time = receipt.get(
        "dateTime",
        ""
    )


    text_message += (

        f"\n🕒 "
        f"{date_time[11:16]}"
    )


    return text_message



# ==========================
# СОХРАНЕНИЕ В БАЗУ
# ==========================

def save_to_database(data):

    receipt = data["data"]

    db = SessionLocal()


    try:

        new_receipt = Receipt(

            receipt_id=
                receipt.get("id"),

            store_id=
                receipt.get("storeId"),

            device_id=
                receipt.get("deviceId"),

            employee_id=
                receipt.get("employeeId"),

            shift_id=
                receipt.get("shiftId"),


            payment=
                receipt.get("paymentSource"),


            amount=
                receipt.get(
                    "totalAmount",
                    0
                ),


            date=
                datetime.fromisoformat(

                    receipt["dateTime"]
                    .replace(
                        "Z",
                        "+00:00"
                    )

                )

        )


        db.add(new_receipt)



        for item in receipt.get(
            "items",
            []
        ):


            new_item = ReceiptItem(

                receipt_id=
                    receipt.get("id"),


                name=
                    item.get("name"),


                price=
                    item.get(
                        "sumPrice",
                        item.get(
                            "price",
                            0
                        )
                    ),


                quantity=
                    item.get(
                        "quantity",
                        1
                    )

            )


            db.add(new_item)



        db.commit()


        print(
            "SAVED TO POSTGRES"
        )


    except Exception as e:


        print(
            "DATABASE ERROR:",
            e
        )

        db.rollback()



    finally:

        db.close()



# ==========================
# HOME
# ==========================

@app.get("/")
def home():

    return {

        "status":
            "WaveOS is running"

    }



# ==========================
# ЭВОТОР
# ==========================

@app.post("/webhook")
@app.put("/webhook")
async def evotor_webhook(
    request: Request
):


    body = await request.body()


    if not body:

        return {
            "ok": True
        }


    data = json.loads(body)



    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )



    if data.get(
        "type"
    ) == "ReceiptCreated":


        save_to_database(
            data
        )


        send_message(
            format_receipt(data)
        )



    return {
        "ok": True
    }



# ==========================
# TELEGRAM
# ==========================

@app.post("/telegram")
async def telegram_webhook(
    request: Request
):


    data = await request.json()



    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )



    if data.get(
        "message"
    ):


        handle_command(
            data["message"]
        )



    return {
        "ok": True
    }
