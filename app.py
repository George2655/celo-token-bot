import requests
import time
import json
from flask import Flask, request
import threading

app = Flask(__name__)

TOKEN_ADDRESS = "0x2b9018CeB303D540BbF08De8e7De64fDDD63396C"
CHAIN = "celo"
CHECK_INTERVAL_SECONDS = 60
TELEGRAM_BOT_TOKEN = "7229916149:AAGoE-Cj5-Xe8zv5GTLVnsS7uWiwqf8dZTQ"

USERS_FILE = "subscribers.json"

# Завантажити список користувачів
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Зберегти список користувачів
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# Надіслати повідомлення одному користувачу
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Помилка надсилання {chat_id}:", e)

# Отримати ціну токена
def get_token_price():
    url = f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])
        for pair in pairs:
            if pair.get("chainId") == CHAIN:
                return float(pair["priceUsd"])
    except Exception as e:
        print("Помилка при отриманні ціни:", e)
    return None

# Webhook від Telegram
@app.route(f"/bot{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        users = load_users()
        if chat_id not in users:
            users.append(chat_id)
            save_users(users)
            send_telegram_message(chat_id, "✅ Хто красавчик?")
        else:
            send_telegram_message(chat_id, "🔁 Ти красавчик")
    return "OK"

# Фоновий цикл
def price_monitor():
    while True:
        price = get_token_price()
        if price:
            message = f"${price:.8f} Pact"
            print(message)
            users = load_users()
            for user in users:
                send_telegram_message(user, message)
        else:
            print("Ціну не отримано.")
        time.sleep(CHECK_INTERVAL_SECONDS)

# Запуск сервера
def run_flask():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=price_monitor, daemon=True).start()
app.run(host="0.0.0.0", port=10000)

"Add app.py"
