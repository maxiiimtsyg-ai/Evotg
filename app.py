from fastapi import FastAPI, Request
import os
import json
import requests
from datetime import datetime

from database import engine, SessionLocal
from models import Base, Receipt, ReceiptItem
from telegram_bot import handle_command


app = FastAPI()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# создание таблиц (существующие не трогаем)
Base.metadata.create_all(bind=engine)



def send_message(text):

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram env missing")
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_TOKEN}/sendMessage"
    )

    try:

        r = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )

        print(
            "Telegram:",
            r.status_code,
            r.text
        )

    except Exception as e:
        print("Telegram error:", e)



def payment_name(payment):

    return {
        "PAY_CASH": "💵 Наличные",
        "PAY_CARD": "💳 Карта",
        "PAY_QR": "📱 СБП"
    }.get(payment, payment or "Не указано")



def format_receipt(data):

    receipt = data.get("data", {})

    text = (
        "☕ На Волне\n\n"
        "🧾 Новый чек\n\n"
        f"💰 Сумма: "
        f"{receipt.get('totalAmount',0)} ₽\n"
        f"{payment_name(receipt.get('paymentSource'))}\n\n"
        "🥤 Товары:\n"
    )


    for item in receipt.get("items", []):

        text += (
            f"• {item.get('name','Товар')} "
            f"— "
            f"{item.get('sumPrice', item.get('price',0))} ₽\n"
        )


    dt = receipt.get("dateTime")

    if dt:
        text += (
            "\n🕒 "
            + dt[11:16]
        )


    return text



def save_to_database(data):

    receipt = data.get("data", {})

    db = SessionLocal()


    try:

        receipt_id = receipt.get("id")


        # защита от дублей
        exists = (
            db.query(Receipt)
            .filter(
                Receipt.receipt_id == receipt_id
            )
            .first()
        )


        if exists:
            print("DUPLICATE RECEIPT")
            return



        new_receipt = Receipt(

            receipt_id=receipt_id,

            store_id=receipt.get(
                "storeId"
            ),

            device_id=receipt.get(
                "deviceId"
            ),

            employee_id=receipt.get(
                "employeeId"
            ),

            shift_id=receipt.get(
                "shiftId"
            ),


            date=datetime.fromisoformat(
                receipt["dateTime"]
                .replace(
                    "Z",
                    "+00:00"
                )
            )
            if receipt.get("dateTime")
            else datetime.utcnow(),


            payment=receipt.get(
                "paymentSource"
            ),


            amount=receipt.get(
                "totalAmount",
                0
            )
        )


        db.add(new_receipt)



        for item in receipt.get(
            "items",
            []
        ):

            db.add(
                ReceiptItem(

                    receipt_id=receipt_id,

                    name=item.get(
                        "name"
                    ),

                    price=item.get(
                        "sumPrice",
                        item.get(
                            "price",
                            0
                        )
                    ),

                    quantity=item.get(
                        "quantity",
                        1
                    )
                )
            )


        db.commit()

        print(
            "DATABASE UPDATE OK"
        )


    except Exception as e:

        print(
            "DATABASE ERROR:",
            e
        )

        db.rollback()


    finally:

        db.close()



@app.get("/")
def home():

    return {
        "status":
        "WaveOS is running"
    }



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


    try:

        data = json.loads(
            body
        )

    except Exception:

        return {
            "ok": True
        }



    print(
        "EVOTOR DOCUMENT:"
    )

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
            format_receipt(
                data
            )
        )



    return {
        "ok": True
    }





@app.post("/telegram")
async def telegram_webhook(
    request: Request
):

    data = await request.json()


    print(
        "TELEGRAM UPDATE:"
    )

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
