from fastapi import FastAPI, Request
import os
import requests
import json

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERROR: TELEGRAM_TOKEN or CHAT_ID is missing")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)


@app.get("/")
def home():
    return {"status": "Evotor bot is running"}


@app.post("/webhook")
@app.put("/webhook")
async def webhook(request: Request):

    body = await request.body()

    print("========== NEW WEBHOOK ==========")
    print(body.decode("utf-8"))
    print("================================")

    try:
        data = json.loads(body)
    except:
        data = {"raw": body.decode("utf-8")}

    send_message(
        "☕ Получен документ от Эвотор\n\n"
        + json.dumps(data, ensure_ascii=False, indent=2)[:3500]
    )

    return {"ok": True}
