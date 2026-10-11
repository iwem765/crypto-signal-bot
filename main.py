import time
import requests
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8827909892:AAGggK3SNqVxF82THp-hPTc8ePmgwC9kcnw"
USERS_FILE = "users.txt"
THRESHOLD_PERCENT = 0.1  # Сигнал при изменении цены на 0.1%

# Твоя реферальная ссылка (замени на свою партнёрскую ссылку от Binance/Bybit для заработка!)
REF_LINK = "https://accounts.binance.com/register?ref=YOUR_REF_ID"

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"
]

last_prices = {}

def get_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def add_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def send_telegram_message(user_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": user_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Ошибка отправки пользователю {user_id}: {e}")

def get_main_keyboard():
    # Красивые инлайн-кнопки для пользователей
    return {
        "inline_keyboard": [
            [{"text": "📊 Список монет", "callback_data": "coins"}],
            [{"text": "💎 VIP-Подписка", "callback_data": "vip"}],
            [{"text": "📈 Торговать на бирже", "url": REF_LINK}]
        ]
    }

def process_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 5, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=10).json()
        if "result" in response:
            for update in response["result"]:
                offset = update["update_id"] + 1
                
                # Обработка текстовых сообщений (/start)
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    
                    if text == "/start":
                        add_user(chat_id)
                        welcome_text = (
                            "👋 <b>Добро пожаловать в Crypto Signal Bot!</b>\n\n"
                            "🚀 Я отслеживаю изменение цен топ-10 криптовалют в реальном времени.\n"
                            "Выбери нужный пункт в меню ниже:"
                        )
                        send_telegram_message(chat_id, welcome_text, get_main_keyboard())

                # Обработка нажатий на инлайн-кнопки
                elif "callback_query" in update:
                    callback = update["callback_query"]
                    chat_id = callback["message"]["chat"]["id"]
                    data = callback["data"]
                    
                    if data == "coins":
                        coins_text = "📌 <b>Отслеживаемые монеты:</b>\n" + ", ".join(SYMBOLS)
                        send_telegram_message(chat_id, coins_text, get_main_keyboard())
                    elif data == "vip":
                        vip_text = (
                            "💎 <b>VIP-Доступ к сигналам</b>\n\n"
                            "Получай мгновенные уведомления без задержек и доступ к эксклюзивным альткоинам!\n"
                            "💳 Стоимость: <b>$9.99 / месяц</b>\n\n"
                            "<i>Для подключения пиши администратору: @твои_контакты</i>"
                        )
                        send_telegram_message(chat_id, vip_text, get_main_keyboard())
                        
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
    return offset

def check_prices():
    global last_prices
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, timeout=5).json()
        current_prices = {item["symbol"]: float(item["price"]) for item in response if item["symbol"] in SYMBOLS}
        
        users = get_users()
        
        for symbol, price in current_prices.items():
            if symbol in last_prices:
                old_price = last_prices[symbol]
                if old_price > 0:
                    change = ((price - old_price) / old_price) * 100
                    
                    if abs(change) >= THRESHOLD_PERCENT:
                        emoji = "🟢 🚀" if change > 0 else "🔴 📉"
                        direction = "Рост" if change > 0 else "Падение"
                        
                        # Сообщение с сигналом + вшитая реферальная ссылка на биржу под каждым сигналом
                        message = (
                            f"{emoji} <b>СИГНАЛ: {symbol}</b>\n\n"
                            f"<b>Движение:</b> {direction} на <b>{change:+.2f}%</b>\n"
                            f"<b>Текущая цена:</b> ${price:,.4f}\n"
                            f"<b>Предыдущая цена:</b> ${old_price:,.4f}\n\n"
                            f"👉 <a href='{REF_LINK}'>Открыть сделку на бирже</a>"
                        )
                        for user_id in users:
                            send_telegram_message(user_id, message)
            
            last_prices[symbol] = price
    except Exception as e:
        print(f"Ошибка проверки цен: {e}")

def main():
    print("Бот успешно запущен!")
    update_offset = None
    while True:
        update_offset = process_updates(update_offset)
        check_prices()
        time.sleep(3)

if __name__ == "__main__":
    main()
