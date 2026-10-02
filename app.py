import os
import json
import time
import threading
import requests

from flask import Flask, request

app = Flask(__name__)

TOKEN_ADDRESS = "0x2b9018CeB303D540BbF08De8e7De64fDDD63396C"
CHAIN = "celo"
CHECK_INTERVAL_SECONDS = 60
USERS_FILE = "subscribers.json"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")


def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=10
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Telegram error for {chat_id}: {error}")


def get_token_price():
    url = f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        pairs = data.get("pairs", [])

        for pair in pairs:
            if pair.get("chainId") == CHAIN:
                price = pair.get("priceUsd")

                if price:
                    return float(price)

    except (requests.RequestException, ValueError, KeyError) as error:
        print(f"Price fetch error: {error}")

    return None


@app.route(f"/bot{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return "OK"

    message = data["message"]

    chat_id = str(message["chat"]["id"])
    text = message.get("text", "").strip()

    users = load_users()

    if text == "/start":
        if chat_id not in users:
            users.append(chat_id)
            save_users(users)

        send_telegram_message(
            chat_id,
            "✅ You are subscribed to token price updates."
        )

    elif text == "/stop":
        if chat_id in users:
            users.remove(chat_id)
            save_users(users)

        send_telegram_message(
            chat_id,
            "🛑 You are unsubscribed from price updates."
        )

    elif text == "/price":
        price = get_token_price()

        if price is not None:
            send_telegram_message(
                chat_id,
                f"Current token price: ${price:.8f}"
            )
        else:
            send_telegram_message(
                chat_id,
                "Could not fetch the token price."
            )

    else:
        send_telegram_message(
            chat_id,
            "Commands:\n"
            "/start - subscribe\n"
            "/stop - unsubscribe\n"
            "/price - current price"
        )

    return "OK"


def price_monitor():
    while True:
        price = get_token_price()

        if price is not None:
            message = f"Token price: ${price:.8f}"

            print(message)

            users = load_users()

            for user in users:
                send_telegram_message(user, message)

        else:
            print("Price unavailable.")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    threading.Thread(
        target=price_monitor,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000))
    )
