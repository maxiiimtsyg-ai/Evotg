from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    if TELEGRAM_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text
        })


@app.get("/")
def home():
    return {"status": "Evotor bot is running"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    send_message(
        "☕ Новый документ от Эвотор:\n\n" +
        str(data)[:1000]
    )

    return {"ok": True}
